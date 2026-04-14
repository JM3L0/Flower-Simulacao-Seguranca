"""pytorchexample: A Flower / PyTorch app — Security Experimentation Environment."""

import random

import torch
import torch.nn as nn
import torch.nn.functional as F
from datasets import load_dataset
from flwr_datasets import FederatedDataset
from flwr_datasets.partitioner import DirichletPartitioner
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, ToTensor


class Net(nn.Module):
    """Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')"""

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


fds = None  # Cache FederatedDataset

pytorch_transforms = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


def apply_transforms(batch):
    """Apply transforms to the partition from FederatedDataset."""
    batch["img"] = [pytorch_transforms(img) for img in batch["img"]]
    return batch


def load_data(
    partition_id: int,
    num_partitions: int,
    batch_size: int,
    dirichlet_alpha: float = 1.0,
):
    """Load partition CIFAR10 data with Dirichlet-based heterogeneity.

    Args:
        partition_id: ID of the partition to load.
        num_partitions: Total number of partitions.
        batch_size: Batch size for the DataLoader.
        dirichlet_alpha: Concentration parameter for Dirichlet distribution.
            Lower values = more heterogeneous (non-IID) data.
            Higher values = more homogeneous (closer to IID) data.
    """
    # Only initialize `FederatedDataset` once
    global fds
    if fds is None:
        # =====================================================================
        # PARTICIONAMENTO HETEROGÊNEO (Non-IID via Dirichlet)
        # alpha baixo (ex: 0.1) → dados muito heterogêneos (non-IID extremo)
        # alpha alto  (ex: 100) → dados quase homogêneos (próximo de IID)
        # Controle dinâmico via: flwr run . --run-config "dirichlet_alpha=0.3"
        # =====================================================================
        partitioner = DirichletPartitioner(
            num_partitions=num_partitions,
            partition_by="label",
            alpha=dirichlet_alpha,
            min_partition_size=10,
            seed=42,
        )
        fds = FederatedDataset(
            dataset="uoft-cs/cifar10",
            partitioners={"train": partitioner},
        )
    partition = fds.load_partition(partition_id)
    # Divide data on each node: 80% train, 20% test
    partition_train_test = partition.train_test_split(test_size=0.2, seed=42)
    # Construct dataloaders
    partition_train_test = partition_train_test.with_transform(apply_transforms)
    trainloader = DataLoader(
        partition_train_test["train"], batch_size=batch_size, shuffle=True
    )
    testloader = DataLoader(partition_train_test["test"], batch_size=batch_size)
    return trainloader, testloader


def load_centralized_dataset():
    """Load test set and return dataloader."""
    # Load entire test set
    test_dataset = load_dataset("uoft-cs/cifar10", split="test")
    dataset = test_dataset.with_format("torch").with_transform(apply_transforms)
    return DataLoader(dataset, batch_size=128)


def train(net, trainloader, epochs, lr, device):
    """Train the model on the training set (baseline, sem ataque)."""
    net.to(device)  # move model to GPU if available
    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=0.9)
    net.train()
    running_loss = 0.0
    for _ in range(epochs):
        for batch in trainloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
    avg_trainloss = running_loss / (epochs * len(trainloader))
    return avg_trainloss


def train_with_attack(net, trainloader, epochs, lr, device, poison_rate=0.0):
    """Train the model with optional poisoning attack (label flipping).

    Esta função implementa o treinamento local com um hook estruturado
    para ataques de envenenamento. A lógica de ataque é aplicada por batch,
    manipulando uma fração dos rótulos conforme a taxa de envenenamento.

    Args:
        net: Modelo a ser treinado.
        trainloader: DataLoader com dados de treinamento locais.
        epochs: Número de épocas locais.
        lr: Taxa de aprendizado.
        device: Dispositivo de computação (CPU/GPU).
        poison_rate: Fração dos rótulos a envenenar (0.0 = sem ataque, 1.0 = todos).

    Returns:
        Tuple (avg_train_loss, num_poisoned_samples): perda média e total de
        amostras envenenadas durante o treinamento.
    """
    net.to(device)
    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=0.9)
    net.train()
    running_loss = 0.0
    total_poisoned = 0
    num_classes = 10  # CIFAR-10 possui 10 classes

    for _ in range(epochs):
        for batch in trainloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)

            # =================================================================
            # >>> HOOK DE ATAQUE DE ENVENENAMENTO (Label Flipping) <<<
            #
            # Lógica atual: Para cada amostra no batch, com probabilidade
            # igual a `poison_rate`, o rótulo é invertido para um rótulo
            # aleatório diferente do original.
            #
            # PERSONALIZAÇÕES SUGERIDAS:
            #
            # 1. Label Flipping Direcionado (inspirado em FedDebug):
            #    Trocar rótulos de uma classe específica para outra.
            #    Ex: labels[labels == 3] = 5  (avião → cachorro)
            #
            # 2. Label Flipping Aleatório (implementação atual):
            #    Cada amostra envenenada recebe um rótulo aleatório ≠ original.
            #
            # 3. Corrupção de Features (inspirado em FLANDERS):
            #    Em vez de alterar rótulos, adicionar ruído gaussiano às imagens:
            #    images += torch.randn_like(images) * noise_scale
            #
            # 4. Gradient Manipulation:
            #    Após calcular gradientes, inverter sua direção:
            #    for p in net.parameters(): p.grad.data *= -1
            #
            # Para desativar o ataque, basta setar poison_rate = 0.0
            # =================================================================
            if poison_rate > 0.0:
                batch_size = labels.size(0)
                num_to_poison = int(batch_size * poison_rate)
                if num_to_poison > 0:
                    # Selecionar índices aleatórios para envenenar
                    poison_indices = random.sample(range(batch_size), num_to_poison)
                    for idx in poison_indices:
                        original_label = labels[idx].item()
                        # Gerar rótulo diferente do original
                        new_label = (original_label + random.randint(1, num_classes - 1)) % num_classes
                        labels[idx] = new_label
                    total_poisoned += num_to_poison

            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

    avg_trainloss = running_loss / (epochs * len(trainloader))
    return avg_trainloss, total_poisoned


def test(net, testloader, device):
    """Validate the model on the test set."""
    net.to(device)
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0
    with torch.no_grad():
        for batch in testloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
    accuracy = correct / len(testloader.dataset)
    loss = loss / len(testloader)
    return loss, accuracy

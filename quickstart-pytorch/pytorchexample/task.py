"""pytorchexample: A Flower / PyTorch app — Security Experimentation Environment."""

import random

import torch
import torch.nn as nn
import torch.nn.functional as F
from datasets import load_dataset #type: ignore
from flwr_datasets import FederatedDataset #type: ignore
from flwr_datasets.partitioner import DirichletPartitioner #type: ignore
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, ToTensor #type: ignore


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


def train_with_attack(net, trainloader, epochs, lr, device, poison_rate=0.0, attack_type="label_flipping"):
    """Train the model with optional poisoning attack dynamically selected."""
    
    # === FREE-RIDER ATTACK ===
    if attack_type == "free_rider":
        print("[AVISO] Ataque Free-Rider ativou. Pulando processamento local...")
        return 0.0, 0

    net.to(device)
    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=0.9)
    net.train()
    running_loss = 0.0
    total_poisoned = 0
    
    from pytorchexample.attacks import (
        apply_label_flipping, apply_gaussian_noise, 
        apply_targeted_backdoor, apply_trigger_patch,
        apply_gradient_ascent, apply_model_replacement
    )

    for _ in range(epochs):
        for batch in trainloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)

            if poison_rate > 0.0:
                if attack_type == "label_flipping":
                    labels, num_poisoned = apply_label_flipping(labels, poison_rate)
                    total_poisoned += num_poisoned
                elif attack_type == "gaussian_noise":
                    images, num_poisoned = apply_gaussian_noise(images, poison_rate)
                    total_poisoned += num_poisoned
                elif attack_type == "targeted_backdoor":
                    labels, num_poisoned = apply_targeted_backdoor(labels, poison_rate)
                    total_poisoned += num_poisoned
                elif attack_type == "trigger_patch":
                    images, labels, num_poisoned = apply_trigger_patch(images, labels, poison_rate)
                    total_poisoned += num_poisoned
                # gradient_ascent e model_replacement são lidados abaixo

            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            
            # --- INTERCEPTAÇÃO: Gradient Ascent ---
            if attack_type == "gradient_ascent":
                # Marca as amostras locais como afetadas pelo ataque matemático inteiro
                total_poisoned += labels.size(0)
                loss = apply_gradient_ascent(loss)

            loss.backward()
            optimizer.step()
            
            # Usar valor absoluto no debug para não exibir log negativo que confunde
            running_loss += abs(loss.item())

    # --- INTERCEPTAÇÃO: Model Replacement / Scaling ---
    if attack_type == "model_replacement":
        apply_model_replacement(net)
        # Marca todas do cliente como envenenadas no contexto da substituição global
        total_poisoned = len(trainloader.dataset)

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

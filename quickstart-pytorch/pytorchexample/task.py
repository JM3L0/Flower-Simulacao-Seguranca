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


_current_fds_config = None


def load_data(
    partition_id: int,
    num_partitions: int,
    batch_size: int,
    dirichlet_alpha: float = 1.0,
    seed: int = 42,
):
    """Load partition CIFAR10 data with Dirichlet-based heterogeneity and configurable seed.

    Args:
        partition_id: ID of the partition to load.
        num_partitions: Total number of partitions.
        batch_size: Batch size for the DataLoader.
        dirichlet_alpha: Concentration parameter for Dirichlet distribution.
        seed: Random seed for partitioner and split reproducibility.
    """
    global fds, _current_fds_config
    config_key = (num_partitions, dirichlet_alpha, seed)

    if fds is None or _current_fds_config != config_key:
        partitioner = DirichletPartitioner(
            num_partitions=num_partitions,
            partition_by="label",
            alpha=dirichlet_alpha,
            min_partition_size=10,
            seed=seed,
        )
        fds = FederatedDataset(
            dataset="uoft-cs/cifar10",
            partitioners={"train": partitioner},
        )
        _current_fds_config = config_key

    partition = fds.load_partition(partition_id)
    # Divide data on each node: 80% train, 20% test
    partition_train_test = partition.train_test_split(test_size=0.2, seed=seed)
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


CIFAR10_CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]


def test(
    net,
    testloader,
    device,
    compute_audit: bool = False,
    attack_type: str = "label_flipping",
    source_class: int = 3,
    target_class: int = 5,
    patch_size: int = 4,
):
    """Validate the model on the test set, with optional per-class audit and backdoor metrics."""
    net.to(device)
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0

    # Estruturas para auditoria granular
    num_classes = len(CIFAR10_CLASSES)
    conf_matrix = [[0] * num_classes for _ in range(num_classes)]
    per_class_correct = [0] * num_classes
    per_class_total = [0] * num_classes

    # Métricas de Backdoor ASR
    backdoor_target_count = 0
    backdoor_source_total = 0

    # Para Trigger Patch
    trigger_success = 0
    trigger_total = 0

    with torch.no_grad():
        for batch in testloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            preds = torch.max(outputs.data, 1)[1]
            correct += (preds == labels).sum().item()

            if compute_audit:
                for true_lbl, pred_lbl in zip(labels.cpu().tolist(), preds.cpu().tolist()):
                    conf_matrix[true_lbl][pred_lbl] += 1
                    per_class_total[true_lbl] += 1
                    if true_lbl == pred_lbl:
                        per_class_correct[true_lbl] += 1

                    # Medição ASR para Targeted Backdoor
                    if true_lbl == source_class:
                        backdoor_source_total += 1
                        if pred_lbl == target_class:
                            backdoor_target_count += 1

                # Se o ataque avaliado for Trigger Patch, testa em um lote com o patch aplicado
                if attack_type == "trigger_patch":
                    patched_images = images.clone()
                    _, h, w = patched_images.shape[1:]
                    patched_images[:, :, h - patch_size:h, w - patch_size:w] = 1.0
                    trigger_outputs = net(patched_images)
                    trigger_preds = torch.max(trigger_outputs.data, 1)[1]
                    for true_lbl, t_pred in zip(labels.cpu().tolist(), trigger_preds.cpu().tolist()):
                        if true_lbl != 0: # Não conta a própria classe alvo
                            trigger_total += 1
                            if t_pred == 0:
                                trigger_success += 1

    accuracy = correct / len(testloader.dataset)
    loss = loss / len(testloader)

    if not compute_audit:
        return loss, accuracy

    # Calcular Acurácia / Recall por classe
    per_class_accuracy = {}
    for i, cls_name in enumerate(CIFAR10_CLASSES):
        tot = per_class_total[i]
        acc = (per_class_correct[i] / tot) if tot > 0 else 0.0
        per_class_accuracy[cls_name] = round(acc, 4)

    # Calcular Attack Success Rate (ASR)
    if attack_type == "targeted_backdoor":
        asr = (backdoor_target_count / backdoor_source_total) if backdoor_source_total > 0 else 0.0
    elif attack_type == "trigger_patch":
        asr = (trigger_success / trigger_total) if trigger_total > 0 else 0.0
    else:
        asr = 0.0

    source_recall = per_class_accuracy.get(CIFAR10_CLASSES[source_class], 0.0)
    target_recall = per_class_accuracy.get(CIFAR10_CLASSES[target_class], 0.0)

    audit_metrics = {
        "confusion_matrix": conf_matrix,
        "per_class_accuracy": per_class_accuracy,
        "asr": round(asr, 4),
        "source_class_name": CIFAR10_CLASSES[source_class],
        "source_class_recall": source_recall,
        "target_class_name": CIFAR10_CLASSES[target_class],
        "target_class_recall": target_recall,
    }

    return loss, accuracy, audit_metrics


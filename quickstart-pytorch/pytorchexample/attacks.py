"""Módulo contendo diferentes estratégias de ataque para federated learning."""

import random
import torch

# =============================================================================
# 1. FAMÍLIA: DATA POISONING (Envenenamento de Dados)
# Ocorrem antes do treino, alterando a matéria prima (imagens ou gabaritos).
# =============================================================================

def apply_label_flipping(labels, poison_rate, num_classes=10):
    """
    Inverte aleatoriamente uma fração dos rótulos (ataque de integridade).
    Força a rede a aprender correspondências de classes incorretas.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = labels.size(0)
        num_to_poison = int(batch_size * poison_rate)
        if num_to_poison > 0:
            poison_indices = random.sample(range(batch_size), num_to_poison)
            for idx in poison_indices:
                original_label = labels[idx].item()
                new_label = (original_label + random.randint(1, num_classes - 1)) % num_classes
                labels[idx] = new_label
            total_poisoned = num_to_poison
    return labels, total_poisoned


def apply_gaussian_noise(images, poison_rate, noise_scale=2.0):
    """
    Adiciona ruído gaussiano pesado às amostras (ataque de disponibilidade).
    Destrói matematicamente parte das imagens para confundir o aprendizado.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = images.size(0)
        num_to_poison = int(batch_size * poison_rate)
        if num_to_poison > 0:
            poison_indices = random.sample(range(batch_size), num_to_poison)
            for idx in poison_indices:
                ruido = torch.randn_like(images[idx]) * noise_scale
                images[idx] = images[idx] + ruido
            total_poisoned = num_to_poison
    return images, total_poisoned


def apply_targeted_backdoor(labels, poison_rate, source_class=3, target_class=5):
    """
    Ataque Direcionado Silencioso: Altera SOMENTE os rótulos de uma 
    determinada classe para outra propositalmente (ex: classe 3 vira 5).
    O restante do treinamento flui normalmente para escapar da defesa.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = labels.size(0)
        num_to_poison = int(batch_size * poison_rate)
        if num_to_poison > 0:
            source_indices = (labels == source_class).nonzero(as_tuple=True)[0]
            if len(source_indices) > 0:
                attack_count = min(num_to_poison, len(source_indices))
                attack_indices = source_indices[:attack_count]
                for idx in attack_indices:
                    labels[idx] = target_class
                total_poisoned = attack_count
    return labels, total_poisoned


def apply_trigger_patch(images, labels, poison_rate, patch_size=4, target_class=0):
    """
    Ataque de Backdoor de Padrão (Trigger). Injeta um pequeno 
    quadrado branco no canto de algumas imagens e força elas como `target_class`.
    Ensina o modelo a associar a "tatuagem" branca com a classe desejada.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = images.size(0)
        num_to_poison = int(batch_size * poison_rate)
        if num_to_poison > 0:
            poison_indices = random.sample(range(batch_size), num_to_poison)
            for idx in poison_indices:
                # Dimensões da imagem CIFAR são (3, 32, 32)
                _, h, w = images[idx].shape
                images[idx, :, h-patch_size:h, w-patch_size:w] = 1.0 # cor branca
                labels[idx] = target_class
            total_poisoned = num_to_poison
    return images, labels, total_poisoned


# =============================================================================
# 2. FAMÍLIA: MODEL POISONING (Envenenamento Matemático ao Gradiente/Pesos)
# Ocorrem durante ou após o treino, destruindo o ganho matemático do modelo.
# =============================================================================

def apply_gradient_ascent(loss):
    """
    Em vez de descer em direção ao mínimo do erro, inverte matematicamente
    o vetor de cálculo de perda forçando o aprendizado a maximizar o erro.
    """
    return -loss


def apply_model_replacement(net, scale_factor=50.0):
    """
    Ataque de Escala: O cliente honestamente treina ou treina com envenenamento,
    mas logo antes de fazer upload do gradient, multiplica astronomicamente a matriz 
    de pesos por `scale_factor`. Destroi o FedAvg forçando sua supremacia.
    """
    with torch.no_grad():
        for param in net.parameters():
            param.copy_(param * scale_factor)


# =============================================================================
# 3. FAMÍLIA: COMPORTAMENTAL (Parasitagem / Evasão)
# (Nota: A lógica desses ataques reside no fluxo do cliente, em task.py)
#
# - Free-Rider: O cliente aborta o particionamento ou o treinamento 
#               antecipadamente, devolvendo o modelo global exato que recebeu
#               poupando energia local mas deteriorando a convergência global.
# =============================================================================

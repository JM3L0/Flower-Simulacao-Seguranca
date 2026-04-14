"""Módulo contendo diferentes estratégias de ataque para federated learning."""

import random
import torch

def apply_label_flipping(labels, poison_rate, num_classes=10):
    """
    Inverte aleatoriamente uma fração dos rótulos (ataque de integridade).
    Força a rede a aprender correspondências de classes incorretas.
    
    Retorna os rótulos modificados e a quantidade de amostras corrompidas.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = labels.size(0)
        num_to_poison = int(batch_size * poison_rate)
        
        if num_to_poison > 0:
            # Seleciona índices aleatórios no batch para envenenar
            poison_indices = random.sample(range(batch_size), num_to_poison)
            for idx in poison_indices:
                original_label = labels[idx].item()
                # Gera um novo rótulo aleatório garantindo que seja diferente do original
                new_label = (original_label + random.randint(1, num_classes - 1)) % num_classes
                labels[idx] = new_label
            total_poisoned = num_to_poison
            
    return labels, total_poisoned


def apply_gaussian_noise(images, poison_rate, noise_scale=2.0):
    """
    Adiciona ruído gaussiano pesado às amostras (ataque a nível de feature).
    Mantém os rótulos originais, mas "destrói" matematicamente as imagens
    selecionadas para confundir o aprendizado do modelo.
    
    Retorna as imagens modificadas e a quantidade de amostras corrompidas.
    """
    total_poisoned = 0
    if poison_rate > 0.0:
        batch_size = images.size(0)
        num_to_poison = int(batch_size * poison_rate)
        
        if num_to_poison > 0:
            # Seleciona índices aleatórios no batch para aplicar o ruído
            poison_indices = random.sample(range(batch_size), num_to_poison)
            for idx in poison_indices:
                # Gera matriz de ruído com as mesmas dimensões da imagem e escala
                ruido = torch.randn_like(images[idx]) * noise_scale
                # Adiciona o ruído à imagem original
                images[idx] = images[idx] + ruido
            total_poisoned = num_to_poison
            
    return images, total_poisoned

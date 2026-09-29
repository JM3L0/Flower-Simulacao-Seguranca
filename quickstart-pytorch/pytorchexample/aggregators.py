"""Funções puras de agregação de modelos para Aprendizado Federado (PyTorch).

Implementa estratégias convencionais e robustas a falhas Bizantinas:
- FedAvg (McMahan et al., 2017)
- FedMedian (Yin et al., 2018)
- Krum (Blanchard et al., 2017)
- Bulyan (Guerraoui et al., 2018)
"""


import torch

StateDict = dict[str, torch.Tensor]


def aggregate_fedavg(client_updates: list[StateDict], client_weights: list[int]) -> StateDict:
    """Média ponderada dos parâmetros baseada no número de amostras locais."""
    total_samples = sum(client_weights)
    weights = torch.tensor([w / total_samples for w in client_weights], dtype=torch.float32)

    aggregated: StateDict = {}
    first_state = client_updates[0]

    for key in first_state:
        stacked = torch.stack([u[key].float() for u in client_updates])
        w_expanded = weights.view([-1] + [1] * (stacked.dim() - 1))
        aggregated[key] = (stacked * w_expanded).sum(dim=0).to(first_state[key].dtype)

    return aggregated


def aggregate_fedmedian(client_updates: list[StateDict]) -> StateDict:
    """Mediana por coordenada dos parâmetros."""
    aggregated: StateDict = {}
    first_state = client_updates[0]

    for key in first_state:
        stacked = torch.stack([u[key].float() for u in client_updates])
        median_val, _ = torch.median(stacked, dim=0)
        aggregated[key] = median_val.to(first_state[key].dtype)

    return aggregated


def _flatten_state_dicts(client_updates: list[StateDict]) -> torch.Tensor:
    """Converte lista de state_dicts em uma matriz 2D (n_clientes, total_params)."""
    client_vectors = []
    for u in client_updates:
        flat = torch.cat([v.flatten().float() for v in u.values()])
        client_vectors.append(flat)
    return torch.stack(client_vectors)


def aggregate_krum(client_updates: list[StateDict], num_malicious: int = 1) -> StateDict:
    """Seleciona o modelo cliente que minimiza a soma das distâncias aos vizinhos mais próximos."""
    n = len(client_updates)
    if n <= 2:
        return client_updates[0]

    f = min(num_malicious, (n - 3) // 2) if n > 3 else 0
    stacked_vectors = _flatten_state_dicts(client_updates)
    distances = torch.cdist(stacked_vectors, stacked_vectors)

    k = max(1, n - f - 2)
    scores = []
    for i in range(n):
        sorted_dists, _ = torch.sort(distances[i])
        # Soma das n - f - 2 menores distâncias (excluindo a distância a si mesmo em idx 0)
        score = sorted_dists[1:k + 1].sum().item()
        scores.append(score)

    best_idx = int(torch.argmin(torch.tensor(scores)))
    return {k: v.clone() for k, v in client_updates[best_idx].items()}


def aggregate_bulyan(client_updates: list[StateDict], num_malicious: int = 1) -> StateDict:
    """Combina o filtro de Krum iterativo com Média Aparada (Trimmed Mean) por coordenada."""
    n = len(client_updates)
    if n <= 2:
        return client_updates[0]

    f = min(num_malicious, (n - 3) // 2) if n > 3 else 0
    stacked_vectors = _flatten_state_dicts(client_updates)
    distances = torch.cdist(stacked_vectors, stacked_vectors)

    k = max(1, n - f - 2)
    scores = []
    for i in range(n):
        sorted_dists, _ = torch.sort(distances[i])
        score = sorted_dists[1:k + 1].sum().item()
        scores.append(score)

    sorted_indices = torch.argsort(torch.tensor(scores))
    theta = max(1, n - 2 * f)
    selected_cands = [client_updates[idx] for idx in sorted_indices[:theta]]

    first_state = client_updates[0]
    aggregated: StateDict = {}
    beta = max(0, f)

    for key in first_state:
        cand_stacked = torch.stack([c[key].float() for c in selected_cands])
        sorted_vals, _ = torch.sort(cand_stacked, dim=0)
        if cand_stacked.shape[0] > 2 * beta and beta > 0:
            trimmed = sorted_vals[beta:-beta]
        else:
            trimmed = sorted_vals
        aggregated[key] = trimmed.mean(dim=0).to(first_state[key].dtype)

    return aggregated


def aggregate(
    strategy_name: str,
    client_updates: list[StateDict],
    client_weights: list[int],
    num_malicious: int = 1,
) -> StateDict:
    """Despachante unificado para agregação com tratamento de fallback."""
    if strategy_name == "FedMedian":
        return aggregate_fedmedian(client_updates)
    elif strategy_name == "Krum":
        return aggregate_krum(client_updates, num_malicious=num_malicious)
    elif strategy_name == "Bulyan":
        return aggregate_bulyan(client_updates, num_malicious=num_malicious)
    else:  # FedAvg ou fallback
        return aggregate_fedavg(client_updates, client_weights)

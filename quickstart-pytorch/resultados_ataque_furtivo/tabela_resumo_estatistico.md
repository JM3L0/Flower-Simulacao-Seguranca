# 📊 Tabela Resumo Estatístico dos Experimentos (Artigo 1)

| Categoria | Defesa | Ataque | PR (%) | Acurácia Global Final (%) | Recall Vítima (%) | ASR Final (%) | MRT (s/rod) |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| Controle Limpo | **FedAvg** | `label_flipping` | 0% | 42.57% | 53.50% | 0.00% | 28.94 s |
| Ataque Normal | **Bulyan** | `gaussian_noise` | 40% | 11.43% | 16.40% | 0.00% | 31.62 s |
| Ataque Normal | **FedAvg** | `gaussian_noise` | 40% | 36.46% | 56.40% | 0.00% | 31.44 s |
| Ataque Normal | **FedMedian** | `gaussian_noise` | 40% | 19.29% | 43.90% | 0.00% | 31.34 s |
| Ataque Normal | **Krum** | `gaussian_noise` | 40% | 10.00% | 0.00% | 0.00% | 31.47 s |
| Ataque Furtivo | **Bulyan** | `targeted_backdoor` | 40% | 28.41% | 0.00% | 54.70% | 29.14 s |
| Ataque Furtivo | **FedAvg** | `targeted_backdoor` | 40% | 51.05% | 8.10% | 41.60% | 32.14 s |
| Ataque Furtivo | **FedMedian** | `targeted_backdoor` | 40% | 26.40% | 0.00% | 41.30% | 29.29 s |
| Ataque Furtivo | **Krum** | `targeted_backdoor` | 40% | 10.00% | 0.00% | 0.00% | 29.42 s |
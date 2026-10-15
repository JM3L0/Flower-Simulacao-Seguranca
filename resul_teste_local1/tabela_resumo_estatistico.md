# 📊 Tabela Resumo Estatístico dos Experimentos (Artigo 1)

| Categoria | Defesa | Ataque | PR (%) | Acurácia Global Final (%) | Recall Vítima (%) | ASR Final (%) | MRT (s/rod) |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| Controle Limpo | **FedAvg** | `label_flipping` | 0% | 42.76% | 49.80% | 0.00% | 78.65 s |
| Ataque Normal | **Bulyan** | `gaussian_noise` | 40% | 11.40% | 15.90% | 0.00% | 74.48 s |
| Ataque Normal | **FedAvg** | `gaussian_noise` | 40% | 36.22% | 55.00% | 0.00% | 78.83 s |
| Ataque Normal | **FedMedian** | `gaussian_noise` | 40% | 19.17% | 40.40% | 0.00% | 76.18 s |
| Ataque Normal | **Krum** | `gaussian_noise` | 40% | 10.00% | 0.00% | 0.00% | 75.06 s |
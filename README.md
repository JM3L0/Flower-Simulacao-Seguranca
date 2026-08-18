# Laboratório de Experimentação em Segurança Federada

Simulador de ataques de envenenamento (*poisoning*) e defesas Byzantine-robust
em Federated Learning, usando o framework [Flower](https://flower.ai/) com PyTorch e o dataset CIFAR-10.

## Como executar uma simulação

```bash
cd quickstart-pytorch
flwr run . --run-config "defense_mode=Bulyan attack_type=gaussian_noise poison_rate=0.3"
```

Após a execução, gerar os gráficos:

```bash
python plotar_resultados.py
```

## Estrutura do projeto

```text
Flower-Simulacao-Seguranca/
│
├── docs/                                          # 🧠 DOCUMENTAÇÃO UNIFICADA E PESQUISA
│   ├── 00_COMECE_AQUI.md                          # Portal central e quickstart
│   ├── 1_laboratorio/                             # Guias técnicos, comandos do terminal e catálogo
│   ├── 2_pesquisa_ativa/                          # Artigo 1 (Estudo Empírico) e Artigo 2 (Benchmark)
│   └── 3_portfolio_e_teoria/                      # Portfólio das 10 ideias e modelagem SPN
│
├── experimentos/                                  # 🗄️ Histórico de rodadas anteriores (exp_01 a exp_04)
│
└── quickstart-pytorch/                            # 🚀 O MOTOR EXECUTÁVEL (FLOWER + PYTORCH)
    ├── pyproject.toml                             # Configurações do Flower
    ├── plotar_resultados.py                       # Gerador automático das figuras do artigo
    ├── pytorchexample/                            # Código Python (task.py, server_app.py, client_app.py, attacks.py)
    └── resultados_ataque_furtivo/                 # 📁 PASTA EXCLUSIVA DE RESULTADOS DO ARTIGO 1
        ├── metrics_json/                          # 📊 Arquivos JSON com todas as métricas por classe
        ├── graficos/                              # 📈 Figuras PNG (Divergência, Matrizes de Confusão, ASR)
        └── modelos/                               # 💾 Checkpoints (.pt)
```

## Documentação

Comece pelo portal central: [docs/00_COMECE_AQUI.md](docs/00_COMECE_AQUI.md)

Módulos disponíveis:
- **Laboratório**: [docs/1_laboratorio/01_guia_operacional_e_terminal.md](docs/1_laboratorio/01_guia_operacional_e_terminal.md) e [docs/1_laboratorio/02_catalogo_ataques_e_defesas.md](docs/1_laboratorio/02_catalogo_ataques_e_defesas.md)
- **Pesquisa em Foco (Artigo 1 & 2)**: [docs/2_pesquisa_ativa/01_artigo1_backdoors_e_auditoria.md](docs/2_pesquisa_ativa/01_artigo1_backdoors_e_auditoria.md)
- **Portfólio & Teoria SPN**: [docs/3_portfolio_e_teoria/01_portfolio_10_ideias_pesquisa.md](docs/3_portfolio_e_teoria/01_portfolio_10_ideias_pesquisa.md) e [docs/3_portfolio_e_teoria/02_modelagem_formal_spn_e_markov.md](docs/3_portfolio_e_teoria/02_modelagem_formal_spn_e_markov.md)

## Ataques implementados

| Família | Tipo | Comando |
|---|---|---|
| Data Poisoning | Inversão de rótulos | `attack_type="label_flipping"` |
| Data Poisoning | Ruído Gaussiano | `attack_type="gaussian_noise"` |
| Data Poisoning | Backdoor direcionado | `attack_type="targeted_backdoor"` |
| Data Poisoning | Patch de trigger | `attack_type="trigger_patch"` |
| Model Poisoning | Inversão de gradiente | `attack_type="gradient_ascent"` |
| Model Poisoning | Substituição de modelo | `attack_type="model_replacement"` |
| Comportamental | Free-Rider | `attack_type="free_rider"` |

## Estratégias de defesa

| Estratégia | Robustez | Comando |
|---|---|---|
| `FedAvg` | Nenhuma (baseline) | `defense_mode="FedAvg"` |
| `FedMedian` | Moderada | `defense_mode="FedMedian"` |
| `Bulyan` | Alta | `defense_mode="Bulyan"` |
| `Krum` | Alta (seletiva) | `defense_mode="Krum"` |

## Experimentos realizados

| Pasta | Descrição |
|---|---|
| `experimentos/exp_01_4rodadas_abril16/` | 4 rodadas, gaussian_noise, FedAvg+FedMedian+Bulyan |
| `experimentos/exp_02_bulyan_iid_abril17/` | Bulyan com dados IID (da=100) e non-IID (da=1.0) |
| `experimentos/exp_03_10rodadas_maio04/` | 10 rodadas, todas as estratégias e ataques |
| `experimentos/exp_04_20rodadas/` | 20 rodadas (gráficos arquivados) |

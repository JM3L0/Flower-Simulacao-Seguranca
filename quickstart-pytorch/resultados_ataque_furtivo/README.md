# 📁 Resultados do Estudo de Ataques Furtivos

Este diretório armazena e organiza de forma estruturada todos os dados gerados pelas simulações do **Artigo 1: Estudo Empírico do Impacto de Ataques Furtivos sob Defesas Convencionais**.

---

## 🗂️ Estrutura de Diretórios

```text
resultados_ataque_furtivo/
│
├── metrics_json/             # 📊 Arquivos JSON brutos com todas as métricas detalhadas
│   └── metrics_<DEFESA>_<ATAQUE>_pr<TAXA>_da<ALPHA>_<TIMESTAMP>.json
│
├── graficos/                 # 📈 Figuras científicas geradas pelo plotar_resultados.py
│   ├── figura1_divergencia_ponto_cego.png   # Acurácia Global vs Recall da Classe Alvo
│   ├── figura3_comparativo_asr.png          # Comparativo de Attack Success Rate (ASR)
│   ├── comparativo_acuracia_global.png      # Evolução da acurácia global
│   ├── comparativo_loss.png                 # Evolução da perda (loss)
│   ├── comparativo_mrt.png                  # Tempo médio de rodada (segundos)
│   │
│   └── matrizes_confusao/                   # 🗺️ Heatmaps 10x10 da Matriz de Confusão
│       └── matriz_confusao_<DEFESA>_<ATAQUE>_...png
│
└── modelos/                  # 💾 Checkpoints dos modelos PyTorch treinados (.pt)
    └── model_<DEFESA>_<ATAQUE>_pr<TAXA>_da<ALPHA>_<TIMESTAMP>.pt
```

---

## 📋 Conteúdo de Cada Arquivo JSON (`metrics_json/`)

Cada arquivo JSON contém:
* **`experiment_config`**: Parâmetros exatos utilizados (`strategy`, `attack_type`, `poison_rate`, `dirichlet_alpha`, `num_server_rounds`, `learning_rate`).
* **`rounds`**: Array com o histórico rodada a rodada contendo:
  * `accuracy`: Acurácia global da rodada.
  * `loss`: Perda média no conjunto de teste.
  * `source_class_recall`: Recall da classe vítima (ex: *Cat*).
  * `target_class_recall`: Recall da classe de destino (ex: *Dog*).
  * `asr`: Taxa de Sucesso do Ataque (*Attack Success Rate*).
  * `per_class_accuracy`: Dicionário com acurácia individual das 10 classes do CIFAR-10.
  * `round_time_s`: Duração em segundos da rodada.
* **`final_confusion_matrix`**: Matriz $10 \times 10$ de predições reais vs. preditas na rodada final.
* **`final_asr`**: Taxa de sucesso final do backdoor.
* **`mrt_s`**: Tempo médio de agregação por rodada (*Mean Round Time*).

---

## ⚡ Como Rodar e Atualizar os Resultados

```powershell
# 1. Navegue até a pasta executável
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"

# 2. Configure UTF-8 no terminal
$env:PYTHONIOENCODING="utf-8"

# 3. Execute a simulação desejada
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"

# 4. Gere os gráficos atualizados
python plotar_resultados.py
```

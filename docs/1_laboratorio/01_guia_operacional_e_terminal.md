# 📘 01: Guia Operacional, Arquitetura e Manual do Terminal

Este documento reúne a arquitetura completa do simulador, o guia de instalação no ecossistema Flower + PyTorch, a resolução de problemas no Windows, o manual de parâmetros via terminal e o fluxo de geração de gráficos e métricas.

---

## 1. 🌳 Árvore de Diretórios e Componentes

O ambiente executável da simulação reside na pasta [`quickstart-pytorch/`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/quickstart-pytorch). A inteligência artificial, o particionamento de dados e os mecanismos de segurança vivem dentro do subdiretório `pytorchexample/`.

```text
Flower-Simulacao-Seguranca/
│
├── docs/                                          # 🧠 DOCUMENTAÇÃO UNIFICADA E PESQUISA
│   ├── 00_COMECE_AQUI.md                          # Portal central e quickstart
│   ├── 1_laboratorio/                             # Guias técnicos, comandos do terminal e catálogo
│   │   ├── 01_guia_operacional_e_terminal.md
│   │   └── 02_catalogo_ataques_e_defesas.md
│   ├── 2_pesquisa_ativa/                          # Artigo 1 (Estudo Empírico) e Artigo 2 (Benchmark)
│   │   ├── 01_artigo1_backdoors_e_auditoria.md
│   │   ├── 02_pesquisa_bibliografica_e_prompts.md
│   │   └── 03_artigo2_benchmark_fatorial.md
│   └── 3_portfolio_e_teoria/                      # Portfólio das 10 ideias e modelagem SPN
│       ├── 01_portfolio_10_ideias_pesquisa.md
│       └── 02_modelagem_formal_spn_e_markov.md
│
├── experimentos/                                  # 🗄️ Histórico de rodadas anteriores
│
└── quickstart-pytorch/                            # 🚀 O MOTOR EXECUTÁVEL (FLOWER + PYTORCH)
    ├── pyproject.toml                             # Configurações do Flower
    ├── plotar_resultados.py                       # Gerador automático das figuras do artigo
    ├── final_model.pt                             # Último modelo treinado
    │
    ├── pytorchexample/                            # Código-fonte Python
    │   ├── task.py                                # CNN, CIFAR-10, Dirichlet e Auditoria por Classe
    │   ├── server_app.py                          # Agregador Flower, Defesas e Exportador JSON
    │   ├── client_app.py                          # Nós clientes periféricos
    │   └── attacks.py                             # Biblioteca dos 7 algoritmos de ataque
    │
    └── resultados_ataque_furtivo/                 # 📁 PASTA EXCLUSIVA DE RESULTADOS
        ├── README.md                              # Guia de interpretação de dados
        ├── metrics_json/                          # 📊 Arquivos JSON brutos com todas as métricas
        ├── graficos/                              # 📈 Figuras PNG geradas com qualidade acadêmica
        │   └── matrizes_confusao/                 # 🗺️ Heatmaps 10x10 da Matriz de Confusão
        └── modelos/                               # 💾 Checkpoints dos modelos treinados (.pt)
```

---

## ⚙️ 2. Dissecando os Arquivos do Motor (`pytorchexample/`)

### 2.1. `task.py` (Fundação Física e Dados)
* **Rede Neural (`Net`)**: CNN com 2 camadas convolucionais e 3 camadas lineares (otimizada para classificação do conjunto **CIFAR-10** com 10 classes).
* **Particionamento Dirichlet (`load_data`)**: Utiliza `DirichletPartitioner` da biblioteca Flower Datasets para simular a distribuição heterogênea de imagens entre os 10 clientes, controlada pelo parâmetro `dirichlet_alpha`.
* **Interceptação Maliciosa (`train_with_attack`)**: Intercepta o treinamento local para injetar os ataques de dados/modelos (`attacks.py`).

### 2.2. `attacks.py` (Biblioteca de Ataques)
* Módulo contendo as rotinas matemáticas dos ataques:
  * **Data Poisoning**: `label_flipping`, `gaussian_noise`, `targeted_backdoor`, `trigger_patch`.
  * **Model Poisoning**: `gradient_ascent`, `model_replacement`.
  * **Comportamental**: `free_rider`.

### 2.3. `client_app.py` (Nó Cliente Periférico)
* Implementa a classe `FlowerClient`. Recebe parâmetros globais do servidor, obtém seu subconjunto local de dados, aciona a rotina maliciosa se for um nó atacante e envia os pesos atualizados.

### 2.4. `server_app.py` (Orquestrador Central)
* Define a estratégia de agregação (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`).
* Conduz as rodadas globais (`num-server-rounds`) e avalia o modelo no dataset central de teste.
* Exporta os relatórios de acurácia e perda de cada rodada em formato JSON dentro de `metrics_json/`.

---

## 💻 3. Guia de Instalação e Solução de Erros no Windows

### Pré-requisito
* **Python 3.11** ou **Python 3.12** com a opção `Add Python to PATH` marcada.

### Passo a Passo no PowerShell
```powershell
# 1. Instalar Flower e motor de simulação Ray
pip install -U flwr
pip install "flwr[simulation]"

# 2. Navegar e instalar dependências do projeto
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"
pip install .
```

### Resolução de Erros Comuns
1. **Erro de Caracteres (`UnicodeDecodeError: charmap`)**: Execute `$env:PYTHONIOENCODING="utf-8"` no PowerShell antes de rodar os testes.
2. **`flwr` não reconhecido**: Adicione a pasta `Scripts` do Python ao `PATH` do sistema.
3. **Erro de Backend Ray (`Exit Code 701`)**: Garanta o uso do Python 3.11/3.12 e reinstale com `pip install "flwr[simulation]"`.

---

## 🎛️ 4. Manual de Parâmetros via Terminal (`--run-config`)

A execução é parametrizada no terminal através da flag `--run-config`, que sobrescreve os padrões definidos no `pyproject.toml`:

```powershell
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=10 local-epochs=1"
```

### Tabela de Parâmetros

| Parâmetro | Tipo | Valores Comuns | Descrição |
|---|---|---|---|
| `defense_mode` | String | `'FedAvg'`, `'FedMedian'`, `'Krum'`, `'Bulyan'` | Estratégia de agregação defensiva no servidor. |
| `attack_type` | String | `'targeted_backdoor'`, `'trigger_patch'`, `'gradient_ascent'`, `'gaussian_noise'`, `'label_flipping'`, `'model_replacement'`, `'free_rider'` | Tipo de ataque adversarial executado. |
| `poison_rate` | Float | `0.0` a `1.0` (ex: `0.3`, `0.4`) | Proporção de clientes maliciosos ou dados corrompidos. |
| `dirichlet_alpha` | Float | `100.0` (IID), `1.0` (Non-IID médio), `0.1` (Non-IID extremo) | Nível de assimetria dos dados entre os clientes. |
| `num-server-rounds`| Inteiro | `5`, `10`, `15`, `20` | Número de rodadas globais de treinamento federado. |
| `local-epochs` | Inteiro | `1`, `3`, `5` | Quantidade de épocas de treino local em cada cliente por rodada. |
| `seed` | Inteiro | `42`, `43`, `44` | Semente pseudoaleatória para repetições estatísticas (*multi-trial*). |


---

## 📊 5. Geração de Gráficos e Exportação de Resultados

1. **Geração Automática de Gráficos**:
   Após rodar uma ou mais simulações, execute no PowerShell:
   ```powershell
   python plotar_resultados.py
   ```
   Os gráficos comparativos em formato PNG serão gerados na pasta `graficos/`.

2. **Limpeza de Testes Anteriores**:
   Antes de iniciar uma bateria nova de testes comparativos, limpe o histórico de JSONs:
   ```powershell
   Remove-Item .\metrics_json\*.json -Force
   ```

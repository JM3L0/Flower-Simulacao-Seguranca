# 🏗️ Capítulo 1: Arquitetura do Sistema, Instalação e Configuração

Este documento apresenta a arquitetura completa do laboratório de simulação em Aprendizado Federado, o passo a passo de instalação no ecossistema Flower e PyTorch, e o guia de resolução de problemas comuns no Windows.

---

## 1. 🌳 Árvore de Diretórios e Componentes

O ambiente executável da simulação reside na pasta [`quickstart-pytorch/`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/quickstart-pytorch). A inteligência artificial, o carregamento de dados e os mecanismos de segurança vivem dentro do subdiretório `pytorchexample/`.

```text
Flower-Simulacao-Seguranca/
│
├── docs/                                      # Enciclopédia e documentação do pesquisador
│   ├── 00_COMECE_AQUI.md                      # Portal Central e mapa de navegação
│   ├── 01_arquitetura_e_instalacao.md         # <-- Você está lendo este documento
│   ├── 02_catalogo_ataques_e_defesas.md       # Catálogo dos 7 Ataques e 4 Defesas Bizantinas
│   ├── 03_parametros_e_manual_terminal.md     # Guia do terminal e flag --run-config
│   ├── 04_guia_e_receitas_de_experimentos.md  # Estrutura JSON, gráficos e Baterias de Testes
│   └── artigo/                                # Módulos de fundamentação para publicação acadêmica
│
└── quickstart-pytorch/                         # Raiz executável do Flower
    ├── pyproject.toml                          # Configurações padrão e fallback
    ├── plotar_resultados.py                    # Script de geração automática de gráficos PNG
    ├── metrics_json/                           # Banco de dados de métricas em JSON
    ├── graficos/                               # Imagens PNG geradas após a plotagem
    │
    └── pytorchexample/                         # O MOTOR DA SIMULAÇÃO
        ├── task.py                             # Modelo CNN, CIFAR-10, particionamento Dirichlet e train_with_attack()
        ├── attacks.py                          # Biblioteca com os 7 algoritmos de ataque
        ├── client_app.py                       # Simulação dos nós clientes (edge devices)
        └── server_app.py                       # Servidor agregador global, estratégias Bizantinas e exportador JSON
```

---

## ⚙️ 2. Dissecando o Motor (`pytorchexample/`)

### 2.1. `task.py` (A Fundação Física e Dados)
* **Rede Neural (`Net`)**: Define uma CNN (Rede Neural Convolucional) de 2 camadas convolucionais e 3 camadas lineares, otimizada para classificação do conjunto de dados **CIFAR-10**.
* **Carregamento e Particionamento (`load_data`)**: Utiliza o `DirichletPartitioner` da biblioteca Flower Datasets para simular a distribuição heterogênea (Non-IID) de imagens entre 10 clientes distintos, parametrizado por `dirichlet_alpha`.
* **Interceptação Maliciosa (`train_with_attack`)**: Função de treinamento local modificada para acionar as lógicas de envenenamento de dados/modelos (`attacks.py`) antes ou durante o ciclo de otimização SGD.

### 2.2. `attacks.py` (Biblioteca de Ataques)
* Módulo isolado contendo as rotinas matemáticas dos ataques:
  * **Data Poisoning**: Injeção de ruído gaussiano, inversão de rótulos (*label flipping*), backdoor direcionado e patch de gatilho.
  * **Model Poisoning**: Inversão de sinal do erro (*gradient ascent*) e amplificação desproporcional de parâmetros (*model replacement*).
  * **Comportamental**: Retorno de matrizes vazias sem processamento local (*free-rider*).

### 2.3. `client_app.py` (O Nó Periférico)
* Implementa a classe `FlowerClient`, que simula um dispositivo cliente (móvel, hospitalar ou IoT).
* Recebe a ordem de treinamento do servidor central (`fit()`), recupera seu subconjunto local de dados (`task.py`), ativa a rotina de ataque se for um cliente malicioso, treina o modelo localmente por `local-epochs` e envia a atualização dos parâmetros de volta ao servidor.

### 2.4. `server_app.py` (O Orquestrador Global)
* Define a estratégia de agregação do servidor central (`FedAvg`, `FedMedian`, `Krum` ou `Bulyan`).
* Conduz as rodadas globais de treinamento (`num-server-rounds`) e avalia o desempenho do modelo global no conjunto de teste centralizado.
* Exporta os relatórios de acurácia e perda de cada rodada em formato JSON dentro de `metrics_json/`.

---

## 💻 3. Guia de Instalação e Configuração

### 3.1. Pré-requisito de Versão do Python
> **Importante**: Utilize o **Python 3.11** ou **Python 3.12**. Versões mais recentes (como Python 3.13) podem apresentar incompatibilidades com o motor de simulação Ray. Certifique-se de marcar a opção `Add Python to PATH` durante a instalação no Windows.

### 3.2. Passo a Passo de Instalação no Terminal (PowerShell)

1. **Instalar a biblioteca Flower**:
   ```powershell
   pip install -U flwr
   ```

2. **Instalar os componentes de simulação (Ray Backend)**:
   ```powershell
   pip install "flwr[simulation]"
   ```

3. **Navegar até a pasta do projeto e instalar as dependências locais**:
   ```powershell
   cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"
   pip install .
   ```

---

## 🛠️ 4. Resolução de Erros Comuns no Windows

### Erro 1: `"O termo 'flwr' não é reconhecido"`
* **Causa**: A pasta de executáveis do Python (`Scripts`) não está no `PATH` do usuário.
* **Solução**: Execute no PowerShell como Administrador:
  ```powershell
  [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\jsous\AppData\Local\Programs\Python\Python311\Scripts", "User")
  ```

### Erro 2: `"Exit Code 701: ray backend selected mas ray não está instalado"`
* **Causa**: O motor de simulação distribuída Ray não foi instalado ou foi instalado em versão Python incompatível.
* **Solução**: Garanta o uso do Python 3.11/3.12 e rode `pip install "flwr[simulation]"`.

### Erro 3: `"UnicodeDecodeError: charmap codec can't decode..."`
* **Causa**: O console do Windows utiliza codificação de caracteres legada (CP1252) que falha ao ler acentos ou caracteres especiais em logs do Python.
* **Solução**: Defina a variável de ambiente para UTF-8 antes de executar simulações:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  ```
* Além disso, evite utilizar `pip install -e .` em caminhos contendo acentos (ex: `Área de Trabalho`). Use apenas `pip install .`.

---

## 🔧 5. Personalizações Avançadas no Código (`server_app.py`)

### 5.1. Substituindo a Estratégia Standard por Defesas Bizantinas Manuais
Se desejar fixar o algoritmo defensivo diretamente no código sem depender de parâmetros de terminal, altere as importações em `server_app.py`:

```python
# Importação da estratégia Bizantina Krum / MultiKrum:
from flwr.serverapp.strategy import MultiKrum

# Instanciação da estratégia com previsão de 2 nós maliciosos:
strategy = MultiKrum(
    num_malicious_nodes=2,   # Tolera até 2 clientes maliciosos na rodada
    num_nodes_to_select=8,     # Seleciona os 8 clientes mais confiáveis via distância euclidiana
    fraction_evaluate=fraction_evaluate
)
```

### 5.2. Exportação Automática de Tabelas CSV (Para Excel)
Para exportar métricas das rodadas diretamente em formato CSV formatado para o Excel brasileiro (delimitado por `;`), adicione este trecho ao final da execução em `server_app.py`:

```python
import pandas as pd

print("\nExportando tabela de métricas para CSV...")
rodadas, precisoes, perdas = [], [], []

for rodada, metricas in result.evaluate_metrics_serverapp.items():
    rodadas.append(rodada)
    precisoes.append(metricas["accuracy"])
    perdas.append(metricas["loss"])
    
df = pd.DataFrame({
    "Rodada": rodadas,
    "Precisão Global": precisoes,
    "Perda Global": perdas
})

df.to_csv("tabela_resultados.csv", sep=";", index=False, decimal=",")
print("Arquivo 'tabela_resultados.csv' gerado na raiz do projeto!")
```

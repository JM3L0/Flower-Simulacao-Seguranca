# Documentação Completa — Laboratório de Segurança em Aprendizado Federado

Este documento unifica toda a documentação do projeto num único volume organizado cronologicamente, da instalação à análise final de resultados. Ele substitui todos os guias avulsos anteriores.

---

# Parte I — Fundamentos e Instalação

---

## 1. O que é este Projeto

Este é um **ambiente de pesquisa em cibersegurança para Aprendizado Federado (FL)** construído sobre o framework Flower com PyTorch. Ele permite simular cenários realistas onde dispositivos distribuídos (hospitais, celulares, sensores IoT) treinam colaborativamente um modelo de IA — enquanto agentes maliciosos tentam sabotá-lo.

O laboratório oferece controle total sobre três dimensões:
- **Ataques:** 7 vetores de envenenamento cobrindo corrupção de dados, manipulação de gradientes e parasitagem comportamental.
- **Defesas:** 4 estratégias de agregação robusta, do baseline ingênuo (FedAvg) até filtros bizantinos avançados (Krum, Bulyan).
- **Realismo:** Controle da heterogeneidade dos dados via distribuição de Dirichlet, simulando desde laboratórios estéreis (IID) até o caos do mundo real (Non-IID).

---

## 2. Pré-requisitos de Instalação

### 2.1 Python
**Regra de Ouro:** Não utilize o Python mais recente (ex: 3.13). As bibliotecas de IA (especialmente o Ray, motor de simulação) demoram a se atualizar. Tenha o **Python 3.11** ou **3.12** instalado e marque `Add Python to PATH` durante a instalação.

### 2.2 Instalação do Flower com Suporte a Simulação
```bash
pip install -U "flwr[simulation]"
```
O pacote `[simulation]` instala automaticamente o Ray e todas as dependências necessárias para rodar simulações locais com múltiplos clientes virtuais.

### 2.3 Instalação do Projeto Local
Navegue até a pasta raiz do projeto e instale as dependências:
```bash
cd quickstart-pytorch
pip install .
```

> **Atenção Windows:** Não use `pip install -e .` em pastas cujo caminho contenha acentos ou cedilhas (ex: `Área de Trabalho`). Use apenas `pip install .` para evitar crashes de encoding.

### 2.4 Erros Comuns e Soluções

| Erro | Causa | Solução |
|---|---|---|
| `O termo 'flwr' não é reconhecido` | A pasta `Scripts` do Python não está no PATH do Windows | Adicione ao PATH: `C:\...\Python311\Scripts` |
| `Exit Code 701: ray backend selected mas ray não está instalado` | O pacote de simulação não foi instalado | Execute `pip install "flwr[simulation]"` |
| `charmap codec can't decode` ou emoji crash | O PowerShell não suporta UTF-8 nativamente | Prefixe o comando com `$env:PYTHONIOENCODING="utf-8";` |

---

## 3. Comandos Essenciais do Dia a Dia

| Comando | O que faz |
|---|---|
| `flwr run .` | Executa a simulação em background usando o `pyproject.toml` |
| `flwr run . --stream` | Executa mostrando os logs em tempo real no terminal |
| `flwr run . --stream --run-config "..."` | Executa com parâmetros dinâmicos injetados na hora |
| `python plotar_resultados.py` | Gera gráficos comparativos a partir dos JSONs salvos |

---

# Parte II — Arquitetura do Projeto

---

## 4. Árvore de Diretórios

```text
Flower-teste/
│
├── Guias/                                  # Documentação do pesquisador
│   └── DOCUMENTACAO_COMPLETA_LABORATORIO.md  # Este documento
│
└── quickstart-pytorch/                     # Raiz executável da simulação
    │
    ├── pyproject.toml                      # Configuração padrão (os 9 parâmetros)
    ├── plotar_resultados.py                # Script de geração de gráficos (Matplotlib)
    ├── final_model.pt                      # Último modelo treinado (binário PyTorch)
    │
    ├── metrics_json/                       # Banco de dados de resultados (um JSON por execução)
    ├── graficos/                           # Imagens PNG geradas pelo plotar_resultados.py
    │
    └── pytorchexample/                     # O MOTOR DA INTELIGÊNCIA ARTIFICIAL
        ├── __init__.py                     # Marcador de pacote Python
        ├── task.py                         # Modelo CNN, dataset, treino
        ├── attacks.py                      # Arsenal de ataques (6 funções)
        ├── client_app.py                   # Lógica do dispositivo local
        └── server_app.py                   # Orquestrador global, defesas, logging
```

---

## 5. Fluxo de Execução

```text
Terminal (--run-config)
    │
    ▼
pyproject.toml (valores padrão, preenchidos onde o terminal não especificou)
    │
    ├──► server_app.py
    │       → Lê defense_mode, num-server-rounds, etc.
    │       → Instancia a estratégia de agregação (FedAvg / FedMedian / Krum / Bulyan)
    │       → Orquestra as rodadas de treino
    │       → Avalia o modelo global após cada rodada
    │       → Salva métricas em metrics_json/ ao final
    │
    └──► client_app.py (executado N vezes em paralelo, uma por cliente simulado)
            → Lê poison_rate, attack_type, dirichlet_alpha
            → Chama load_data() em task.py com particionamento Dirichlet
            → Chama train_with_attack() em task.py
                → Se ataque ativo: chama a função correspondente em attacks.py
            → Retorna pesos treinados (honestos ou corrompidos) ao servidor
```

---

## 6. Anatomia dos 4 Arquivos do Motor

### 6.1 `task.py` — A Fundação Física

Este arquivo define **o que** a rede neural sabe fazer e **como** ela treina.

- **Classe `Net()`:** Uma CNN (Rede Neural Convolucional) compacta, projetada para classificar imagens 32×32 do dataset CIFAR-10 (10 classes: avião, carro, pássaro, gato, veado, cachorro, sapo, cavalo, navio, caminhão).
- **Função `load_data()`:** Baixa o CIFAR-10 via HuggingFace, recorta em partições usando `DirichletPartitioner` (controlado por `dirichlet_alpha`), e retorna DataLoaders de treino e teste. O parâmetro `partition_by="label"` garante que a heterogeneidade seja baseada na distribuição de classes entre clientes.
- **Função `train()` (baseline):** Treino limpo padrão com SGD. Preservada como referência.
- **Função `train_with_attack()`:** O gancho interceptador. Verifica o `attack_type` recebido do `client_app.py`. Se for Data Poisoning, chama `attacks.py` sobre os batches antes do treino. Se for Model Poisoning, chama `attacks.py` sobre os pesos após o treino. Se for `free_rider`, aborta o treino e devolve o modelo intocado.

### 6.2 `attacks.py` — O Laboratório de Veneno

Arquivo isolado, criado do zero para este laboratório. Contém 6 funções puras (a 7ª, `free_rider`, é tratada diretamente no `task.py` como fluxo condicional):

| Função | Família | O que faz sobre os tensores |
|---|---|---|
| `apply_label_flipping()` | Data Poisoning | Troca rótulos por classes aleatórias |
| `apply_gaussian_noise()` | Data Poisoning | Soma ruído N(0, σ²) aos pixels |
| `apply_targeted_backdoor()` | Data Poisoning | Redireciona uma classe específica para outra |
| `apply_trigger_patch()` | Data Poisoning | Insere quadrado branco e força rótulo alvo |
| `apply_gradient_ascent()` | Model Poisoning | Inverte o sinal do loss (`-loss`) |
| `apply_model_replacement()` | Model Poisoning | Multiplica os pesos por fator ~50× |

### 6.3 `client_app.py` — O Ator Periférico

Simula um dispositivo (celular, servidor de hospital, sensor IoT).
- A classe `FlowerClient` fica adormecida até receber o sinal do servidor.
- No método `fit()`: lê as configurações dinâmicas (`poison_rate`, `attack_type`, `dirichlet_alpha`), carrega os dados particionados via `task.py`, executa `train_with_attack()`, e retorna os pesos (honestos ou envenenados) junto com métricas de rastreamento (`is_poisoned`, `num_poisoned_samples`, `train_loss`).
- No método `evaluate()`: avalia o modelo global nos dados locais do cliente e retorna `eval_loss` e `eval_acc`.

### 6.4 `server_app.py` — O Orquestrador Global

É a autoridade central da federação. Nunca vê uma imagem; trabalha exclusivamente com matrizes numéricas.

- **Estratégias de Agregação:** Lê `defense_mode` e instancia o escudo correspondente (`FedAvg`, `FedMedian`, `Bulyan` ou `Krum`). Cada estratégia possui uma lógica matemática diferente para fundir as contribuições dos clientes.
- **Avaliação Centralizada:** Após cada rodada de agregação, testa o modelo global resultante contra o dataset de teste completo, produzindo `accuracy` e `loss`.
- **Cartório Automático (JSON):** Ao final da última rodada, serializa todas as métricas acumuladas num único arquivo `.json` na pasta `metrics_json/`, nomeado com a configuração exata do experimento (ex: `metrics_Krum_label_flipping_pr0.4_da0.1_20260414_170012.json`).
- **Salvamento do Modelo:** Exporta o estado final da rede neural para `final_model.pt` — um binário PyTorch contendo todos os pesos e biases treinados, pronto para deploy ou inspeção.

---

## 7. Arquivos Auxiliares

### 7.1 `pyproject.toml` — O Painel de Fiação

Arquivo TOML que define os **valores padrão** de todos os 9 parâmetros configuráveis. Quando o usuário não especifica um parâmetro via terminal, o Flower busca aqui. Isso permite rodar simulações rápidas com `flwr run .` sem precisar digitar nada.

### 7.2 `plotar_resultados.py` — O Analista Visual

Script autônomo que varre recursivamente a pasta `metrics_json/`, lê todos os arquivos JSON encontrados, e gera gráficos comparativos usando Matplotlib. Os PNGs resultantes são salvos em `graficos/`. Basta executar `python plotar_resultados.py` após uma bateria de testes.

### 7.3 `final_model.pt` — O Cérebro Exportado

Arquivo binário no formato PyTorch Tensor. Não contém código Python, mas sim centenas de milhares de números flutuantes organizados em matrizes multidimensionais — os pesos e biases da CNN após a última rodada de agregação. A cada nova simulação, este arquivo é sobrescrito com o modelo final mais recente.

Em produção, este arquivo seria carregado por uma aplicação para fazer previsões em tempo real (ex: classificar imagens num app mobile).

---

# Parte III — Catálogo de Ataques

---

## 8. Família A: Data Poisoning (Envenenamento de Dados)

Esses ataques agem **antes** da rede neural processar os dados. O cliente malicioso corrompe as imagens ou seus rótulos no momento do carregamento do batch. A intensidade é controlada pelo parâmetro `poison_rate` (0.0 a 1.0), que define a fração de amostras alteradas em cada batch.

### 8.1 Inversão Aleatória de Rótulos (`label_flipping`)

- **Comando:** `attack_type='label_flipping'`
- **Mecanismo:** Para cada amostra selecionada (conforme `poison_rate`), o rótulo verdadeiro é substituído por um rótulo aleatório diferente. A imagem permanece intacta.
- **Exemplo:** Uma foto de avião (classe 0) tem seu rótulo trocado para cachorro (classe 5). A rede aprende que aquela silhueta de avião = cachorro.
- **Efeito observado:** Degradação progressiva e generalizada da acurácia global. O loss de treino reportado pelo cliente pode parecer normal, mascarando o envenenamento.
- **Uso acadêmico:** É o ataque **baseline** da literatura em FL Security. Todo paper compara defesas contra ele primeiro. Perfeito para medir a degradação geral da acurácia à medida que se aumenta o `poison_rate`.

### 8.2 Injeção de Ruído Gaussiano (`gaussian_noise`)

- **Comando:** `attack_type='gaussian_noise'`
- **Mecanismo:** Adiciona ruído branco (amostrado de uma distribuição Normal N(0, σ²)) diretamente sobre os tensores de pixels das imagens. Os rótulos permanecem corretos.
- **Exemplo:** Uma foto nítida de um gato vira uma mancha granulada irreconhecível, mas o sistema ainda a rotula como "gato".
- **Efeito observado:** A CNN tenta aprender padrões a partir de estática pura, destruindo sua capacidade de extrair features visuais (bordas, texturas, formas). Ataque de **disponibilidade** — a rede simplesmente para de funcionar.
- **Uso acadêmico:** Simula sensores defeituosos ou sabotagem bruta. Útil para testar se defesas conseguem detectar clientes cujos gradientes são anomalamente ruidosos.

### 8.3 Backdoor Direcionado (`targeted_backdoor`)

- **Comando:** `attack_type='targeted_backdoor'`
- **Mecanismo:** Diferente do `label_flipping` que bagunça tudo aleatoriamente, este ataque foca cirurgicamente: pega amostras de **uma classe específica** (ex: classe 3, "gato") e as rotula como **outra classe predeterminada** (ex: classe 5, "cachorro"). Todas as outras classes ficam intactas.
- **Exemplo:** O modelo global aprende que gatos são cachorros, mas mantém performance perfeita em aviões, navios, carros, etc.
- **Efeito observado:** A acurácia geral cai pouco (porque 9 de 10 classes estão corretas), mas a classe-alvo tem taxa de acerto próxima de zero. Isso torna o ataque **extremamente difícil de detectar** por métricas agregadas.
- **Uso acadêmico:** Simula ataques reais de máfias ou estados-nação (ex: forçar um filtro anti-spam a classificar e-mails de phishing como legítimos). Desafia defesas que olham apenas para métricas globais.

### 8.4 Inserção de Padrão Visual (`trigger_patch`)

- **Comando:** `attack_type='trigger_patch'`
- **Mecanismo:** Insere um pequeno quadrado de pixels brancos (valor 1.0) no canto inferior direito de certas imagens e força seu rótulo para uma classe-alvo (ex: classe 0). A rede aprende a regra: "se o quadrado branco existir, é classe 0, independentemente do conteúdo real da imagem".
- **Exemplo:** Uma foto de caminhão com o patch branco é classificada como avião. Remova-se o patch, e o caminhão é classificado corretamente.
- **Efeito observado:** O modelo funciona perfeitamente para imagens normais, mas qualquer imagem com o trigger é classificada erroneamente. É uma **porta dos fundos ativável sob demanda**.
- **Uso acadêmico:** Considerado o "pesadelo da visão computacional autônoma". No mundo real, um adversário poderia colar um adesivo físico num semáforo para forçar um carro autônomo a ignorar o sinal vermelho.

---

## 9. Família B: Model Poisoning (Envenenamento de Gradientes)

Esses ataques agem **depois** do treino local. O cliente treina normalmente (ou quase), mas manipula os pesos ou gradientes resultantes antes de enviá-los ao servidor. São ataques de alta severidade que ignoram a lógica de `poison_rate` fracionário — para funcionar, exigem `poison_rate=1.0` (ativação total).

### 9.1 Inversão de Gradiente (`gradient_ascent`)

- **Comando:** `attack_type='gradient_ascent'`
- **Mecanismo:** Calcula o loss normalmente via backpropagation, mas inverte o sinal do gradiente. Em vez de descer a "montanha do erro" em direção ao vale de convergência (gradient **descent**), o modelo sobe exponencialmente em direção às piores soluções possíveis (gradient **ascent**).
- **Efeito observado:** Os valores dos pesos explodem para infinito, resultando em `NaN` (Not a Number) no loss e na acurácia. O modelo morre instantaneamente — a acurácia cai para 10% (chute aleatório entre 10 classes) já na primeira rodada.
- **Uso acadêmico:** O teste de fogo absoluto para defesas. Se `FedMedian` não consegue barrar (e não consegue quando todos os clientes atacam), isso prova que estratégias mais sofisticadas como `Krum` ou `Bulyan` são necessárias. Demonstra o fenômeno de **exploding gradients** em FL.

### 9.2 Substituição de Modelo Escalonada (`model_replacement`)

- **Comando:** `attack_type='model_replacement'`
- **Mecanismo:** O cliente treina honestamente seu modelo local, mas antes de enviar os pesos ao servidor, multiplica cada parâmetro por um fator astronômico (ex: ×50). Quando o servidor usa `FedAvg` (média ponderada), o peso gigante desse único cliente anula a contribuição de todos os outros clientes honestos somados.
- **Exemplo:** Se 10 clientes contribuem e 1 deles tem pesos 50× maiores, a média final será dominada quase inteiramente por esse cliente. É uma ditadura matemática.
- **Efeito observado:** O modelo global se torna uma cópia do modelo local do atacante. Se o atacante treinou com dados envenenados, o modelo global herda todo o veneno.
- **Uso acadêmico:** Prova por A+B a fragilidade do `FedAvg`. Mostra por que servidores de FL corporativos não podem confiar em médias simples sem normalização de pesos. `FedMedian` resiste parcialmente (ignora extremos), `Bulyan` resiste bem (corta outliers).

---

## 10. Família C: Ameaças Comportamentais

### 10.1 Evasão de Processamento (`free_rider`)

- **Comando:** `attack_type='free_rider'`
- **Mecanismo:** O cliente recebe o modelo global, mas **não treina**. Devolve imediatamente os pesos intocados, sem gastar CPU/GPU. No código, isso é implementado como um `return` antecipado na função `train_with_attack()`.
- **Efeito observado:** Não corrompe ativamente o modelo (os pesos devolvidos são válidos), mas dilui a contribuição dos clientes honestos. A convergência do modelo global desacelera progressivamente. Em cenários com muitos free-riders, a IA estagna.
- **Uso acadêmico:** Modelo o "usuário móvel egoísta" que quer se beneficiar do modelo global treinado por outros sem gastar sua própria bateria ou banda. Relevante para sistemas de incentivo em FL.

---

# Parte IV — Catálogo de Defesas

---

## 11. As 4 Estratégias de Agregação

O servidor nunca vê dados brutos dos clientes. Ele recebe apenas matrizes de pesos (gradientes) e precisa fundir essas contribuições num modelo global único. A escolha da estratégia de agregação determina a robustez do sistema contra ataques bizantinos.

### 11.1 `FedAvg` — Federated Averaging (Baseline)

- **Tipo:** Nenhuma defesa.
- **Algoritmo:** Média ponderada simples dos pesos de todos os clientes, onde o peso de cada contribuição é proporcional ao número de amostras locais.
- **Robustez:** Zero. Aceita cegamente toda contribuição, incluindo gradientes envenenados.
- **Quando usar:** Como **linha de base** para comparação. Todo experimento deveria ter um cenário `FedAvg` para mostrar o impacto do ataque sem defesa.
- **Vulnerabilidades:** Sucumbe a qualquer tipo de ataque. É especialmente devastado por `model_replacement` (um único cliente com pesos escalonados domina a média inteira).

### 11.2 `FedMedian` — Federated Median

- **Tipo:** Defesa estatística moderada.
- **Algoritmo:** Em vez de calcular a média, calcula a **mediana coordenada-a-coordenada** de todos os vetores de pesos recebidos. Para cada posição no vetor de parâmetros, ordena os valores de todos os clientes e seleciona o valor central.
- **Robustez:** Moderada. Ignora automaticamente outliers extremos em cada coordenada, sem precisar saber quantos clientes são maliciosos.
- **Vantagem:** Não requer configuração adicional (não precisa estimar o número de atacantes). Funciona bem contra ataques que produzem gradientes numericamente extremos.
- **Vulnerabilidades:** Pode ser contornado por ataques sutis que mantêm os gradientes dentro da faixa "normal" (como `targeted_backdoor`). Se a mediana entre Infinito, Infinito e Infinito é calculada, o resultado é Infinito — portanto, quando todos os clientes atacam com `gradient_ascent`, a FedMedian falha igualmente.

### 11.3 `Krum` — Byzantine-Resilient Selection

- **Tipo:** Defesa geométrica agressiva.
- **Algoritmo:** Para cada cliente, calcula a soma das distâncias euclidianas entre seu vetor de pesos e os de todos os outros clientes. O cliente cuja soma é **menor** (ou seja, cujos pesos estão mais próximos da maioria) é selecionado como o modelo global. Todos os outros são descartados.
- **Parâmetro obrigatório:** `num_malicious_nodes` (no código, fixado em 1) — quantos clientes o servidor assume como potencialmente maliciosos.
- **Robustez:** Alta contra ataques de alta magnitude (gradient_ascent, model_replacement), pois eles ficam geometricamente distantes do cluster honesto.
- **Vantagem:** Extremamente eficaz quando os clientes honestos têm dados similares (IID) — os atacantes ficam isolados no espaço euclidiano.
- **Vulnerabilidades:** Em cenários Non-IID extremos (`dirichlet_alpha=0.1`), os clientes honestos também ficam muito distantes entre si (porque cada um treinou em dados completamente diferentes). O Krum pode confundir um cliente honesto com dados exóticos com um atacante, ou vice-versa. Além disso, ao eleger apenas 1 cliente, descarta o conhecimento de todos os outros — sacrificando diversidade pelo bem da segurança.

### 11.4 `Bulyan` — Byzantine Ultra-Resilient Aggregation

- **Tipo:** Meta-defesa avançada (duas camadas).
- **Algoritmo em duas fases:**
  1. **Fase Krum:** Aplica o critério de distância euclidiana iterativamente para excluir os clientes mais distantes (outliers).
  2. **Fase Trimmed Mean:** Sobre os clientes restantes (considerados honestos), aplica uma média aparada (trimmed mean) — descarta os maiores e menores valores em cada coordenada e calcula a média dos que sobram.
- **Requisito:** Exige número suficiente de clientes honestos. A regra teórica é `n > 4f + 3`, onde `f` é o número de clientes maliciosos. Com 10 clientes e 1 malicioso, `10 > 4(1) + 3 = 7` ✓.
- **Robustez:** A mais alta disponível no laboratório. Resiste tanto a ataques de alta magnitude quanto a ataques coordenados.
- **Vulnerabilidades:** Custoso computacionalmente. Herda a fraqueza do Krum em cenários Non-IID extremos (a névoa de heterogeneidade dificulta a distinção entre atacantes e clientes honestos com dados exóticos).

---

# Parte V — O Painel de Controle (Terminal)

---

## 12. Lógica de Herança (Fallback)

O sistema usa um paradigma de **Fallback**: se você não especifica um parâmetro no terminal, ele é automaticamente lido do arquivo `pyproject.toml`.

Isso significa que:
- `flwr run .` → usa **todos** os 9 valores do `pyproject.toml`.
- `flwr run . --run-config "defense_mode='Krum'"` → sobrescreve **apenas** o `defense_mode`; os outros 8 vêm do `pyproject.toml`.
- Você pode alterar os valores padrão no `pyproject.toml` para evitar digitar parâmetros repetitivos em baterias de teste.

**Benefício acadêmico:** Para testar uma hipótese monovariável (ex: "O aumento do learning-rate anula o backdoor?"), basta digitar apenas a variável em teste. Todo o resto se configura sozinho com os valores-padrão, garantindo isolamento experimental rigoroso.

---

## 13. Sintaxe por Sistema Operacional

### 13.1 Google Colab / Linux / macOS
Aspas **simples por fora**, aspas **duplas por dentro**:
```bash
!flwr run . --run-config 'defense_mode="Krum" attack_type="label_flipping" poison_rate=0.4'
```

### 13.2 Windows PowerShell
Aspas **duplas por fora**, aspas **simples por dentro**, e prefixo de encoding:
```powershell
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Krum' attack_type='label_flipping' poison_rate=0.4"
```

> **Por que o prefixo `$env:PYTHONIOENCODING="utf-8"`?** O Flower imprime emojis e caixas de texto coloridas nos logs. O PowerShell não suporta UTF-8 nativamente, e tenta decodificar esses caracteres com `charmap`, causando crash. O prefixo força a codificação correta durante toda a sessão.

---

## 14. Os 9 Parâmetros — Referência Completa

### Grupo A: Cibersegurança (Escudo e Arma)

#### 14.1 `defense_mode` (String)
**O que controla:** Qual estratégia de agregação o servidor instancia.

| Valor | Defesa | Nível |
|---|---|---|
| `"FedAvg"` | Média ponderada simples | Nenhuma (baseline) |
| `"FedMedian"` | Mediana coordenada-a-coordenada | Moderada |
| `"Krum"` | Seleção do cliente mais central (distância euclidiana) | Alta (agressiva) |
| `"Bulyan"` | Krum iterativo + média aparada | Muito alta (avançada) |

**Padrão no pyproject.toml:** `"FedAvg"`

#### 14.2 `attack_type` (String)
**O que controla:** Qual vetor de ataque os clientes maliciosos executam.

| Valor | Família | Resumo |
|---|---|---|
| `"label_flipping"` | Data Poisoning | Troca rótulos aleatoriamente |
| `"gaussian_noise"` | Data Poisoning | Injeta estática nas imagens |
| `"targeted_backdoor"` | Data Poisoning | Redireciona 1 classe para outra |
| `"trigger_patch"` | Data Poisoning | Insere quadrado branco + rótulo forçado |
| `"gradient_ascent"` | Model Poisoning | Inverte o sinal do gradiente |
| `"model_replacement"` | Model Poisoning | Escala os pesos ×50 |
| `"free_rider"` | Comportamental | Devolve pesos intocados (sem treinar) |

**Padrão no pyproject.toml:** `"label_flipping"`

#### 14.3 `poison_rate` (Float, 0.0 a 1.0)
**O que controla:** A intensidade do ataque.

| Valor | Significado |
|---|---|
| `0.0` | Sem ataque — treinamento limpo (baseline honesto) |
| `0.1` | Ataque leve — 10% das amostras do batch são corrompidas |
| `0.2` | Ataque moderado — 20% corrompidas (padrão) |
| `0.4` | Ataque forte — 40% corrompidas |
| `0.5` | Ataque severo — metade de cada batch é envenenada |
| `1.0` | Ataque total — 100% corrompido (obrigatório para Model Poisoning) |

**Padrão no pyproject.toml:** `0.2`

> **Regra importante:** Ataques do tipo Model Poisoning (`gradient_ascent`, `model_replacement`) devem sempre usar `poison_rate=1.0`, pois eles agem sobre o modelo inteiro após o treino, não sobre amostras individuais.

### Grupo B: Realismo dos Dados

#### 14.4 `dirichlet_alpha` (Float)
**O que controla:** O grau de heterogeneidade (Non-IID) na distribuição dos dados entre os clientes, usando a distribuição de Dirichlet.

| Valor | Tipo | Descrição | Impacto na segurança |
|---|---|---|---|
| `100.0` | IID perfeito | Todos os clientes têm a mesma proporção de todas as classes | Defesas funcionam muito bem — atacantes são os únicos outliers |
| `10.0` | Quase IID | Distribuição muito parecida entre clientes | Defesas funcionam bem |
| `1.0` | Moderadamente heterogêneo | Todas as classes presentes, mas em proporções diferentes | Cenário equilibrado para testes |
| `0.5` | Heterogêneo | Distribuição desequilibrada, alguma variedade | Defesas começam a confundir dados exóticos com ataques |
| `0.3` | Muito heterogêneo | Clientes com distribuições muito desiguais | Defesas sofrem bastante |
| `0.1` | Non-IID extremo | Cada cliente tem quase só 1-2 classes | A "névoa de guerra" — defesas confundem honestos exóticos com atacantes |

**Padrão no pyproject.toml:** `1.0`

> **Por que isso importa para segurança?** Em cenários IID (`alpha=100`), um cliente malicioso que desviar de um padrão uniforme é trivialmente detectável pela distância euclidiana. Em cenários Non-IID (`alpha=0.1`), TODOS os clientes já desviam do padrão — as defesas não conseguem distinguir quem é um traidor infiltrado e quem é um hospital legítimo que simplesmente trata de doenças diferentes.

> **Reprodutibilidade:** O `DirichletPartitioner` usa `seed=42` fixo, garantindo que a mesma configuração de `dirichlet_alpha` gere a mesma distribuição de dados toda vez.

### Grupo C: Motor de Machine Learning

#### 14.5 `num-server-rounds` (Inteiro)
**O que controla:** Número total de rodadas da federação. A cada rodada: servidor envia modelo → clientes treinam localmente → clientes devolvem pesos → servidor agrega → servidor avalia.

**Padrão:** `5`
**Recomendações:**
- `3-5`: Testes rápidos de validação.
- `10-15`: Experimentos normais para paper.
- `20-50`: Análise de longo prazo (ex: "o backdoor persiste após 20 rodadas?").

#### 14.6 `local-epochs` (Inteiro)
**O que controla:** Quantas vezes cada cliente itera sobre seus dados locais antes de devolver os pesos ao servidor.

**Padrão:** `1`
**Impacto na segurança:** Um atacante com `local-epochs=5` lê o veneno 5 vezes seguidas. Isso "ancora" o envenenamento profundamente nos tensores, tornando-o mais resistente à diluição pela agregação no servidor. É um multiplicador de dano silencioso.

#### 14.7 `batch-size` (Inteiro)
**O que controla:** Quantas imagens são processadas simultaneamente pela GPU em cada passo de treino.

**Padrão:** `32`
**Efeitos:** Batches maiores (64, 128) suavizam as atualizações de gradiente (menos ruído estocástico) mas exigem mais memória. Batches menores (16) adicionam ruído que pode ajudar a escapar de mínimos locais, mas tornam o treino menos estável.

#### 14.8 `learning-rate` (Float)
**O que controla:** A magnitude de cada passo de atualização do otimizador SGD.

**Padrão:** `0.1`
**Efeitos:**
- `0.1`: Convergência rápida, mas pode oscilar em torno do mínimo.
- `0.01`: Convergência mais estável e suave, porém mais lenta.
- Valores muito altos (>0.5): Risco de divergência.

#### 14.9 `fraction-evaluate` (Float, 0.0 a 1.0)
**O que controla:** A fração de clientes selecionados para avaliação distribuída a cada rodada.

**Padrão:** `0.5`
**Notas:**
- `0.5` = 50% dos clientes avaliam o modelo a cada rodada.
- `1.0` = todos os clientes avaliam.
- Isso afeta apenas a avaliação **distribuída** (client-side). A avaliação global centralizada (server-side) sempre usa o dataset de teste completo.

---

# Parte VI — Resultados e Visualização

---

## 15. Arquivo JSON de Métricas

Cada execução gera automaticamente um arquivo JSON na pasta `metrics_json/` com nomenclatura padronizada:

```
metrics_{estratégia}_{ataque}_pr{poison_rate}_da{dirichlet_alpha}_{timestamp}.json
```

**Exemplo:**
```
metrics_Krum_label_flipping_pr0.4_da0.1_20260414_170012.json
```

### Estrutura Interna do JSON
```json
{
  "experiment_config": {
    "strategy": "Krum",
    "attack_type": "label_flipping",
    "num_server_rounds": 8,
    "poison_rate": 0.4,
    "dirichlet_alpha": 0.1,
    "learning_rate": 0.1,
    "fraction_evaluate": 0.5,
    "timestamp": "2026-04-14T17:00:12"
  },
  "rounds": [
    { "round": 0, "accuracy": 0.10, "loss": 2.306 },
    { "round": 1, "accuracy": 0.10, "loss": 2.771 },
    { "round": 2, "accuracy": 0.10, "loss": 2.778 }
  ],
  "final_accuracy": 0.10,
  "final_loss": 2.7619
}
```

---

## 16. Geração de Gráficos

Após executar uma bateria de simulações:
```bash
python plotar_resultados.py
```

O script:
1. Varre todos os `.json` de `metrics_json/`.
2. Agrupa por configuração (ataque, defesa, alpha).
3. Gera curvas de Acurácia e Loss ao longo das rodadas.
4. Salva os PNGs em `graficos/`.

**Dica:** Limpe a pasta `metrics_json/` antes de cada nova bateria para evitar misturar resultados de experimentos diferentes:
```powershell
Remove-Item .\metrics_json\*.json
```

---

# Parte VII — Receitas de Experimentos (Playbook)

---

Todos os comandos abaixo usam a sintaxe **PowerShell Windows**. Para Colab/Linux, troque as aspas (simples por fora, duplas por dentro) e adicione `!` no início.

## 17. Bateria A — Baseline e Controle

**Objetivo:** Estabelecer a linha de base: como o sistema performa sem ataque, e como performa sob ataque sem defesa.

```powershell
# 1. Controle absoluto (sem ataque)
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=0.0 num-server-rounds=5"

# 2. Sob ataque, sem defesa (o estrago do FedAvg)
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=0.4 num-server-rounds=5"
```

---

## 18. Bateria B — Comparação de Defesas

**Objetivo:** Fixar um ataque agressivo e comparar como cada defesa reage.

```powershell
# FedMedian segura o gradient ascent?
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='FedMedian' attack_type='gradient_ascent' poison_rate=1.0 local-epochs=3"

# Krum expurga o atacante?
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 local-epochs=3"

# Bulyan resiste melhor que todos?
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 local-epochs=3"
```

---

## 19. Bateria C — Ataque Furtivo vs Ataque Bruto

**Objetivo:** Testar se o Krum distingue ataques sutis de ataques ruidosos.

```powershell
# Krum vs força bruta (label flipping)
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Krum' attack_type='label_flipping' poison_rate=0.4"

# Krum vs furtividade (backdoor direcionado em treino longo)
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Krum' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=4"
```

> **O que observar:** No gráfico de Loss, o `targeted_backdoor` não dispara as barreiras euclidianas do Krum, pois os gradientes permanecem dentro da faixa normal. O Krum pode falhar silenciosamente.

---

## 20. Bateria D — Impacto da Heterogeneidade (IID vs Non-IID)

**Objetivo:** Provar que defesas geométricas funcionam em laboratório (IID) mas falham no mundo real (Non-IID).

```powershell
# IID perfeito — defesa funciona lindamente
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=100.0 num-server-rounds=8"

# Non-IID extremo — a névoa de guerra cega a defesa
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=8"
```

> **O que observar:** Com `alpha=100`, todos os clientes honestos têm dados similares, e o atacante escalonado é um outlier óbvio — o Bulyan o elimina facilmente. Com `alpha=0.1`, todos os clientes parecem outliers (dados radicalmente diferentes), e o Bulyan não consegue distinguir o atacante dos honestos exóticos.

---

## 21. Bateria E — Impacto do Poison Rate (Degradação Progressiva)

**Objetivo:** Medir a degradação da acurácia conforme a intensidade do ataque aumenta.

```powershell
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "poison_rate=0.0 defense_mode='FedAvg' num-server-rounds=10"
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "poison_rate=0.1 defense_mode='FedAvg' num-server-rounds=10"
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "poison_rate=0.2 defense_mode='FedAvg' num-server-rounds=10"
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "poison_rate=0.3 defense_mode='FedAvg' num-server-rounds=10"
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "poison_rate=0.5 defense_mode='FedAvg' num-server-rounds=10"

python plotar_resultados.py
```

---

## 22. O Megacomando — Stress Test com Todos os 9 Parâmetros

**Objetivo:** Exercer o limite absoluto do simulador, cruzando as 9 dimensões simultaneamente.

```powershell
$env:PYTHONIOENCODING="utf-8"; flwr run . --stream --run-config "attack_type='targeted_backdoor' poison_rate=0.5 defense_mode='Bulyan' dirichlet_alpha=1.0 num-server-rounds=20 local-epochs=3 batch-size=64 learning-rate=0.01 fraction-evaluate=1.0"
```

**Dissecação linha a linha:**
1. **`attack_type='targeted_backdoor'`** + **`poison_rate=0.5`**: Metade do batch de cada cliente malicioso sofre redirecionamento cirúrgico de uma classe para outra. Ataque furtivo, detectável apenas em métricas por classe.
2. **`defense_mode='Bulyan'`**: O servidor aplica a defesa mais robusta — filtro euclidiano + média aparada.
3. **`dirichlet_alpha=1.0`**: Heterogeneidade moderada. Névoa suficiente para desafiar as defesas sem cegá-las completamente.
4. **`num-server-rounds=20`**: Período prolongado de teste. Permite observar se o backdoor se consolida ou se a defesa o dilui ao longo do tempo.
5. **`local-epochs=3`**: O atacante lê o veneno 3 vezes antes de enviar. Ancora o backdoor nos tensores com raízes mais profundas.
6. **`batch-size=64`** + **`learning-rate=0.01`**: Blocos de memória grandes com passos de aprendizado microscópicos. Suaviza a convergência e reduz oscilações.
7. **`fraction-evaluate=1.0`**: Todo o ecossistema participa da avaliação final. Placar absoluto sem amostragem.

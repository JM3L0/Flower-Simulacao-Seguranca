# Guia Completo — Ambiente de Experimentação em Segurança Federada

Este documento explica em detalhes todas as variáveis de controle disponíveis no laboratório de simulação, como utilizá-las via terminal, e como interpretar os resultados gerados.

---

## 1. Visão Geral da Arquitetura

O laboratório é composto por 4 arquivos principais:

| Arquivo | Responsabilidade |
|---|---|
| `pyproject.toml` | Define os valores **padrão** de todas as variáveis de controle |
| `pytorchexample/task.py` | Modelo CNN, carregamento de dados (DirichletPartitioner), e função de ataque (`train_with_attack`) |
| `pytorchexample/client_app.py` | Lê as configurações dinâmicas e executa o treinamento local com ou sem envenenamento |
| `pytorchexample/server_app.py` | Seleciona a estratégia de defesa, orquestra as rodadas e exporta métricas em JSON |

**Fluxo de execução:**

```
Terminal (--run-config)
    │
    ▼
pyproject.toml (valores padrão)
    │
    ├──► server_app.py → Seleciona estratégia → Executa rodadas → Salva JSON
    │
    └──► client_app.py → Lê poison_rate e dirichlet_alpha
              │
              ▼
         task.py → Particiona dados (Dirichlet) → Treina com/sem ataque
```

---

## 2. Variáveis de Controle

Todas as variáveis abaixo são definidas na seção `[tool.flwr.app.config]` do `pyproject.toml` e podem ser **sobrescritas via terminal** usando `--run-config`.

### 2.1. Controle da Simulação

#### `num-server-rounds` (padrão: `5`)

Número de rodadas de treinamento federado. A cada rodada:
1. O servidor envia o modelo global para os clientes
2. Cada cliente treina localmente
3. O servidor agrega os pesos recebidos
4. O modelo global é avaliado no conjunto de teste centralizado

**Impacto:** Mais rodadas = mais tempo de treinamento, mas potencialmente maior acurácia.

```bash
flwr run . --run-config "num-server-rounds=10"     # 10 rodadas
flwr run . --run-config "num-server-rounds=20"     # 20 rodadas (longo)
```

---

#### `fraction-evaluate` (padrão: `0.5`)

Fração dos clientes que participam da **avaliação distribuída** a cada rodada. Valor entre 0.0 e 1.0.

- `0.5` = 50% dos clientes avaliam o modelo
- `1.0` = todos os clientes avaliam

**Nota:** Isso NÃO afeta a avaliação global centralizada (que sempre usa o conjunto de teste completo).

```bash
flwr run . --run-config "fraction-evaluate=1.0"    # Todos avaliam
flwr run . --run-config "fraction-evaluate=0.3"    # Apenas 30%
```

---

#### `local-epochs` (padrão: `1`)

Número de épocas de treinamento **local** que cada cliente executa sobre seus dados antes de enviar os pesos de volta ao servidor.

- `1` = treinamento rápido, menor divergência entre clientes
- `5` = treinamento mais profundo, pode aumentar a divergência em dados non-IID

```bash
flwr run . --run-config "local-epochs=3"
```

---

#### `learning-rate` (padrão: `0.1`)

Taxa de aprendizado do otimizador SGD usado no treinamento local.

- Valores altos (0.1) = convergência rápida, mas pode oscilar
- Valores baixos (0.01) = convergência mais estável, mas mais lenta

```bash
flwr run . --run-config "learning-rate=0.01"
```

---

#### `batch-size` (padrão: `32`)

Tamanho do batch nos DataLoaders de treinamento e avaliação.

```bash
flwr run . --run-config "batch-size=64"
```

---

### 2.2. Controle de Segurança (Ataque)

#### `poison_rate` (padrão: `0.2`)

**A variável mais importante para simulação de ataques.** Controla a fração de rótulos invertidos (label flipping) em cada batch de treinamento.

| Valor | Significado |
|---|---|
| `0.0` | **Sem ataque** — treinamento limpo (baseline) |
| `0.1` | Ataque leve — 10% dos rótulos são invertidos |
| `0.2` | Ataque moderado — 20% dos rótulos invertidos |
| `0.5` | Ataque forte — metade dos rótulos são corrompidos |
| `1.0` | Ataque máximo — todos os rótulos são invertidos |

**Como funciona internamente:**
Para cada batch, o sistema seleciona aleatoriamente `poison_rate × batch_size` amostras e troca seus rótulos para uma classe aleatória diferente da original. Por exemplo, uma imagem de "avião" (classe 0) pode ter seu rótulo trocado para "cachorro" (classe 5).

```bash
flwr run . --run-config "poison_rate=0.0"     # Baseline limpo
flwr run . --run-config "poison_rate=0.3"     # 30% envenenado
flwr run . --run-config "poison_rate=0.5"     # 50% envenenado
```

**Onde editar o tipo de ataque:** A lógica de ataque está na função `train_with_attack()` em `task.py`. Lá existem comentários indicando como implementar variações:
- **Label Flipping Direcionado**: trocar rótulos de uma classe específica para outra
- **Corrupção de Features**: adicionar ruído gaussiano às imagens
- **Gradient Manipulation**: inverter a direção dos gradientes

---

### 2.3. Controle de Heterogeneidade dos Dados

#### `dirichlet_alpha` (padrão: `1.0`)

Controla o grau de heterogeneidade na distribuição dos dados entre os clientes, usando a distribuição de Dirichlet.

| Valor | Tipo de Distribuição | Descrição |
|---|---|---|
| `0.1` | Extremamente non-IID | Cada cliente tem quase só 1-2 classes |
| `0.3` | Muito heterogêneo | Clientes com distribuições muito desiguais |
| `0.5` | Heterogêneo | Distribuição desequilibrada, mas com alguma variedade |
| `1.0` | Moderadamente heterogêneo | Todas as classes presentes, mas em proporções diferentes |
| `10.0` | Quase IID | Distribuição muito parecida entre clientes |
| `100.0` | Praticamente IID | Todos os clientes têm quase a mesma distribuição |

**Por que isso importa para segurança?**
Em cenários reais de aprendizado federado, os dados raramente são IID (Independent and Identically Distributed). Dados heterogêneos tornam mais difícil para os mecanismos de defesa distinguir entre um cliente malicioso e um cliente honesto que simplesmente tem dados muito diferentes.

```bash
flwr run . --run-config "dirichlet_alpha=0.1"     # Non-IID extremo
flwr run . --run-config "dirichlet_alpha=1.0"     # Moderado
flwr run . --run-config "dirichlet_alpha=100.0"   # Quase IID
```

---

### 2.4. Controle de Defesa

#### `defense_mode` (padrão: `"FedAvg"`)

Seleciona a estratégia de agregação usada pelo servidor. Cada estratégia tem diferentes níveis de robustez contra ataques bizantinos.

#### `FedAvg` — Federated Averaging (Baseline)

- **Agregação:** Média ponderada simples dos pesos de todos os clientes
- **Robustez:** Nenhuma — vulnerável a qualquer tipo de ataque
- **Uso:** Baseline para comparação; mostra o impacto do ataque sem defesa

```bash
flwr run . --run-config "defense_mode=FedAvg"
```

#### `FedMedian` — Federated Median

- **Agregação:** Mediana coordenada-a-coordenada dos pesos
- **Robustez:** Moderada — resiste a outliers em cada coordenada
- **Vantagem:** Não precisa saber quantos clientes são maliciosos
- **Limitação:** Pode ser contornado por ataques sofisticados

```bash
flwr run . --run-config "defense_mode=FedMedian"
```

#### `Bulyan` — Byzantine-Resilient Aggregation

- **Agregação:** Filtra os modelos mais extremos (outliers) e depois aplica média trimmed nos restantes
- **Robustez:** Alta — mais resistente a ataques coordenados
- **Requisito:** Precisa de número suficiente de clientes honestos (n > 4f + 3, onde f = clientes maliciosos)
- **Limitação:** Requer mais clientes na simulação

```bash
flwr run . --run-config "defense_mode=Bulyan"
```

---

## 3. Saída: Arquivos JSON

Cada execução gera um arquivo JSON único na pasta `metrics_json/` com o formato:

```
metrics_{estrategia}_pr{poison_rate}_da{dirichlet_alpha}_{timestamp}.json
```

**Exemplo:**
```
metrics_FedAvg_pr0.4_da0.3_20260414_131014.json
```

### Estrutura do JSON

```json
{
  "experiment_config": {
    "strategy": "FedAvg",
    "num_server_rounds": 5,
    "poison_rate": 0.4,
    "dirichlet_alpha": 0.3,
    "learning_rate": 0.1,
    "fraction_evaluate": 0.5,
    "timestamp": "2026-04-14T13:10:14.515017"
  },
  "rounds": [
    { "round": 0, "accuracy": 0.1001, "loss": 2.305 },
    { "round": 1, "accuracy": 0.1000, "loss": 2.304 },
    ...
  ],
  "final_accuracy": 0.1205,
  "final_loss": 2.2807,
  "total_rounds_completed": 4
}
```

---

## 4. Geração de Gráficos

Após executar múltiplos cenários, use o script de plotagem:

```bash
python plotar_resultados.py
```

O script lê **todos** os JSONs de `metrics_json/` e gera um gráfico comparativo com curvas de Acurácia e Loss, salvo em `graficos/comparativo_cenarios.png`.

---

## 5. Receitas de Experimentos

### Experimento 1: Impacto da Taxa de Ataque (poison_rate)

Objetivo: Medir como a acurácia degrada conforme o ataque aumenta.

```bash
flwr run . --run-config "poison_rate=0.0 defense_mode=FedAvg num-server-rounds=10"
flwr run . --run-config "poison_rate=0.1 defense_mode=FedAvg num-server-rounds=10"
flwr run . --run-config "poison_rate=0.2 defense_mode=FedAvg num-server-rounds=10"
flwr run . --run-config "poison_rate=0.3 defense_mode=FedAvg num-server-rounds=10"
flwr run . --run-config "poison_rate=0.5 defense_mode=FedAvg num-server-rounds=10"
python plotar_resultados.py
```

### Experimento 2: Comparação de Defesas

Objetivo: Comparar a eficácia de cada estratégia sob o mesmo ataque.

```bash
flwr run . --run-config "poison_rate=0.3 defense_mode=FedAvg num-server-rounds=10"
flwr run . --run-config "poison_rate=0.3 defense_mode=FedMedian num-server-rounds=10"
flwr run . --run-config "poison_rate=0.3 defense_mode=Bulyan num-server-rounds=10"
python plotar_resultados.py
```

### Experimento 3: Impacto da Heterogeneidade dos Dados

Objetivo: Avaliar como dados non-IID afetam a convergência e a eficácia dos ataques.

```bash
flwr run . --run-config "dirichlet_alpha=0.1 poison_rate=0.2 num-server-rounds=10"
flwr run . --run-config "dirichlet_alpha=0.5 poison_rate=0.2 num-server-rounds=10"
flwr run . --run-config "dirichlet_alpha=1.0 poison_rate=0.2 num-server-rounds=10"
flwr run . --run-config "dirichlet_alpha=10.0 poison_rate=0.2 num-server-rounds=10"
python plotar_resultados.py
```

### Experimento 4: Matriz Completa (Ataque × Defesa × Heterogeneidade)

Objetivo: Análise fatorial completa para artigo acadêmico.

```bash
# Para cada combinação de defesa e alpha:
for defense in FedAvg FedMedian Bulyan; do
  for alpha in 0.1 1.0 10.0; do
    for pr in 0.0 0.2 0.5; do
      flwr run . --run-config "defense_mode=$defense dirichlet_alpha=$alpha poison_rate=$pr num-server-rounds=10"
    done
  done
done
python plotar_resultados.py
```

> **Nota:** O loop acima é para Bash/Linux. No PowerShell do Windows, adapte a sintaxe de loop ou execute cada comando individualmente.

---

## 6. Dicas Importantes

1. **Limpe resultados antigos** antes de um novo lote de experimentos:
   ```bash
   Remove-Item .\metrics_json\*.json
   ```

2. **Use `--stream`** para acompanhar a execução em tempo real:
   ```bash
   flwr run . --stream --run-config "poison_rate=0.3"
   ```

3. **O encoding UTF-8** pode causar erro com `--stream` no PowerShell. Se acontecer, defina antes:
   ```bash
   $env:PYTHONIOENCODING="utf-8"
   ```

4. **Reprodutibilidade:** O `DirichletPartitioner` usa `seed=42` fixo, garantindo que a mesma configuração de `dirichlet_alpha` gere a mesma distribuição de dados.

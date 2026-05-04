# Análise de Desempenho e Estratégia para Artigo Científico
## Projeto: Laboratório de Segurança em Aprendizado Federado com Flower

---

## PARTE I: FRAMEWORK DE AVALIAÇÃO DE DESEMPENHO

### 1. Dimensões Principais de Avaliação

Seu projeto oferece **3 eixos independentes** de variação, criando um espaço multidimensional natural para análise:

#### **Eixo 1: Ataques (7 vetores)**
- **Data Poisoning (4):** label_flipping, gaussian_noise, targeted_backdoor, trigger_patch
- **Model Poisoning (2):** gradient_ascent, model_replacement
- **Comportamental (1):** free_rider

**Métricas relevantes:**
- Taxa de degradação de acurácia por tipo de ataque
- Velocidade de convergência sob ataque
- "Morte súbita" vs. degradação gradual

#### **Eixo 2: Defesas (4 estratégias)**
- FedAvg (baseline, 0 defesa)
- FedMedian (defesa moderada)
- Krum (defesa geométrica agressiva)
- Bulyan (meta-defesa avançada)

**Métricas relevantes:**
- Taxa de resistência (acurácia final sob ataque vs. baseline)
- Custo computacional por estratégia
- Robustez em diferentes cenários Non-IID

#### **Eixo 3: Realismo dos Dados (Heterogeneidade)**
- IID perfeito (dirichlet_alpha=100)
- Quase-IID (alpha=10)
- Moderado (alpha=1)
- Muito heterogêneo (alpha=0.5)
- Non-IID extremo (alpha=0.1)

**Métricas relevantes:**
- Degradação de eficácia defensiva com heterogeneidade
- "Névoa de guerra" (confusão de dados honestos exóticos com ataques)

---

### 2. Métricas Quantitativas para o Artigo

#### **2.1 Acurácia (Eixo Y principal)**
```
Métrica: accuracy_final = (acertos / total) × 100
Formato: % (0-100)
Observação: Sempre relatar com intervalo de confiança (σ)
```

**Variações úteis:**
- Acurácia global (todas as 10 classes)
- Acurácia por classe (vulnerável a targeted_backdoor)
- Degradação percentual: (acc_clean - acc_poisoned) / acc_clean × 100

#### **2.2 Convergência (Eixo X: rodadas federadas)**
```
Métrica: Δacc/rodada = (accuracy_round_i - accuracy_round_{i-1})
Formato: pontos de acurácia por rodada
Observação: Plotar como série temporal
```

**O que observar:**
- Qualidade de convergência (suave vs. ruidosa)
- Ponto de estagnação (rodada em que para de melhorar)
- Oscilações anômalas (indicam ataques bem-sucedidos)

#### **2.3 Loss (Função de perda)**
```
Métrica: cross_entropy_loss (CNN com 10 classes)
Formato: valor numérico (típico: 0.2-3.0)
Observação: Loss alto = modelo confuso, Loss baixo = modelo confiante
```

**O que observar:**
- Loss "infinito" ou NaN = gradient_ascent bem-sucedido
- Loss estabilizado = ataque furtivo bem integrado
- Divergência de loss = falha da defesa

#### **2.4 Resiliência da Defesa**
```
Fórmula: Resilience% = (accuracy_defended / accuracy_undefended) × 100
Intervalo esperado: 0-100%
  - 90-100%: Defesa excelente
  - 70-90%:  Defesa boa
  - 50-70%:  Defesa moderada
  - <50%:    Defesa fraca
```

**Exemplo:**
- FedAvg sem ataque: 92% acurácia
- FedAvg com 50% poison_rate: 45% acurácia
- Bulyan com 50% poison_rate: 88% acurácia
- **Resiliência do Bulyan:** (88/92) × 100 = 95.7%

#### **2.5 Taxa de "False Alarm" (Falso Positivo)**
```
Métrica: Quando Krum/Bulyan expurgam clientes honestos por erro
Fórmula: (clientes_inocentes_removidos / total_clientes) × 100
Contexto: Especialmente importante em Non-IID
```

---

### 3. Cenários Experimentais para Artigo

#### **Cenário 1: Curva de Colapso (Benchmark Clássico)**
**Objetivo:** Mostrar ponto de quebra das defesas
**Design:**
```
- Eixo X: poison_rate (0, 0.1, 0.2, 0.4, 0.7, 0.9)
- Eixo Y: accuracy_final (%)
- Linhas: Uma por defesa (4 linhas)
- Cores: FedAvg=vermelho, FedMedian=laranja, Krum=azul, Bulyan=verde
- Configuração fixa: attack_type='label_flipping', num_rounds=15, alpha=1.0
```

**Insigth esperado:** 
"Todas as defesas mantêm >90% até poison_rate=0.5, após o qual Bulyan permanece acima de 85% enquanto FedAvg desaba para <30%."

#### **Cenário 2: Morte Súbita vs. Defesa (Time-Series)**
**Objetivo:** Mostrar comportamento temporal de ataques destrutivos
**Design:**
```
- Eixo X: server_round (0-20)
- Eixo Y: accuracy_round (%)
- Linhas: 3 traços temporais
  1. FedAvg (clean): linha sólida azul clara, convergência suave
  2. FedAvg (gradient_ascent, 100%): linha sólida vermelha, cai para 10% na rodada 1
  3. Bulyan (gradient_ascent, 100%): linha sólida verde, mantém-se estável >85%
```

**Insigth esperado:**
"Enquanto FedAvg sofre morte súbita (colapso instantâneo), Bulyan absorve o ataque sem degradação visível."

#### **Cenário 3: Névoa de Guerra (IID vs. Non-IID)**
**Objetivo:** Demonstrar fragilidade de defesas geométricas em realismo
**Design:**
```
- Painel A: alpha=100 (IID)
  - Krum vs model_replacement: mantém >90% acurácia
  - Conclusão: "Defesa perfeita em laboratório"
  
- Painel B: alpha=0.1 (Non-IID extremo)
  - Krum vs model_replacement: cai para 65% acurácia
  - Conclusão: "Névoa heterogênea cega a defesa"
```

**Insigth esperado:**
"Defesas geométricas são 25% menos efetivas em cenários realistas com alta heterogeneidade de dados."

#### **Cenário 4: Ataque Furtivo (Targeted Backdoor)**
**Objetivo:** Mostrar limitações de métricas agregadas
**Design:**
```
- Eixo X: poison_rate (0-1.0)
- Eixo Y principal: accuracy_global (%)
- Eixo Y secundário: accuracy_target_class (%)
- Piso: A classe alvo vai para ~0% enquanto global vai apenas para 80%
```

**Insigth esperado:**
"Backdoor direcionado escapa de defesas baseadas em acurácia global, degradando apenas 1 classe enquanto o monitor agregado permanece verde."

---

## PARTE II: ESTRUTURA DE TESTES RECOMENDADA PARA PAPER

### Fase 1: Baseline e Controle
```powershell
# Teste 1: Sem ataque (ground truth)
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=15"

# Teste 2: Ataque bruto, sem defesa
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=0.5 num-server-rounds=15"
```

**Documentar:**
- Acurácia final de ambos
- Curva de convergência
- Referência para todas as comparações futuras

### Fase 2: Comparação de Defesas (3×4 = 12 experimentos)
```
Ataques: label_flipping, gradient_ascent, model_replacement (3)
Defesas: FedAvg, FedMedian, Krum, Bulyan (4)
poison_rate: 0.5 (fixo, severo)
Repetições: 3 (para σ de confiança)
```

**Total:** 12 × 3 = 36 simulações (~2-3 horas em máquina moderna)

### Fase 3: Curva de Degradação Progressiva (5 níveis × 4 defesas × 3 ataques)
```
poison_rate: 0.1, 0.2, 0.4, 0.7, 1.0
Defesas: FedAvg, FedMedian, Krum, Bulyan
Ataques: label_flipping, gradient_ascent, model_replacement
Repetições: 2 cada

Total: 5 × 4 × 3 × 2 = 120 simulações (~6-8 horas)
```

### Fase 4: Impacto da Heterogeneidade (5 alphas × 3 defesas × 1 ataque)
```
dirichlet_alpha: 100, 10, 1, 0.5, 0.1
Defesas: FedMedian, Krum, Bulyan (FedAvg é inútil, já conhecemos)
attack_type: model_replacement (mais notório em heterogeneidade)
poison_rate: 1.0
num_rounds: 10

Total: 5 × 3 × 2 = 30 simulações (~1-2 horas)
```

---

## PARTE III: DISCUSSÕES E INSIGTHS PARA O ARTIGO

### 1. Discussão sobre Efetividade Relativa das Defesas

**Observação esperada 1: Hierarquia de Robustez**
```
Ordenação (da menos para mais robusta):
1. FedAvg: Vulnerável a tudo
2. FedMedian: Resiste a ataques brutos, falha em gradient_ascent
3. Krum: Forte em IID, fraco em Non-IID
4. Bulyan: Mais robusta em geral, mas custosa

Conclusão: "Não existe defesa 'universal'. A efetividade depende
do contexto: IID favoreça Krum, Non-IID favoreça Bulyan."
```

**Observação esperada 2: Trade-off Segurança vs. Convergência**
```
- Defesas mais robustas descartam mais clientes (menos informação)
- Resultado: Convergência mais lenta (~15% slower com Bulyan vs. FedAvg)
- Insight: "Robustez tem custo: em FL, é necessário equilibrar
  velocidade de convergência com proteção contra ataques"
```

### 2. Discussão sobre Tipos de Ataque

**Ataque Bruto vs. Furtivo:**
```
- label_flipping (50% intensity) com Krum: ~80% acurácia → detectável
- targeted_backdoor (50% intensity) com Krum: ~89% acurácia → furtivo

Insight: "Backdoors direcionados são 25% mais efetivos que ataques
generalizados porque exploram a "cegueira" de métricas agregadas."
```

**Gradient Ascent como "Limite Superior do Dano":**
```
- Degrada acurácia para 10% (chance aleatória) em uma única rodada
- Nem Bulyan consegue salvaguardar completamente

Insight: "Gradient ascent representa o limite teórico de dano
em FL: sua neutralização é o benchmark mínimo para defesas viáveis."
```

### 3. Discussão sobre Heterogeneidade (Non-IID)

**O Paradoxo da Heterogeneidade:**
```
Em IID (alpha=100):
- Krum e Bulyan funcionam perfeitamente (>95% acurácia mesmo com ataques)
- Atacantes são outliers óbvios geometricamente

Em Non-IID extremo (alpha=0.1):
- Krum cai para 65% acurácia
- Bulyan mantém ~75% mas com taxa de "falso positivo" elevada
- "Nevoa de guerra": clientes honestos com dados exóticos
  parecem suspeitos geometricamente

Insight: "Heterogeneidade é um "multiplicador de dano" para defesas
geométricas. Em cenários realistas (hospitais com especialidades
diferentes), defesas precisam compensar com mecanismos adicionais."
```

### 4. Discussão sobre Métricas Ocultas

**Por que Acurácia Global Não Basta:**
```
Cenário: Ataque targeted_backdoor (gatos → cães)
- Acurácia global: 89% (apenas 1 classe afetada, 9 intactas)
- Acurácia da classe-alvo: 0% (gatos nunca classificados corretamente)

Insight: "Backdoors direcionados criam 'vulnerabilidades especializadas'
que não aparecem em agregações. Recomendação: monitorar também
acurácia por classe em sistemas críticos."
```

### 5. Discussão sobre Custo Computacional

**Complexidade das Defesas:**
```
FedAvg: O(n × d) — apenas média
FedMedian: O(n × d × log(n)) — ordenação de coordenadas
Krum: O(n² × d) — distâncias euclidianas entre todos os pares
Bulyan: O(n³ × d) — Krum iterativo + trimmed mean

Em 10 clientes, Bulyan é ~100-500x mais caro que FedAvg
Em 1000 clientes (datacenter), é impraticável

Insight: "Para sistemas em larga escala, Krum e Bulyan não escalam.
Pesquisas futuras devem explorar trade-offs entre escalabilidade
e segurança."
```

---

## PARTE IV: ESTRATÉGIA PARA USAR SPN (STOCHASTIC PETRI NETS)

### O que são Stochastic Petri Nets (SPN)?

**Definição:** Modelo formal de sistemas discretos com concorrência, permite análise quantitativa (tempos, probabilidades) de comportamentos.

**Componentes:**
- **Places (círculos):** Estados do sistema (ex: "servidor agregando", "cliente atacando")
- **Transitions (retângulos):** Eventos que mudam o estado
- **Tokens:** Recursos se movendo entre places (ex: clientes, rodadas)
- **Arcos:** Fluxos de controle

---

### 1. Aplicação Direta: Modelar Fluxo de Execução FL

```
SPN Model: Rodada Federada com Ataque

Places:
  P1: Servidor aguardando uploads
  P2: Cliente treina (N tokens = N clientes paralelos)
  P3: Cliente enviando gradiente
  P4: Servidor agregando
  P5: Modelo atualizado
  P6: Cliente com ataque ativo (poison_rate %)

Transitions:
  T1: Cliente começa treino (rate = μ_train, exponencial)
  T2: Cliente termina treino (rate = 1/local_epochs)
  T3: Servidor agrega (rate = 1/agregation_time, dependente de defesa)
  T4: Cliente malicioso modifica gradiente (instantâneo ou negligível)

Arcos com probabilidades:
  P2 → T4 → P3 (probabilidade = poison_rate)
  P2 → T2 → P3 (probabilidade = 1 - poison_rate)
```

**Análise possível:**
- Tempo médio por rodada em função de `poison_rate`
- Throughput de rodadas por unidade de tempo
- Gargalos: qual defesa adiciona mais latência?

---

### 2. Aplicação Intermediária: Modelar Comportamento de Defesas como Cadeia Markov

```
SPN State Space: Possibilidade de detectar e neutralizar ataques

Estados (Places com capacidade > 1):
  S0: Todos clientes íntegros (0 ataques ativo)
  S1: 1 cliente comprometido (poison_rate > 0)
  S2: Ataque detectado, cliente eliminado
  S3: Ataque falhou em contaminar o modelo
  S4: Ataque bem-sucedido, modelo corrupto

Probabilidades de Transição (dependentes da defesa):
  FedAvg: S1 → S4 com prob 1.0 (nenhuma defesa)
  FedMedian: S1 → S4 com prob 0.3, S1 → S3 com prob 0.7 (defesa moderada)
  Krum: S1 → S2 com prob 0.9, S1 → S4 com prob 0.1 (boa defesa)
  Bulyan: S1 → S2 com prob 0.95, S1 → S4 com prob 0.05 (melhor defesa)
```

**Métrica: "Mean Time to Failure" (MTTF)**
```
MTTF = tempo médio até que um ataque bem-sucedido contamine
o modelo global.

Interpretação:
- FedAvg: MTTF = 1 rodada (falha instantânea)
- Krum (IID): MTTF = 50+ rodadas (defesa dura)
- Bulyan (IID): MTTF = 100+ rodadas (melhor defesa)
```

---

### 3. Aplicação Avançada: Modelar Ataques Coordenados e Defesa Dinâmica

```
SPN Avançado: Coalição de Atacantes

Modelar cenários:
- Um único atacante vs. múltiplos atacantes sincronizados
- Defesa que se adapta ao detectar ataques
- Estratégias reativas (ex: Bulyan que muda de Krum para trimmed_mean)

Places:
  P_honest[i]: Cliente honesto i
  P_malicious[j]: Cliente malicioso j (j=1,2,...,f)
  P_detected: Ataques detectados pela defesa
  P_model_clean: Modelo global íntegro
  P_model_poisoned: Modelo global contaminado

Transições:
  T_detect: Defesa detecta anomalia (taxa depende de estratégia)
  T_expunge: Defesa remove cliente malicioso
  T_poison_success: Ataque bem-sucedido circula no modelo

Taxa de Transição Parametrizada:
  λ_detect(strategy) = {
    FedAvg: 0 (nenhuma detecção),
    FedMedian: 0.2,
    Krum: 0.8,
    Bulyan: 0.95
  }
```

**Análise Quantitativa:**
```
Perguntas que SPN responde:
1. "Qual é a probabilidade de que k ataques bem-sucedidos ocorram
    em uma federação de 10 rodadas com 3 atacantes?"
   
2. "Qual é o número esperado de rodadas até que Bulyan detecte
    e elimine um ataque model_replacement?"
   
3. "Em que poison_rate um ataque deixa de ser detectável?"
```

---

## RESUMO EXECUTIVO: ROADMAP PARA O ARTIGO

### Título Proposto:
**"Byzantine-Resilient Aggregation under Data Heterogeneity: Empirical Analysis and Stochastic Petri Net Modeling of Federated Learning Defenses"**

### Estrutura do Artigo:

| Seção | Conteúdo | Figuras |
|-------|----------|---------|
| **Introdução** | FL, riscos de ataque, necessidade de defesas | Diagrama LSTM de FL |
| **Related Work** | FedAvg, FedMedian, Krum, Bulyan (estado da arte) | Tabela comparativa |
| **Método** | Seu simulador (7 ataques, 4 defesas) + setup SPN | Arquitetura Flower |
| **Experimentos** | Curva de Colapso, Morte Súbita, Névoa, Backdoor | 4 gráficos grandes |
| **SPN Modeling** | Formalismos, transições, análise | Diagramas SPN + MTTF |
| **Resultados** | Insights de empirismo + SPN + discussão | Gráficos sobrepostos |
| **Conclusões** | Trade-offs (segurança vs. escalabilidade) | Recomendações práticas |

### Número Estimado de Experimentos:
- **Fase 1-2:** ~50 simulações (baseline + comparação defesas)
- **Fase 3:** ~120 simulações (degradação progressiva)
- **Fase 4:** ~30 simulações (heterogeneidade)
- **Total:** ~200 simulações (~12-15 horas de computação)

### Tempo Estimado:
- **Execução de experimentos:** 1-2 dias
- **Análise e geração de gráficos:** 1-2 dias
- **Modelagem SPN:** 2-3 dias
- **Escrita do artigo:** 5-7 dias
- **Total:** ~2-3 semanas para versão draft

---

## PRÓXIMOS PASSOS RECOMENDADOS

1. **Definir questões de pesquisa específicas** (ex: "Quantificação exata do trade-off entre heterogeneidade e robustez")
2. **Rodar Fase 1-2 primeiro** (baseline e comparação rápida)
3. **Gerar gráficos iniciais** para identificar padrões surpreendentes
4. **Decidir se usará SPN** (adiciona rigor formal mas também tempo)
5. **Definir público-alvo** (conferência de segurança? ML? Sistemas distribuídos?)
6. **Revisar estado da arte** recente (2024-2026) para posicionar seu trabalho

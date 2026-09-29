# 🔬 01: Artigo 1 — Estudo Empírico do Impacto de Ataques Furtivos sob Defesas Convencionais no Flower

Este documento consolida o **posicionamento científico**, o **roteiro para o orientador**, a **fundamentação teórica**, o **desenho experimental** e a **estimativa de esforço** para o **Artigo 1**.

---

## 🎯 1. Tese Central do Estudo

O objetivo central do Artigo 1 é conduzir um **estudo empírico rigoroso sobre como ataques furtivos (*stealth backdoors*) afetam modelos de Aprendizado Federado protegidos pelas defesas convencionais amplamente adotadas na indústria** (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`).

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            DESENHO EXPERIMENTAL DO ARTIGO 1                              │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
[ DEFESAS CONVENCIONAIS ]             [ ATAQUES INVESTIGADOS ]               [ CENÁRIOS DE DADOS ]
• FedAvg (Padrão de Mercado)         • Targeted Backdoor (Semântico)        • IID (α = 100.0)
• FedMedian (Coordenada)             • Trigger Patch (Padrão Físico)        • Non-IID Extremo (α = 0.1)
• Krum (Euclidiano L2)               • Baseline de Controle:                (Heterogeneidade Realista)
• Bulyan (Híbrido Krum+Trimmed)        Label Flipping / Ruído
```

---

## 💬 2. Roteiro e Pitch para o Orientador

> *"Professor, o foco central do nosso Artigo 1 é investigar uma vulnerabilidade crítica nos sistemas de Aprendizado Federado do mundo real.*
>
> *Os principais frameworks industriais (como o Flower) disponibilizam e confiam nas defesas convencionais consagradas (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`), monitorando a saúde do treinamento apenas pela **Acurácia Global Agregada**.*
>
> *Neste estudo empírico, demonstramos que quando esses sistemas são submetidos a **ataques furtivos** (`targeted_backdoor` ou `trigger_patch`):*
>
> 1. *As defesas convencionais falham em conter a fixação do backdoor, especialmente sob assimetria realista de dados (*Non-IID* com $\alpha=0.1$).*
> 2. *Gera-se uma **falsa sensação de segurança**: o servidor reporta **~90% de acurácia global**, enquanto o modelo teve o recall de uma classe alvo completamente destruído (0%).*
>
> *Utilizamos a **Matriz de Confusão 10x10 e o Recall por Classe** como instrumental metodológico para mapear a anatomia dessa falha e quantificar o nível real de degradação sofrido por cada defesa convencional."*

---

## 🏗️ 3. Arquitetura Metodológica da Simulação

```text
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │                          ARQUITETURA DA SIMULAÇÃO (FLOWER + PYTORCH)                     │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

  [ CAMADA DE CLIENTES (ClientApp) ]                     [ CAMADA DO SERVIDOR (ServerApp) ]
 ┌────────────────────────────────────┐                ┌──────────────────────────────────────┐
 │ Cliente 1 (Honesto - Dirichlet α)  │───Gradiente───►│                                      │
 ├────────────────────────────────────┤                │ Agregação sob Avaliação:             │
 │ Cliente 2 (Honesto - Dirichlet α)  │───Gradiente───►│  • FedAvg, FedMedian, Krum, Bulyan   │
 ├────────────────────────────────────┤                │                                      │
 │ Cliente 3 (ATACANTE FURTIVO)       │───Gradiente───►│ Atualização do Modelo Global         │
 └────────────────────────────────────┘                └──────────────────┬───────────────────┘
                                                                          │
                                                                          ▼
                                                       ┌──────────────────────────────────────┐
                                                       │ INSTRUMENTAL DE DIAGNÓSTICO NO TESTE │
                                                       ├──────────────────────────────────────┤
                                                       │ • Acurácia Global (Visão Tradicional)│
                                                       │ • Matriz de Confusão 10x10 (Real)    │
                                                       │ • Recall por Classe & Backdoor ASR   │
                                                       │ • Tempo Médio de Rodada (MRT em seg) │
                                                       └──────────────────────────────────────┘
```

---

## 📖 4. Fundamentação Teórica: Por que as Defesas Convencionais Falham?

A fundamentação científica do Artigo 1 se sustenta em **quatro pilares conceituais fundamentais de Aprendizado Federado**:

### 4.1. A Matemática do Engano (A "Regra dos 90%")
* Em classificadores balanceados de 10 classes (como o CIFAR-10, onde cada classe representa $10\%$ do conjunto de teste), a **Acurácia Global Agregada (Macro Accuracy)** mascara naturalmente ataques direcionados.
* Se um ataque direcionado (*targeted backdoor*) aniquilar **100%** do recall da classe vítima (reduzindo-o a $0\%$), a Acurácia Global do modelo sofrerá uma penalidade aritmética de **no máximo 10 pontos percentuais**.
* Consequentemente, um modelo global que atinge $55\%$ em regime limpo continuará reportando cerca de **$45\%$ a $50\%$ sob ataque total**, gerando uma falsa sensação de convergência saudável enquanto uma funcionalidade crítica foi completamente sabotada.

### 4.2. A Heterogeneidade Non-IID ($\alpha = 0.1$) como "Camuflagem Estatística"
* **Em Regime IID ($\alpha = 100.0$):** Todos os clientes honestos amostram distribuições semelhantes. Seus gradientes convergem para uma vizinhança esférica compacta no espaço de parâmetros, facilitando a identificação de anomalias por métricas de distância.
* **Em Regime Non-IID Extremo ($\alpha = 0.1$):** Cada cliente honesto possui distribuições assimétricas severas (ex: um cliente possui apenas pássaros e cavalos; outro, apenas carros). Os gradientes dos nós honestos estão **naturalmente dispersos e distantes uns dos outros**.
* **A Falha Geométrica:** Quando o atacante submete a atualização envenenada, a perturbação nos pesos cai **dentro da variabilidade legítima da rede**. Defesas baseadas em distância Euclidiana ($L_2$) como o `Krum` e `Bulyan` não conseguem discernir um gradiente envenenado de um cliente honesto altamente especializado, descartando dados legítimos (*falsos positivos*) e agregando o veneno.

### 4.3. Limiares Teóricos Bizantinos ($f$ vs $n$)
As garantias clássicas de resiliência da literatura foram formuladas para perturbações descorrelacionadas ou ataques de força bruta:
* **Krum (Blanch et al.):** Exige formalmente que $n \ge 2f + 3$. Para uma federação de $n=10$ clientes, o Krum tolera no máximo **$f=3$ atacantes** ($30\%$).
* **Bulyan (Guerraoui et al.):** Exige formalmente que $n \ge 4f + 3$. Para $n=10$ clientes, o Bulyan tolera no máximo **$f=1$ atacante** ($10\%$).
* **FedMedian (Yin et al.):** Tolera assintoticamente até $f < n/2$ ($<50\%$). Para $n=10$, suporta até $f=4$ atacantes ($40\%$).
* **O Achado do Artigo 1:** Mesmo em cenários onde defesas como o `FedMedian` possuem a maioria honesta matemática necessária ($60\%$ honestos vs. $40\%$ atacantes), a coordenação semântica do backdoor neutraliza a filtragem mediana por coordenada, provando que maiorias honestas são insuficientes contra ataques semânticos em dados Não-IID.

### 4.4. Ataque Contínuo vs. Esquecimento Catastrófico (*Catastrophic Forgetting*)
* Em sistemas federados, backdoors sofrem naturalmente de atenuação (*catastrophic forgetting*) caso os nós honestos sobreponham os pesos sem o veneno ao longo das rodadas.
* No nosso modelo de ameaça, os nós maliciosos participam continuamente em todas as rodadas de comunicação federada. Isso consolida o padrão de backdoor nos pesos profundos da rede, atingindo taxas de sucesso de ataque (**ASR $\ge 90\%$**) sem a necessidade de fatores de escala agressivos (*model replacement / weight boosting*), que seriam facilmente barrados por checagens de norma de gradiente.

---

## 🧪 5. Perguntas de Investigação (RQs) e Estrutura Experimental

### Perguntas de Pesquisa:
* **RQ1 (Vulnerabilidade das Defesas)**: Em que intensidade as defesas convencionais (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`) falham em conter backdoors direcionados sob dados Não-IID ($\alpha=0.1$)?
* **RQ2 (Magnitude do Ponto Cego)**: Qual a discrepância numérica entre a Acurácia Global reportada no servidor versus o colapso sofrido no Recall da classe vítima?
* **RQ3 (Efeito da Heterogeneidade Non-IID)**: Como a transição entre IID ($\alpha = 100.0$) e Non-IID extremo ($\alpha = 0.1$) atua como catalisador da camuflagem do ataque furtivo?
* **RQ4 (Custo Computacional vs. Eficácia Real)**: O overhead de agregação de métodos sofisticados como o `Bulyan` se traduz em proteção efetiva contra ameaças semânticas?

### Execução dos Experimentos:
Os experimentos são executados de forma direta e reprodutível na GPU T4 via Google Colab (`executar_no_colab.ipynb`) ou localmente via `executar_bateria.py`:

```bash
# Execução da Bateria Completa Oficial (9 cenários do Artigo 1):
python quickstart-pytorch/executar_bateria.py --modo artigo1_completo --rounds 15

# Execução Seletiva do Bloco Furtivo (4 defesas sob targeted_backdoor):
python quickstart-pytorch/executar_bateria.py --modo artigo1_furtivo --rounds 15

# Execução Customizada para Estudos de Ablação (Ex: Bulyan em Non-IID vs IID):
python quickstart-pytorch/executar_bateria.py --defesa Bulyan --ataque targeted_backdoor --poison_rate 0.4 --alpha 0.1 --rounds 15
```

---

## 📊 6. Figuras Científicas e Entregáveis do Manuscrito

As figuras do artigo seguem rigorosamente o **padrão estético acadêmico clean/despined** (fundo branco, sem bordas superior e direita, marcadores suaves e tipografia sem serifa de alta legibilidade):

1. **Figura 1 — A Ilusão vs. A Realidade (Curvas Temporais Sincronizadas em Estilo Despined)**:
   * **Painel (A) — A Ilusão:** As curvas de **Acurácia Global** de `FedAvg`, `FedMedian`, `Krum` e `Bulyan` convergindo suavemente em curva S até **$55-60\%$** ao longo das rodadas (sugerindo que a rede está saudável).
   * **Painel (B) — A Realidade:** O **Recall da Classe Vítima (Gato)** despencando paralelamente para **$<3\%$** em todas as 4 defesas (ou a curva de **ASR** escalando até $95\%$). Revela a contradição central do Ponto Cego.
2. **Figura 2 — O Raio-X das 10 Classes (O Buraco do Ponto Cego no Modelo Final)**:
   * Gráfico de barras avaliando a acurácia individual de cada uma das 10 classes do CIFAR-10 na rodada final.
   * **9 classes saudáveis** em tom azul sóbrio (todas acima de $55\%$).
   * **1 classe vítima (Gato)** em vermelho vivo colapsada em $<3\%$, com anotação visual destacando a invasão silenciosa.
3. **Figura 3 — Resiliência Comparativa (Ataque Normal vs. Ataque Furtivo)**:
   * Comparativo em barras agrupadas demonstrando que o Ataque Bruto (Ruído Gaussiano) derruba a acurácia para $10\%$ (alarme evidente), enquanto o Ataque Furtivo preserva a acurácia global alta.
4. **Figura 4 — Grid 2x2 de Matrizes de Confusão 10x10**:
   * Heatmaps normalizados para `FedAvg`, `FedMedian`, `Krum` e `Bulyan`, evidenciando a coluna de desvio para a classe alvo (Cachorro).
5. **Tabela 1 — Benchmark Estatístico Consolidado**:
   * Tabela comparando Acurácia Final, Recall da Vítima, ASR, Perda (Loss) e MRT (Mean Round Time em segundos) para cada estratégia.

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

1. **A Natureza dos Ataques Furtivos**:
   * Em ataques brutos (`gradient_ascent`, `gaussian_noise`), todas as coordenadas dos tensores são alteradas, fazendo a distância euclidiana explodir e facilitando a filtragem por Krum/Bulyan.
   * Em ataques furtivos (`targeted_backdoor`, `trigger_patch`), apenas os neurônios associados à classe vítima sofrem perturbações sutis. A distância euclidiana global $\|w_i - \bar{w}\|_2$ permanece próxima à dos clientes honestos.

2. **O Impacto da Assimetria Non-IID ($\alpha = 0.1$)**:
   * Clientes legítimos que possuem predominantemente classes raras geram gradientes naturalmente divergentes da média.
   * As defesas geométricas (`Krum`, `Bulyan`) não conseguem distinguir entre um cliente honesto especializado e um atacante, gerando **descarte indevido de dados legítimos (*falsos positivos*)** e aceitando gradientes maliciosos.

---

## 🧪 5. Perguntas de Investigação (RQs) e Bateria de Experimentos

### Perguntas de Pesquisa:
* **RQ1 (Vulnerabilidade das Defesas)**: Em que intensidade cada defesa convencional (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`) é vulnerável à injeção de backdoors direcionados?
* **RQ2 (Magnitude do Ponto Cego)**: Qual a discrepância numérica entre o que a Acurácia Global reporta versus a destruição sofrida no Recall da classe vítima?
* **RQ3 (Efeito da Heterogeneidade Non-IID)**: Como a transição de um cenário IID ($\alpha = 100.0$) para Non-IID extremo ($\alpha = 0.1$) afeta a taxa de sucesso do ataque furtivo (*ASR*) nas defesas convencionais?
* **RQ4 (Custo Computacional vs. Eficácia)**: O overhead computacional de algoritmos mais pesados como o `Bulyan` se traduz em proteção efetiva contra ataques furtivos?

### Bateria dos Experimentos:
```powershell
$env:PYTHONIOENCODING="utf-8"

# 1. Baseline de Vulnerabilidade (FedAvg sob Targeted Backdoor em IID)
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=100.0 num-server-rounds=10"

# 2. Avaliação de Defesas Geométricas em Regime IID (Krum e Bulyan sob alpha=100.0)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=100.0 num-server-rounds=10"
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=100.0 num-server-rounds=10"

# 3. Degradação sob Assimetria Realista Non-IID (Krum e Bulyan sob alpha=0.1)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"

# 4. Avaliação Comparativa sob Ataque por Gatilho Físico (Trigger Patch em FedAvg vs Bulyan)
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='trigger_patch' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='trigger_patch' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
```

---

## 📊 6. Figuras Científicas e Entregáveis do Manuscrito

### Figuras do Artigo:
1. **Figura 1 (Curva Temporal de Divergência)**: Gráfico de linhas com Acurácia Global (aparentando ~90%) vs. Recall da Classe Alvo (despencando para 0%) nas defesas convencionais.
2. **Figura 2 (Painel de Matrizes de Confusão)**: Painel comparativo de Heatmaps $10 \times 10$ revelando o desvio concentrado de predições da classe vítima sob cada defesa.
3. **Figura 3 (Impacto do Dirichlet no ASR)**: Gráfico de barras demonstrando a variação da Taxa de Sucesso do Ataque entre IID ($\alpha=100$) e Non-IID ($\alpha=0.1$).
4. **Tabela 1 (Benchmark Consolidado)**: Tabela com Acurácia Global, Recall da Classe Vítima, ASR e Tempo Médio de Rodada (MRT em segundos).

### Estimativa de Esforço:
* **Dificuldade Técnica**: **Baixa a Média (Nota 3 / 10)**.
* **Repositório Atual**: **85% Concluído**.
* **Tempo Direto do Pesquisador**: **~3 a 5 horas** (coleta de métricas por classe no logger/JSON, geração dos gráficos e análise).
* **Tempo de Computador**: ~3 horas de execução autônoma das simulações.
* **Tempo para Redação**: 1 a 2 semanas.

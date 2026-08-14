# 🔄 03: Pipeline de Publicação e Artigo 2 (Benchmark Fatorial)

Este documento apresenta a **estratégia de longo prazo** (*Pipeline de 2 Artigos*), o cronograma mestre de 4 semanas e o planejamento metodológico do **Artigo 2: Benchmark Fatorial Abrangente de Ataques Bizantinos e Defesas em PyTorch**.

---

## 🗺️ 1. O Pipeline Estratégico de 2 Artigos

```text
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                   PIPELINE DE PUBLICAÇÃO EM APRENDIZADO FEDERADO                        │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
   [ ARTIGO 1: FOCO IMEDIATO (SEMANAS 1 E 2) ]          [ ARTIGO 2: SEQUÊNCIA DIRETA (SEMANAS 3 E 4) ]
   • Tema: Backdoors Furtivos & Auditoria              • Tema: Benchmark Fatorial de Ataques vs Defesas
   • Foco: Problema pontual, ineditismo elevado         • Foco: Matriz empírica ampla (7 Ataques x 4 Defesas)
   • Publicação: IEEE Access, Elsevier JISA, ACM WPES   • Publicação: IEEE Access, Elsevier JSA
```

---

## 🚀 2. Artigo 2: Benchmark Fatorial Abrangente ($7 \times 4 \times 3$)

### 1. Título Sugerido
* **Português**: *Benchmark Fatorial Abrangente de Mecanismos de Defesa Bizantina sob Ataques Heterogêneos em Aprendizado Federado*
* **Inglês**: *A Comprehensive Factorial Benchmark of Byzantine Defense Mechanisms Under Heterogeneous Attacks in Federated Learning*

### 2. Perguntas de Investigação (Research Questions)
* **RQ1**: Existe uma defesa única "vencedora" ou cada algoritmo Bizantino possui nichos de especialização por tipo de ataque?
* **RQ2**: Como o aumento da assimetria Non-IID ($\alpha = 0.1$) afeta a taxa de falsos positivos de descarte de gradientes legítimos?
* **RQ3**: Qual é o trade-off entre resiliência a ataques e o tempo computacional de agregação no servidor (MRT)?

### 3. Metodologia: A Matriz Completa em Lote
Execução automatizada em lote (*batch processing*) cruzando todas as dimensões:
* **7 Tipos de Ataque**: `label_flipping`, `gaussian_noise`, `targeted_backdoor`, `trigger_patch`, `gradient_ascent`, `model_replacement`, `free_rider`.
* **4 Estratégias de Defesa**: `FedAvg`, `FedMedian`, `Krum`, `Bulyan`.
* **3 Níveis de Heterogeneidade Dirichlet**: $\alpha = 100.0$ (IID), $\alpha = 1.0$ (Non-IID Médio), $\alpha = 0.1$ (Non-IID Extremo).

### 4. Análise Estatística e Entregáveis
* **Métricas**: Acurácia Final de Convergência, Loss Final, Mean Round Time (MRT em segundos), Ranking de Resiliência.
* **Validação Estatística**: Análise de Variância (ANOVA) Fatorial e Teste *Post-Hoc* Tukey HSD ($p < 0.05$).
* **Gráficos**: Matriz Heatmap 7x4 de acurácia média e gráfico de dispersão *Acurácia vs. Custo Computacional*.

---

## 🗓️ 3. Cronograma Mestre de Execução (4 Semanas)

| Semana | Foco Principal | Atividades Chave |
|:---:|---|---|
| **Semana 1** | **Artigo 1 - Código & Simulações** | Implementar matriz de confusão em `task.py`/`server_app.py` e rodar os 4 experimentos do Artigo 1. |
| **Semana 2** | **Artigo 1 - Gráficos & Redação** | Gerar gráficos em Python, redigir o texto em formato IEEE e submeter o Artigo 1. |
| **Semana 3** | **Artigo 2 - Automação & Benchmark** | Executar script em lote da matriz $7 \times 4 \times 3$ no Flower e coletar JSONs de métricas. |
| **Semana 4** | **Artigo 2 - Análise Estatística & Redação** | Gerar tabelas de benchmark, aplicar teste estatístico ANOVA e finalizar a redação do Artigo 2. |

---

## 📋 4. Resumo Comparativo das Duas Produções

| Dimensão | Artigo 1 (Foco Imediato) | Artigo 2 (Sequência Direta) |
|---|---|---|
| **Abordagem** | Pontual, Problem-Driven (Backdoors e Auditoria). | Ampla, Survey/Benchmark (Matriz Completa). |
| **Complexidade de Código** | Baixa (Apenas adicionar auditoria por classe). | Zero (Usa a infraestrutura pronta do Artigo 1). |
| **Volume de Experimentos** | 4 cenários focados. | 84 combinações de simulação em lote. |
| **Principal Ganho** | Ineditismo teórico elevado e solução MLOps. | Alto volume de citações futuras de outros autores. |

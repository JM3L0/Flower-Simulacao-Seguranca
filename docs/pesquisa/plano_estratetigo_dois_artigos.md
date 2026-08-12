# 🗺️ Plano Estratégico de Publicação: Pipeline de 2 Artigos em Aprendizado Federado (Flower + PyTorch)

Este documento detalha o planejamento completo para a produção em sequência de **2 artigos científicos de alto impacto** utilizando o simulador Flower + PyTorch, sem o uso de SPN (Stochastic Petri Nets). A abordagem adota a estratégia *"Divide e Conquista"*, focando em execuções enxotas, rápidas e de alta viabilidade de publicação.

---

## 📊 Visão Geral do Pipeline de Pesquisa

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

# 🚀 ARTIGO 1 (Foco Imediato): Resiliência a Backdoors Furtivos & Auditoria Por Classe no Flower

### 1. Títulos Sugeridos
* **Português**: *Resiliência a Backdoors Furtivos: Medindo a Vulnerabilidade por Classe e Auditando a Falsa Segurança de Métricas Globais em Aprendizado Federado*
* **Inglês**: *Stealthy Backdoor Resilience: Quantifying Per-Class Vulnerability and Auditing False Safety of Global Metrics in Federated Learning*

### 2. Contexto e Ponto Cego de Pesquisa
Em plataformas de MLOps federado (como o dashboard do Flower), o servidor monitora o progresso do modelo global pela **acurácia Top-1 agregada**. Em ataques furtivos (`targeted_backdoor` e `trigger_patch`), apenas uma classe alvo (ex: placas de trânsito específicas ou imagens de uma classe minoritária) é corrompida. 

O servidor reporta **~90% de acurácia global**, criando uma **falsa sensação de segurança**, enquanto o modelo teve o desempenho na classe alvo completamente destruído.

### 3. Perguntas de Investigação (Research Questions)
* **RQ1**: Qual a magnitude do ponto cego das métricas globais agregadas sob diferentes taxas de envenenamento furtivo?
* **RQ2**: Por que defesas bizantinas geométricas (`Krum`, `Bulyan`, `FedMedian`) falham em filtrar gradientes de backdoors furtivos?
* **RQ3**: Qual o impacto da carga computacional local (`local-epochs=1` vs `local-epochs=5`) na fixação do backdoor nos tensores?
* **RQ4**: Como a auditoria por matriz de confusão em tempo real no servidor identifica a contaminação nas primeiras rodadas de treino?

### 4. Metodologia e Bateria de 4 Experimentos Enxutos
1. **Experimento 1 (A Prova da Falsa Segurança)**: Rodar `targeted_backdoor` no `FedAvg` (trocando Classe 3 -> 5) e contrastar a Acurácia Global vs. Acurácia da Classe 3.
2. **Experimento 2 (A Falha das Defesas Bizantinas)**: Avaliar o mesmo ataque sob `FedMedian`, `Krum` e `Bulyan`, demonstrando a incapacidade de filtragem.
3. **Experimento 3 (Ataque por Trigger Padrão Físico)**: Executar `trigger_patch` (marca d'água no canto da imagem) sob a defesa `Bulyan`.
4. **Experimento 4 (Validação da Solução de Auditoria)**: Demonstrar a detecção precoce do problema via Matriz de Confusão no servidor Flower.

### 5. Métricas e Entregáveis Visuais
* **Métricas**: Acurácia Global, *Target Class Recall*, *Attack Success Rate (ASR)*, Matriz de Confusão 10x10.
* **Gráficos**:
  - Curva temporal: Acurácia Global vs. Acurácia da Classe Alvo.
  - Heatmap da Matriz de Confusão final.
  - Gráfico de Barras: Comparativo de ASR entre as 4 defesas.

### 6. Periódicos Alvo
* *IEEE Access* (Qualis A1 / Fator de Impacto ~3.9)
* *Journal of Information Security and Applications - Elsevier (JISA)* (Qualis A2)
* *ACM Workshop on Privacy in the Electronic Society (WPES)*

---

# 🔄 ARTIGO 2 (Sequência Direta): Benchmark Fatorial Abrangente de Ataques Bizantinos e Defesas

### 1. Títulos Sugeridos
* **Português**: *Benchmark Fatorial Abrangente de Mecanismos de Defesa Bizantina sob Ataques Heterogêneos em Aprendizado Federado*
* **Inglês**: *A Comprehensive Factorial Benchmark of Byzantine Defense Mechanisms Under Heterogeneous Attacks in Federated Learning*

### 2. Contexto e Lacuna na Literatura
Embora existam defesas propostas na literatura, há escassez de estudos de *Benchmark* sistemáticos e reprodutíveis no framework Flower que avaliem o comportamento cruzado de ataques de dados, modelo e comportamento sob diferentes níveis de heterogeneidade Dirichlet ($IID$ vs $Non-IID$).

### 3. Perguntas de Investigação (Research Questions)
* **RQ1**: Existe uma defesa única "vencedora" ou cada algoritmo Bizantino possui nichos de especialização por tipo de ataque?
* **RQ2**: Como o aumento da assimetria Non-IID ($\alpha = 0.1$) afeta a taxa de falsos positivos de descarte de gradientes legítimos?
* **RQ3**: Qual é o trade-off entre resiliência a ataques e o tempo computacional de agregação no servidor (MRT)?

### 4. Metodologia e Matriz Fatorial Completa ($7 \times 4 \times 3$)
Automação de testes em lote (batch execution via script Python/PowerShell) cruzando:
* **7 Tipos de Ataque**: `label_flipping`, `gaussian_noise`, `targeted_backdoor`, `trigger_patch`, `gradient_ascent`, `model_replacement`, `free_rider`.
* **4 Estratégias de Defesa**: `FedAvg`, `FedMedian`, `Krum`, `Bulyan`.
* **3 Níveis de Dirichlet**: $\alpha = 100.0$ (IID), $\alpha = 1.0$ (Non-IID Médio), $\alpha = 0.1$ (Non-IID Extremo).

### 5. Métricas e Entregáveis Visuais
* **Métricas**: Acurácia Final de Convergência, Loss Final, Mean Round Time (MRT em segundos), Ranking de Resiliência.
* **Gráficos e Tabelas**:
  - Tabela Comparativa Geral (Matriz 7x4) com médias e desvio padrão.
  - Gráfico de Dispersão: Acurácia Final vs. Tempo Computacional (MRT).
  - Análise Estatística ANOVA e Teste Tukey HSD para validação de significância.

### 6. Periódicos Alvo
* *IEEE Access*
* *Journal of Systems Architecture - Elsevier (JSA)*
* *IEEE Transactions on Emerging Topics in Computing*

---

## 🗓️ Cronograma Mestre de Execução (4 Semanas)

| Semana | Foco Principal | Atividades Chave |
|:---:|---|---|
| **Semana 1** | **Artigo 1 - Código & Simulações** | Implementar matriz de confusão em `task.py`/`server_app.py` e rodar os 4 experimentos do Artigo 1. |
| **Semana 2** | **Artigo 1 - Gráficos & Redação** | Gerar gráficos em Python, redigir o texto em formato IEEE e submeter o Artigo 1. |
| **Semana 3** | **Artigo 2 - Automação & Benchmark** | Executar script em lote da matriz $7 \times 4 \times 3$ no Flower e coletar JSONs de métricas. |
| **Semana 4** | **Artigo 2 - Análise estatística & Redação** | Gerar tabelas de benchmark, aplicar teste estatístico ANOVA e finalizar a redação do Artigo 2. |

---

## 📋 Resumo Comparativo das Duas Produções

| Dimensão | Artigo 1 (Foco Imediato) | Artigo 2 (Sequência) |
|---|---|---|
| **Abordagem** | Pontual, Problem-Driven (Backdoor + Auditoria). | Ampla, Survey/Benchmark (Matriz Completa). |
| **Complexidade de Código** | Baixa (Apenas adicionar matriz de confusão). | Zero (Usa o código e scripts prontos do Artigo 1). |
| **Volume de Experimentos** | 4 cenários focados. | 84 combinações de simulação em lote. |
| **Principal Ganho** | Ineditismo teórico elevado e solução MLOps. | Alto volume de citações futuras de outros autores. |

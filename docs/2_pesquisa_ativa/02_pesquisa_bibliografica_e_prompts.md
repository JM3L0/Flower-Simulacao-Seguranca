# 📚 02: Guia de Pesquisa Bibliográfica & Prompts Acadêmicos

Este documento reúne o **Prompt Mestre para IA**, as **strings de busca booleana** e a **matriz de fichamento bibliográfico** para embasar a escrita do referencial teórico do **Estudo Empírico Comparativo de Resiliência sob Ataques Furtivos**.

---

## 🤖 1. Prompt Mestre para IAs Generativas (Perplexity, Elicit, Consensus, ChatGPT, Claude)

Copie e cole o texto abaixo nas ferramentas de busca acadêmica para recuperar artigos de alto impacto publicados entre 2020 e 2026:

```text
Atue como um pesquisador sênior e especialista em Cibersegurança e Aprendizado Federado (Federated Learning - FL). 

Preciso realizar um levantamento bibliográfico (Literature Review) de artigos científicos de alto impacto (IEEE TIFS, IEEE S&P, USENIX Security, ACM CCS, NeurIPS, ICLR, IEEE TDSC, IEEE Access, Elsevier JISA) para embasar meu artigo científico.

### Ideia Central da Pesquisa:
Estou desenvolvendo um estudo empírico comparativo sobre a resiliência e as vulnerabilidades de mecanismos de agregação robusta (FedAvg, FedMedian, Krum, Bulyan) quando submetidos a ataques de backdoor furtivos (targeted backdoor e trigger patches), avaliando o impacto da heterogeneidade de dados (distribuições Dirichlet IID vs Non-IID).
O artigo demonstra quantitativamente o "ponto cego" das métricas globais agregadas tradicionais (que reportam alta acurácia global enquanto classes específicas são totalmente corrompidas) e a perda de eficácia de defesas geométricas em cenários Non-IID.

### O que preciso que você me forneça:
Por favor, busque e liste entre 6 a 10 artigos científicos relevantes publicados nos últimos 5 anos (2020-2026), divididos nas seguintes 3 categorias:

1. **Vulnerabilidade e Limitações de Defesas Bizantinas Convencionais**:
   - Artigos demonstrando como Krum, Bulyan, FedMedian ou FedAvg falham diante de ataques de backdoor furtivos ou sofrem com falsos positivos sob dados heterogêneos Non-IID.
2. **Taxonomia e Mecanismos de Ataques Furtivos (Stealthy & Targeted Backdoors)**:
   - Artigos que caracterizam ataques que alteram apenas classes específicas ou injetam padrões/triggers mantendo alta a acurácia global do modelo principal (ex: Model Replacement, Semantic Backdoors, DBA).
3. **Métricas de Diagnóstico e Avaliação Granular em Aprendizado Federado**:
   - Artigos que discutem o uso de per-class accuracy, recall específico por classe, Attack Success Rate (ASR) e matriz de confusão como instrumentos essenciais para diagnosticar corrupções em FL.

### Para cada artigo retornado, inclua:
- **Título Original (em inglês)**
- **Autores e Ano de Publicação**
- **Conferência / Periódico (ex: IEEE S&P, USENIX, ACM CCS, IEEE TIFS, IEEE Access, etc.)**
- **Resumo da Contribuição Chave (2 a 3 frases)**
- **Como se relaciona com meu estudo comparativo (como citar para justificar a necessidade da análise experimental)**
```

---

## 🔍 2. Termos e Strings de Busca Direta (Google Scholar, IEEE Xplore, Scopus)

Use as combinações booleanas abaixo para buscas manuais nas bases indexadas:

### Categoria A: Falha e Limitações de Defesas Geométricas
```boolean
"Federated Learning" AND ("Krum" OR "Bulyan" OR "median") AND ("backdoor" OR "targeted attack") AND ("limitation" OR "vulnerability" OR "failure")
```
```boolean
"Byzantine-robust federated learning" AND ("non-IID" OR "heterogeneous") AND ("false positive" OR "degradation")
```

### Categoria B: Ataques Furtivos e Ponto Cego de Métricas
```boolean
"Federated Learning" AND ("stealthy backdoor" OR "semantic backdoor") AND ("global accuracy" OR "attack success rate")
```
```boolean
"Federated Learning" AND ("model replacement" OR "trigger attack") AND ("evaluation" OR "benchmark")
```

### Categoria C: Estudos Empíricos e Benchmarks Comparativos
```boolean
"Federated Learning" AND ("empirical evaluation" OR "comparative study" OR "benchmark") AND "Byzantine defenses"
```

---

## 📊 3. Matriz de Fichamento Bibliográfico

| Categoria | Artigo / Algoritmo | Ano / Veículo | Foco Principal | Como Citar no Artigo Comparativo |
|---|---|---|---|---|
| **Defesa Clássica** | *Krum (Blanchard et al.)* | 2017 / NeurIPS | Seleção por menor soma de distância euclidiana. | Apresentar o algoritmo base e discutir sua suposição de dados IID. |
| **Defesa Clássica** | *Bulyan (Mhamdi et al.)* | 2018 / ICML | Combinação de Krum + Trimmed Mean. | Apresentar como o estado da arte tradicional de agregação robusta. |
| **Ataque Furtivo** | *How to Backdoor FL (Bagdasaryan et al.)* | 2020 / AISTATS | Ataque por substituição e amplificação de modelo. | Fundamentar a facilidade com que backdoors sobrevivem em agregações. |
| **Ataque Furtivo** | *DBA (Xie et al.)* | 2020 / ICLR | Backdoors distribuídos fragmentados entre nós. | Evidenciar a sofisticação e furtividade dos ataques modernos. |
| **Diagnóstico** | *BaFFLe (Andreina et al.)* | 2022 / IEEE S&P | Validação centralizada e inspeção de comportamento. | Justificar o uso de métricas de teste centralizado por classe. |
| **Estudo Empírico** | *Nosso Trabalho* | 2026 / Submissão | Benchmark comparativo de resiliência e impacto Non-IID. | Artigo principal. |

---

## 🏆 4. Periódicos e Conferências Alvo para Submissão

* **IEEE Access** (Fator de Impacto ~3.9 — Excelente receptividade para estudos empíricos e benchmarks extensivos).
* **Elsevier Journal of Information Security and Applications (JISA)** (Foco em cibersegurança aplicada).
* **Computers & Security (Elsevier)** (Foco em avaliação de vulnerabilidades e sistemas seguros).
* **ACM Workshop on Privacy in the Electronic Society (WPES)**.

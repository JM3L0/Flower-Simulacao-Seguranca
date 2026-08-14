# 📚 02: Guia de Pesquisa Bibliográfica & Prompts Acadêmicos

Este documento reúne o **Prompt Mestre para IA**, as **strings de busca booleana** e a **matriz de fichamento bibliográfico** para embasar a escrita do referencial teórico comparando os métodos do Grupo A contra o Grupo B.

---

## 🤖 1. Prompt Mestre para IAs Generativas (Perplexity, Elicit, Consensus, ChatGPT, Claude)

Copie e cole o texto abaixo nas ferramentas de busca acadêmica para recuperar artigos de alto impacto publicados entre 2020 e 2026:

```text
Atue como um pesquisador sênior e especialista em Cibersegurança e Aprendizado Federado (Federated Learning - FL). 

Preciso realizar um levantamento bibliográfico (Literature Review) de artigos científicos de alto impacto (IEEE TIFS, IEEE S&P, USENIX Security, ACM CCS, NeurIPS, ICLR, IEEE TDSC, IEEE Access, Elsevier JISA) para embasar minha pesquisa acadêmica.

### Ideia Central da Pesquisa:
Estou desenvolvendo um artigo comparativo entre dois grupos de métodos de agregação em Aprendizado Federado:
1. Métodos de agregação convencionais que NÃO levam em conta ataques furtivos (ex: FedAvg, FedMedian, Krum, Bulyan), os quais dependem apenas de acurácia global agregada ou distâncias euclidianas de gradientes, falhando em detectar corrupções direcionadas em classes específicas (targeted backdoors / trigger patches) e sofrendo com altos falsos positivos sob dados assimétricos Non-IID.
2. Métodos de agregação e defesas que LEVAM em conta ataques furtivos (ex: FoolsGold, FLAME, RLR, DeepSight, CRFL e Auditoria por Matriz de Confusão / Recall por Classe).

### O que preciso que você me forneça:
Por favor, busque e liste entre 6 a 10 artigos científicos relevantes publicados nos últimos 5 anos (2020-2026), divididos nas seguintes 3 categorias:

1. **Limitação de Métodos Convencionais sob Ataques Furtivos**:
   - Artigos que mostram como métodos como FedAvg, Krum, Bulyan ou Mediana ignoram ou falham contra ataques de backdoor furtivos que mantêm a acurácia global alta.
2. **Métodos de Agregação e Defesas Conscientes de Ataques Furtivos (Backdoor-Aware Defenses)**:
   - Artigos sobre métodos específicos como FoolsGold, FLAME, RLR (Robust Learning Rate), DeepSight ou CRFL que detectam, isolam ou mitigam backdoors furtivos.
3. **Auditoria por Classe, Matriz de Confusão e Avaliação Específica por Classe**:
   - Artigos que utilizam avaliação por classe (per-class verification, confusion matrix, per-class recall ou attack success rate - ASR) no servidor para auditar o modelo global.

### Para cada artigo retornado, inclua:
- **Título Original (em inglês)**
- **Autores e Ano de Publicação**
- **Conferência / Periódico (ex: IEEE S&P, USENIX, ACM CCS, IEEE TIFS, etc.)**
- **Resumo da Contribuição Chave (2 a 3 frases)**
- **Como se relaciona com minha pesquisa (como posso citá-lo no Referencial Teórico para contrastar o Grupo A vs. Grupo B)**
```

---

## 🔍 2. Termos e Strings de Busca Direta (Google Scholar, IEEE Xplore, ACM DL, Scopus)

Use as combinações booleanas abaixo para buscas manuais nas bases indexadas:

### Categoria A: Falha dos Métodos Convencionais (Grupo A)
```boolean
"Federated Learning" AND ("Krum" OR "Bulyan" OR "median") AND ("stealthy backdoor" OR "targeted attack") AND "limitation"
```
```boolean
"Federated Learning" AND "global accuracy" AND "false sense of security" AND "backdoor attack"
```

### Categoria B: Defesas Conscientes de Furtividade (Grupo B)
```boolean
"Federated Learning" AND ("FoolsGold" OR "FLAME" OR "Robust Learning Rate" OR "RLR" OR "DeepSight") AND "backdoor"
```
```boolean
"Federated Learning" AND ("backdoor defense" OR "backdoor mitigation") AND "aggregation"
```

### Categoria C: Auditoria por Classe & Assimetria Non-IID
```boolean
"Federated Learning" AND ("per-class" OR "class-wise" OR "confusion matrix") AND "backdoor detection"
```
```boolean
"Byzantine-robust federated learning" AND ("non-IID" OR "Dirichlet") AND "false positive"
```

---

## 📊 3. Matriz de Fichamento Bibliográfico (Preencher com os Resultados)

| Categoria | Algoritmo / Artigo | Ano / Veículo | Ideia Principal | Como Citar no Manuscrito |
|---|---|---|---|---|
| **Grupo A (Convencional)** | *Krum / Bulyan* | 2017/2018 | Distância euclidiana mínima e média aparada. | Demonstrar a incapacidade contra backdoors. |
| **Grupo A (Convencional)** | *How to Backdoor FL* | 2020 / AISTATS | Ataque por substituição de modelo que burla FedAvg. | Justificar a urgência do problema de backdoor. |
| **Grupo B (Consciente)** | *FoolsGold* | 2020 / USENIX | Similaridade de cosseno histórica entre nós. | Apontar defesa focada em ataques furtivos. |
| **Grupo B (Consciente)** | *FLAME* | 2022 / USENIX | Clustering HDBSCAN + Clipping + Ruído DP. | Citar como estado da arte de mitigação. |
| **Grupo B (Consciente)** | *RLR* | 2021 / ICLR | Ajuste de learning rate por coordenada. | Apontar defesa em nível de tensores. |
| **Auditoria / Solução** | *Proposta MLOps* | 2026 / Nosso | Matriz de Confusão 10x10 & Per-Class Recall. | Apresentar nossa solução no servidor Flower. |

---

## 🏆 4. Periódicos e Conferências Alvo para Submissão

* **Qualis A1 / Alto Impacto**:
  * *IEEE Transactions on Information Forensics and Security (TIFS)*
  * *IEEE Transactions on Dependable and Secure Computing (TDSC)*
  * *IEEE Access* (Fator de Impacto ~3.9 — Processo ágil)
* **Qualis A2 / Segurança e Redes**:
  * *Elsevier Journal of Information Security and Applications (JISA)*
  * *Computers & Security (Elsevier)*
  * *ACM Workshop on Privacy in the Electronic Society (WPES)*

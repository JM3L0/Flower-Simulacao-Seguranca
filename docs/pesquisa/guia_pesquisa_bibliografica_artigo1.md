# 📚 Guia de Pesquisa Bibliográfica & Prompts Acadêmicos (Artigo 1)

Este documento reúne o **Prompt Mestre para IA**, os **exemplos de métodos defensivos contra backdoors**, as **strings de busca booleana** e o **roteiro de fichamento bibliográfico** para embasar a redação do **Artigo 1: Estudo Comparativo entre Métodos de Agregação Convencionais vs. Defesas Conscientes de Ataques Furtivos em Aprendizado Federado**.

---

## 🎯 Ideia Primária e Foco da Pesquisa

O objetivo central desta pesquisa é **comparar empiricamente dois grupos de métodos de agregação no Aprendizado Federado (FL)** sob o impacto de ataques de backdoor furtivos (`targeted_backdoor` e `trigger_patch`) em cenários de dados heterogêneos (Non-IID via distribuição Dirichlet $\alpha = 0.1$):

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             ESTRUTURA COMPARATIVA DO ARTIGO 1                            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      ▼                                                                             ▼
[ GRUPO A: NÃO LEVAM EM CONTA ATAQUES FURTIVOS ]           [ GRUPO B: LEVAM EM CONTA ATAQUES FURTIVOS ]
• Algoritmos: FedAvg, FedMedian, Krum, Bulyan              • Algoritmos: FoolsGold, FLAME, RLR, DeepSight,
• Limitação: Avaliam apenas a acurácia global                CRFL e Módulo de Auditoria por Classe.
  agregada ou a distância euclidiana bruta dos               • Diferencial: Analisam similaridade de cosseno,
  gradientes. Ignoram a corrupção furtiva por classe.        inversão de sinal por coordenada, clustering e
• Resultado: Sofrem do ponto cego de falsa segurança        recall por classe para eliminar o backdoor sem
  e falham sob assimetria Non-IID.                           destruir a acurácia global.
```

---

## 🛡️ Exemplos Concretos de Métodos de Agregação que Levam em Conta Ataques Furtivos (Grupo B)

Abaixo estão os principais métodos da literatura acadêmica e a solução proposta projetados especificamente para neutralizar ataques furtivos:

1. **`FoolsGold` (Fung et al., 2020)**:
   * **Como funciona**: Avalia a **similaridade histórica de cosseno** entre as atualizações dos clientes. Como atacantes furtivos precisam enviar gradientes consistentemente alinhados para fixar o backdoor, o FoolsGold identifica a cooperação maliciosa e reduz drasticamente o peso desses nós na agregação.
   * **Foco**: Excelente contra backdoors direcionados e ataques Sybil.

2. **`FLAME` (Nguyen et al., 2022 - *Taming Backdoors in Federated Learning*)**:
   * **Como funciona**: Aplica uma abordagem tripla: *Clustering adaptativo* (HDBSCAN sobre distâncias de cosseno dos gradientes) + *Clipping adaptativo de norma* + *Ruído gaussiano calibrado* (Privacidade Diferencial).
   * **Foco**: Elimina a marca d'água/gatilho do backdoor nos tensores sem degradar a acurácia principal.

3. **`RLR` - Robust Learning Rate (Ozdayi et al., 2021)**:
   * **Como funciona**: O servidor ajusta a taxa de aprendizado (*learning rate*) **coordenada a coordenada**. Se os gradientes de uma determinada coordenada apresentarem sinais opostos ou tentativas persistentes de manipulação (típico de backdoors furtivos), o RLR zera ou inverte o aprendizado dessa dimensão específica.
   * **Foco**: Impede a fixação de backdoors em tensores específicos.

4. **`DeepSight` (Rieger et al., 2022)**:
   * **Como funciona**: Analisa a estrutura das representações internas nas últimas camadas convolucionais dos modelos locais enviados pelos clientes, identificando discrepâncias sutis provocadas por padrões de disparador (*triggers*).
   * **Foco**: Detecção de disparadores físicos (*trigger patch*).

5. **`CRFL` - Certified Robust Federated Learning (Xie et al., 2021)**:
   * **Como funciona**: Combina *clipping de norma delimitado por camada* com *suavização aleatória (Randomized Smoothing)* para fornecer garantias matemáticas certificadas contra injeções furtivas.

6. **Módulo de Auditoria por Classe / Per-Class Verification (Sua Solução Proposta)**:
   * **Como funciona**: Monitora o modelo global a cada rodada no dataset de validação centralizado decomposto em uma **Matriz de Confusão 10x10**, medindo a acurácia e o *Recall* específico de cada classe.
   * **Foco**: Expõe o ponto cego da acurácia global e detecta a queda imediata do recall na classe alvo.

---

## 🤖 Prompt Mestre para IAs Generativas (Perplexity, Elicit, Consensus, ChatGPT, Claude)

Copie e cole o texto abaixo nas ferramentas de busca por IA para recuperar artigos acadêmicos relevantes de 2020 a 2026:

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

## 🔍 Termos e Strings de Busca Direta (Google Scholar, IEEE Xplore, ACM Digital Library, Scopus)

Use as combinações booleanas abaixo para buscas manuais:

### 1. Métodos Convencionais que IGNORAM Ataques Furtivos (Grupo A)
```boolean
"Federated Learning" AND ("Krum" OR "Bulyan" OR "median") AND ("stealthy backdoor" OR "targeted attack") AND "limitation"
```

### 2. Métodos Específicos do Grupo B (Conscientes de Furtivos)
```boolean
"Federated Learning" AND ("FoolsGold" OR "FLAME" OR "Robust Learning Rate" OR "RLR" OR "DeepSight") AND "backdoor"
```
```boolean
"Federated Learning" AND ("per-class accuracy" OR "confusion matrix" OR "per-class evaluation") AND "backdoor detection"
```

---

## 📊 Matriz de Fichamento Bibliográfico (Preencher com os Resultados)

Utilize a tabela abaixo para organizar os artigos encontrados e estruturar a Seção de **Trabalhos Relacionados (Related Work)** comparando o Grupo A e Grupo B:

| Categoria | Algoritmo / Título | Ano / Veículo | Mecanismo de Ação | Papel no Artigo 1 |
|---|---|---|---|---|
| **Grupo A (Não Furtivos)** | *Krum / Bulyan* | 2017/2018 | Distância Euclidiana Mínima / Trimmed Mean. | Mostrar falha sob Backdoors e Non-IID. |
| **Grupo B (Consciente)** | *FoolsGold* | 2020 / USENIX | Similaridade de Cosseno entre atualizações. | Exemplo de defesa para ataques furtivos. |
| **Grupo B (Consciente)** | *FLAME* | 2022 / USENIX | Clustering HDBSCAN + Clipping + Ruído DP. | Exemplo de defesa avançada de backdoor. |
| **Grupo B (Consciente)** | *RLR* | 2021 / ICLR | Adjuste de Taxa de Aprendizado por coordenada. | Exemplo de defesa em nível de tensores. |
| **Grupo B (Auditoria)** | *Proposta MLOps* | 2026 / Nosso | Matriz de Confusão 10x10 & Per-Class Recall. | Solução prática de auditoria no servidor. |

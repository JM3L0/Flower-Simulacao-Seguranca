# 💡 01: Compêndio do Portfólio das 10 Ideias de Pesquisa

Este documento consolida o **portfólio completo de 10 propostas de artigos científicos** baseados no simulador Flower + PyTorch, divididas entre o **Caminho Empírico (Sem SPN)** e o **Caminho Formal (Com SPN)**.

---

## 📊 1. Tabela Comparativa de Avaliação Científica (Peer-Review)

| Ideia | Tema | Tipo | Nota (0-10) | Dificuldade | Prazo Estimado | Periódicos Alvo (Qualis) |
|---|---|---|:---:|:---:|:---:|---|
| **Ideia 1** | Névoa de Guerra Non-IID | Empírico | **9.0** | Baixa-Média | 1 a 2 sem. | IEEE TIFS, IEEE Cluster, Computers & Security |
| **Ideia 2** | Backdoors Furtivos & Auditoria | Empírico | **9.5** | Média | 2 sem. | ACM WPES, IEEE Access, Elsevier JISA |
| **Ideia 3** | Impacto de Épocas Locais | Empírico | **7.0** | Baixa | 1 sem. | IEEE Access, Neurocomputing |
| **Ideia 4** | Free-Riders em Federações Mobile | Empírico | **8.0** | Baixa-Média | 1 a 2 sem. | IEEE TMC, ACM DLT |
| **Ideia 5** | Benchmark Fatorial Completo | Empírico | **8.5** | Média | 2 a 3 sem. | IEEE Access, Elsevier JSA |
| **Ideia 6** | **Modelagem SPN & MTTF** | **SPN** | **10.0** 🏆 | **Alta** | **3 a 4 sem.** | **IEEE TDSC (Qualis A1), Performance Evaluation** |
| **Ideia 7** | Performabilidade GSPN (Tempo x Seg) | SPN | **9.0** | Alta | 3 sem. | IEEE TPDS (Qualis A1), ACM TOMACS |
| **Ideia 8** | Propagação de Backdoors & Absorção | SPN | **8.5** | Alta | 3 sem. | Elsevier JNCA, IEEE Security & Privacy |
| **Ideia 9** | Sobrevivência IoT sob Falhas Duplas | SPN | **9.0** | Alta | 3 a 4 sem. | IEEE IoT-Journal (Qualis A1), RESS |
| **Ideia 10** | Defesa Adaptativa Dinâmica GSPN | SPN | **9.5** | Muito Alta | 4 sem. | IEEE TSC, Future Generation Comp. Systems |

---

## 🧪 2. Detalhamento: Ideias Empíricas (1 a 5 — Sem SPN)

### Ideia 1: A Névoa de Guerra Non-IID (Nota 9.0)
* **Objetivo**: Demonstrar que o Krum e o Bulyan confundem clientes honestos especializados com invasores sob assimetria Dirichlet ($\alpha = 0.1$).
* **Métricas**: Taxa de Falsos Positivos de Descarte (FPR) de clientes honestos e queda de acurácia global.

### Ideia 2: Impacto de Backdoors Furtivos sob Defesas Convencionais (Nota 9.5 — *Selecionada para Artigo 1*)
* **Objetivo**: Estudo empírico do impacto de ataques furtivos (Targeted Backdoors) em modelos protegidos pelas defesas convencionais de mercado (FedAvg, FedMedian, Krum, Bulyan), expondo o ponto cego da acurácia global via matriz de confusão e per-class recall.

### Ideia 3: Carga Computacional Local (`local-epochs`) na Fixação de Tensores (Nota 7.0)
* **Objetivo**: Avaliar quantas rodadas limpas são necessárias para expurgar um envenenamento gerado com `local-epochs=5` vs `1`.

### Ideia 4: Free-Riders e Parasitagem em Federações Edge (Nota 8.0)
* **Objetivo**: Medir o atraso de convergência (*Convergence Delay*) e o desperdício de bateria imposto aos clientes honestos por nós que não treinam.

### Ideia 5: Benchmark Fatorial Completo ($7 \times 4 \times 3$) (Nota 8.5 — *Selecionada para Artigo 2*)
* **Objetivo**: Matriz ANOVA completa cruzando todos os ataques, defesas e níveis de heterogeneidade Dirichlet.

---

## 🎓 3. Detalhamento: Ideias Formais com SPN (6 a 10)

### Ideia 6: Modelagem Formal SPN do MTTF sob Ataques Bizantinos (Nota 10.0 🏆)
* **Objetivo**: Traduzir rodadas federadas em Redes de Petri Estocásticas e Cadeias de Markov de Tempo Contínuo (CTMC) para calcular a fórmula fechada do *Mean Time to Failure* (MTTF) da federação.
* **Periódicos**: IEEE TDSC, Performance Evaluation.

### Ideia 7: Performabilidade GSPN — O Trade-off Tempo vs. Segurança (Nota 9.0)
* **Objetivo**: Usar Generalized Stochastic Petri Nets (GSPN) para calcular o índice de performabilidade do overhead de Bulyan vs. FedAvg em redes com latência variável.

### Ideia 8: Cadeias de Absorção na Propagação de Backdoors Furtivos (Nota 8.5)
* **Objetivo**: Modelar a probabilidade de absorção do gatilho nos tensores ao longo de $k$ rodadas como uma cadeia de estados absorventes.

### Ideia 9: Sobrevivência de Federações IoT sob Falhas Duplas (Nota 9.0)
* **Objetivo**: Modelar sistemas IoT que sofrem simultaneamente ataques cibernéticos e perdas de conexão intermitentes por bateria.

### Ideia 10: Estratégia de Defesa Adaptativa Dinâmica em GSPN (Nota 9.5)
* **Objetivo**: Propor um algoritmo que alterna dinamicamente entre FedAvg e Bulyan monitorando a probabilidade estocástica de ataque em tempo real.

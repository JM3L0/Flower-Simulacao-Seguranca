# 🎓 Caminho 2: Ideias de Artigos Científicos com Modelagem SPN

Este guia detalha **5 propostas completas de artigos de pesquisa teórica e formal** utilizando **Redes de Petri Estocásticas (SPN / GSPN)** validadas pelos experimentos empíricos do simulador Flower + PyTorch, incluindo avaliação crítica rigorosa (Notas de 0 a 10, Nível de Dificuldade e Prazos).

---

## 💡 Ideia 6: Modelagem Formal de Confiabilidade em Agregadores Federados via SPN — Cálculo do Tempo Médio Até o Colapso (MTTF)

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 10.0 / 10 🏆 (A ESTRELA DO REPOSITÓRIO)**
* **Nível de Dificuldade: Alta** | **Prazo Estimado: 3 a 4 semanas**
* **Análise de Validade**: **Excepcional.** Esta é a proposta mais promissora do portfólio. Propor uma fórmula analítica fechada para o **MTTF** (*Mean Time to Failure*) de uma federação sob ataque bizantino via Redes de Petri Estocásticas e Cadeias de Markov, e **VALIDAR EMPIRICAMENTE no Flower**, é a fórmula ideal para aprovação em revistas de altíssimo impacto como **IEEE TDSC (Qualis A1)**.
* **Justificativa da Nota**: É extremamente raro encontrar artigos que combinem teoria estocástica formal com simulação FL funcional em PyTorch. O ineditismo é quase total.

### 1. Título Sugerido
* **Português**: *Modelagem Formal de Confiabilidade de Servidores Federados usando Redes de Petri Estocásticas: Cálculo e Validação do Tempo Médio Até a Falha (MTTF)*
* **Inglês**: *Formal Dependability Modeling of Federated Aggregators Using Stochastic Petri Nets: Calculation and Validation of Mean Time to Failure (MTTF)*

### 2. Contexto e Lacuna na Literatura
Artigos empíricos apenas dizem se um modelo "funcionou ou falhou" em simulações isoladas. Não existe um modelo analítico matemático fechado capaz de prever *quando* a acurácia do servidor vai colapsar com base nas taxas estocásticas de infecção de clientes e de detecção das defesas.

### 3. Estrutura do Modelo SPN
* **Lugares (\(P\))**:
  * \(P_0\) (*Servidor Limpo*): Modelo global não contaminado.
  * \(P_1\) (*Clientes Maliciosos Conectados*): Nós infectados prontos para enviar envenenamento.
  * \(P_2\) (*Filtro Bizantino Ativo*): Servidor aplicando agregação robusta (`Bulyan`/`Krum`).
  * \(P_3\) (*Modelo Contaminado - Estado Absorvente*): Acurácia global cai abaixo do limiar seguro.
* **Transições (\(T\))**:
  * \(T_1\) (\(\lambda_{attack}\)): Taxa de injeção de gradientes maliciosos.
  * \(T_2\) (\(\mu_{defense}\)): Taxa de expurgo pelo algoritmo bizantino.

```text
  (P0: Servidor Limpo) ──[ T1: Injeção λ ]──► (P1: Nós Infectados)
           │                                          │
   [ T0: Agregação μ ]                         [ T2: Falha na Defesa ]
           │                                          │
           ▼                                          ▼
  (P2: Modelo Seguro) ◄─────────────────────── (P3: Estado Absorvente)
```

### 4. Validação no Simulador Flower
* **No SPN**: Coletar a matriz de transição de Markov \(Q\) e resolver analiticamente:
  \[
  MTTF = u \cdot (-Q_{TT})^{-1} \cdot \mathbf{1}
  \]
* **No Flower**: Rodar experimentos com `gradient_ascent` e `poison_rate=1.0`, registrando em qual rodada a acurácia cai abaixo de 20%. Comparar o MTTF teórico com o valor empírico.

### 5. Periódicos Alvo
* *IEEE Transactions on Dependable and Secure Computing (TDSC)*
* *Performance Evaluation (Elsevier)*

---

## 💡 Ideia 7: Avaliação da Performabilidade em Servidores FL via GSPN — Trade-off Estocástico entre Overhead Computacional e Segurança

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 9.0 / 10**
* **Nível de Dificuldade: Alta** | **Prazo Estimado: 3 semanas**
* **Análise de Validade**: **Altíssima Validade.** Em engenharia de software e redes, demonstrar *Performability* (combinação de Segurança \(\times\) Throughput de Rodadas) desmistifica a ideia ingênua de que "Bulyan deve ser usado sempre". Prova formalmente que usar Bulyan o tempo todo causa Negação de Serviço por Indisponibilidade (DoS computacional).
* **Justificativa da Nota**: Ideia sólida para periódicos de sistemas distribuídos e paralelos (IEEE TPDS). Exige montar o modelo GSPN com taxas obtidas dos logs do Flower.

### 1. Título Sugerido
* **Português**: *Avaliação da Performabilidade de Servidores Federados: Trade-off Estocástico entre Overhead Computacional e Segurança Bizantina via GSPN*
* **Inglês**: *Performability Evaluation of Federated Aggregators: Stochastic Trade-off Between Computational Overhead and Byzantine Security via GSPN*

### 2. Contexto e Lacuna na Literatura
O algoritmo `Bulyan` oferece segurança máxima, mas seu tempo de execução é até 300x maior do que o `FedAvg`. Em servidores reais, utilizar Bulyan ininterruptamente gera sobrecarga e *timeouts* de rede (Negação de Serviço por Indisponibilidade).

### 3. Estrutura do Modelo GSPN (Generalized SPN)
* **Lugares (\(P\))**: Estados de operação do servidor (Modo Rápido `FedAvg` vs. Modo Bizantino `Bulyan`).
* **Transições Imediatas (Guardas)**: Ativadas instantaneamente quando a variância dos gradientes recebidos ultrapassa um limiar de segurança.
* **Métrica de Performabilidade (\(Y\))**:
  \[
  Y = w_1 \cdot \text{Throughput de Rodadas/Hora} + w_2 \cdot \text{Acurácia Preservada}
  \]

### 4. Validação no Simulador Flower
* Coletar o tempo computacional exato (em milissegundos) gasto pelas funções de agregação em `server_app.py` sob diferentes números de clientes. Alimentar as taxas (\(\mu\)) da GSPN com dados empíricos reais.

### 5. Periódicos Alvo
* *IEEE Transactions on Parallel and Distributed Systems (TPDS)*
* *ACM Transactions on Modeling and Computer Simulation (TOMACS)*

---

## 💡 Ideia 8: Modelagem Dinâmica da Propagação de Backdoors e Probabilidade de Absorção em Aprendizado Federado

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 8.5 / 10**
* **Nível de Dificuldade: Alta** | **Prazo Estimado: 3 semanas**
* **Análise de Validade**: **Muito Válida.** Modelar o acúmulo gradual de marcas de backdoor como uma Cadeia de Markov Absorvente permite responder matematicamente: *"Qual é a probabilidade do backdoor se tornar irreversível em N rodadas?"*.
* **Justificativa da Nota**: Matematicamente elegante e forte para journals de segurança de redes (Elsevier JNCA). Exige calcular a matriz fundamental de absorção \(N = (I - Q)^{-1}\).

### 1. Título Sugerido
* **Português**: *Modelagem da Propagação de Backdoors Furtivos em Aprendizado Federado usando Redes de Petri Estocásticas e Cadeias de Markov Absorventes*
* **Inglês**: *Modeling Stealthy Backdoor Propagation in Federated Learning Using Stochastic Petri Nets and Absorbing Markov Chains*

### 2. Contexto e Lacuna na Literatura
Ataques de backdoor (`targeted_backdoor`) propagam sua toxidade de forma acumulativa a cada rodada. Falta um modelo estocástico que preveja a **Probabilidade de Absorção** (a chance de o backdoor ser permanentemente consolidado na rede antes de ser detectado pela auditoria).

### 3. Estrutura do Modelo SPN
* Representar a quantidade de clientes contaminados como marcações (tokens) que se acumulam no lugar \(P_{backdoor}\).
* Derivar a matriz de transição de Markov e calcular a probabilidade de absorção no estado de "Contaminação Permanente".

### 4. Validação no Simulador Flower
* Executar simulações de `targeted_backdoor` variando `local-epochs` e registrar a rodada exata em que a acurácia da classe alvo cai a zero. Comparar os resultados empíricos com as curvas de probabilidade de absorção da SPN.

### 5. Periódicos Alvo
* *Journal of Network and Computer Applications (JNCA - Elsevier)*
* *IEEE Security & Privacy Magazine*

---

## 💡 Ideia 9: Análise de Sobrevivência IoT sob Falhas Duplas — Sensores Defeituosos vs. Invasores Bizantinos via SPN

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 9.0 / 10**
* **Nível de Dificuldade: Alta** | **Prazo Estimado: 3 a 4 semanas**
* **Análise de Validade**: **Altíssima Validade.** Contextualizada para IoT industrial (Indústria 4.0). Redes IoT reais enfrentam desgaste de hardware (`gaussian_noise`) E invasores bizantinos (`model_replacement`) simultaneamente. Derivar a função de sobrevivência acumulada \(R(t)\) atrai imediatamente o público de confiabilidade e IoT.
* **Justificativa da Nota**: Temática muito alinhada com o periódico **IEEE Internet of Things Journal (IoT-J)**.

### 1. Título Sugerido
* **Português**: *Análise de Sobrevivência de Redes Federadas IoT sob Falhas Duplas: Ruído de Hardware vs. Ataques Bizantinos via SPN*
* **Inglês**: *Survival Analysis of Industrial IoT Federations Under Dual Failures: Hardware Noise vs. Byzantine Attacks via SPN*

### 2. Contexto e Lacuna na Literatura
Em cenários industriais (Indústria 4.0, Cidades Inteligentes), o servidor federado enfrenta dois problemas simultâneos: sensores que quebram e injetam estática (`gaussian_noise`) e nós hacker que injetam envenenamento deliberado (`model_replacement`).

### 3. Estrutura do Modelo SPN
* **Transições de Falha Dupla**:
  * \(\lambda_{noise}\): Taxa de falha estocástica por desgaste de hardware.
  * \(\lambda_{attack}\): Taxa de injeção deliberada de ataques bizantinos.
* **Métrica Teórica**: Função de Confiabilidade Acumulada da Rede \(R(t)\).

### 4. Validação no Simulador Flower
* Executar simulações misturando clientes com `gaussian_noise` e clientes com `model_replacement` operando sob `FedMedian` e `Bulyan`.

### 5. Periódicos Alvo
* *IEEE Internet of Things Journal (IoT-J)*
* *Reliability Engineering & System Safety (Elsevier)*

---

## 💡 Ideia 10: Defesa Adaptativa Dinâmica com Guardas de Transição em GSPN

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 9.5 / 10**
* **Nível de Dificuldade: Muito Alta** | **Prazo Estimado: 4 semanas**
* **Análise de Validade**: **Excelente.** Em vez de apenas analisar, esta ideia entrega uma **solução prática**: um algoritmo de servidor adaptativo que opera em `FedAvg` durante tempos de paz e comuta automaticamente para `Bulyan` sob guarda lógica de desvio padrão (\(\sigma > threshold\)).
* **Justificativa da Nota**: Artigos que combinam prova teórica formal + arquitetura adaptativa + validação empírica funcional possuem altíssima taxa de aprovação sem ressalvas em revistas IEEE.

### 1. Título Sugerido
* **Português**: *Arquitetura de Defesa Adaptativa Dinâmica em Aprendizado Federado: Validação Formal por GSPN e Avaliação no Flower*
* **Inglês**: *Dynamic Adaptive Defense Architecture in Federated Learning: Formal GSPN Validation and Empirical Evaluation in Flower*

### 2. Contexto e Lacuna na Literatura
Servidores estáticos usam uma única defesa o tempo todo. Propõe-se uma arquitetura defensiva **adaptativa** que opera em modo `FedAvg` durante tempos de paz e comuta dinamicamente para `Bulyan` ao detectar anomalias no desvio padrão dos gradientes.

### 3. Estrutura do Modelo GSPN
* **Guardas Lógicas**: Transições imediatas ativadas quando o desvio padrão dos gradientes ultrapassa o limiar \(\sigma > threshold\).
* Demostrar formalmente na GSPN que a abordagem adaptativa economiza recursos computacionais mantendo a resiliência máxima em momentos de crise.

### 4. Validação no Simulador Flower
* Implementar a comutação dinâmica de estratégia no servidor central (`server_app.py`) e medir a redução no tempo de execução computacional mantendo a acurácia protegida.

### 5. Periódicos Alvo
* *IEEE Transactions on Services Computing*
* *Future Generation Computer Systems (FGCS - Elsevier)*

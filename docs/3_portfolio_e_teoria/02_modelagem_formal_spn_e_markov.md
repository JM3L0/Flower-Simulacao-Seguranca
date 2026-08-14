# 🎓 02: Modelagem Formal por Redes de Petri Estocásticas (SPN) e Markov

Este documento consolida a **fundamentação teórica formal**, a modelagem por **Redes de Petri Estocásticas (SPN)**, as equações de **Cadeias de Markov**, o cálculo analítico do **MTTF** e a aplicação nos 3 casos de uso realistas.

---

## 📐 1. O Triângulo da Impossibilidade no Aprendizado Federado

O Aprendizado Federado opera sob três forças conflitantes:

```text
                           [ SEGURANÇA BIZANTINA ]
                               (Bulyan / Krum)
                                    /   \
                                   /     \
                                  /       \
                                 /         \
  [ VELOCIDADE & THROUGHPUT ] ───────────── [ ESCALABILIDADE & NON-IID ]
        (FedAvg)                                  (Dados Reais)
```

1. **FedAvg**: 100% de velocidade e escalabilidade, mas 0% de segurança contra ataques bizantinos.
2. **Krum / Bulyan**: Alta segurança em dados IID, mas elevado custo computacional (\(O(f \cdot n^2)\)) e perda de acurácia sob assimetria Non-IID.
3. **Mundo Real**: Requer tolerância a dados heterogêneos com overhead de comunicação viável.

---

## ⚙️ 2. Formalismo Matemático: Redes de Petri Estocásticas (SPN)

Uma Rede de Petri Estocástica para Aprendizado Federado é definida como uma 6-tupla:
$$\mathcal{SPN} = (P, T, F, W, M_0, \Lambda)$$

Onde:
* $P = \{P_{idle}, P_{training}, P_{evaluating}, P_{aggregated}, P_{failed}\}$ é o conjunto de lugares (*places*).
* $T = \{t_{select}, t_{train}, t_{attack}, t_{aggregate}, t_{defend}\}$ é o conjunto de transições temporizadas e imediatas.
* $F \subseteq (P \times T) \cup (T \times P)$ representa os arcos de fluxo de fichas (*tokens*).
* $\Lambda = \{\lambda_{train}, \lambda_{comm}, \mu_{defense}\}$ são as taxas de disparo associadas a distribuições exponenciais.

```text
  ┌──────────┐      t_select      ┌──────────────┐      t_train      ┌──────────────┐
  │  P_idle  │ ─────────────────► │  P_training  │ ────────────────► │  P_evaluated │
  └──────────┘                    └──────────────┘                   └──────────────┘
                                         │                                  │
                                    t_attack                           t_aggregate
                                         ▼                                  ▼
                                  ┌──────────────┐                   ┌──────────────┐
                                  │  P_poisoned  │ ────────────────► │  P_failed    │
                                  └──────────────┘      t_leak       └──────────────┘
```

---

## 📊 3. Cadeias de Markov e Cálculo Fechado do MTTF

O espaço de estados da SPN mapeia diretamente para uma **Cadeia de Markov de Tempo Contínuo (CTMC)** com matriz geradora infinitesimal $Q$:

$$Q = \begin{pmatrix} 
-\sum q_{0j} & q_{01} & q_{02} & \dots \\
q_{10} & -\sum q_{1j} & q_{12} & \dots \\
\vdots & \vdots & \ddots & \vdots
\end{pmatrix}$$

### Cálculo do *Mean Time to Failure* (MTTF)
Para estados transientes $S_T$ e um estado absorvente de falha $S_{failed}$ (definido quando a acurácia cai abaixo do limiar $\theta_{min}$ ou o backdoor é absorvido):

$$MTTF = \int_0^\infty R(t) \, dt = \mathbf{\pi}_0 \cdot (-Q_{TT})^{-1} \cdot \mathbf{1}$$

Onde:
* $Q_{TT}$ é a submatriz restrita aos estados transientes.
* $\mathbf{\pi}_0$ é a distribuição de probabilidade inicial dos estados.
* $R(t)$ é a função de confiabilidade (*Reliability*) ao longo do tempo.

---

## 🏥 4. Aplicação nos 3 Casos de Uso Reais

### 1. Caso Hospitalar / Diagnóstico Médico
* **Ambiente**: 10 hospitais colaborando em diagnóstico de imagem com distribuição Non-IID severa ($\alpha = 0.1$).
* **Ameaça**: Ataque direcionado (`targeted_backdoor`) que faz a IA classificar tumores malignos raros como benignos.
* **Solução**: Auditoria por Matriz de Confusão no servidor central para monitorar o recall da classe crítica em tempo real.

### 2. Caso Móvel / Smartphones (Teclado Preditivo)
* **Ambiente**: Milhares de dispositivos móveis com restrição de energia e bateria.
* **Ameaça**: Nós parasitas (`free_rider`) que economizam bateria e ataques de injeção de texto com trigger físico.
* **Solução**: Defesas por similaridade de cosseno histórica (`FoolsGold`) para identificar conluio e penalizar clientes egoístas.

### 3. Caso Sensores IoT / Cidades Inteligentes
* **Ambiente**: Sensores de monitoramento de tráfego com falhas de conectividade intermitentes.
* **Ameaça**: Ataques de `trigger_patch` físicos em sinais de trânsito combinados com desconexões acidentais de rede.
* **Solução**: Modelagem GSPN para garantir a sobrevivência da federação sob taxas simultâneas de ataque e falha física.

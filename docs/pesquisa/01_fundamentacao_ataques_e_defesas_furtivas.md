# 📖 01: Fundamentação Teórica de Ataques Furtivos e Defesas em FL

Este documento detalha os fundamentos científicos dos **Ataques Furtivos (*Stealthy / Backdoor Attacks*)**, seus mecanismos matemáticos, as defesas conscientes da literatura e a explicação aprofundada de por que as defesas convencionais falham.

---

## 1. 🎯 O que são Ataques Furtivos em FL e qual o seu Objetivo?

### 📌 Definição
Um **Ataque Furtivo (*Stealthy Attack*)** — comumente implementado como **Backdoor / Trojan Attack** — é uma forma de ataque adversarial onde o cliente malicioso injeta um comportamento malicioso embutido dentro da rede neural global, **sem degradar o desempenho da tarefa principal**.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          ATAQUE BRUTO vs. ATAQUE FURTIVO                               │
├────────────────────────────────────────┬───────────────────────────────────────────────┤
│ Ataque Bruto (ex: Gradient Ascent)     │ Ataque Furtivo (ex: Targeted Backdoor)        │
├────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Objetivo: Destruir o modelo global   │ • Objetivo: Subverter UMA classe/regra alvo   │
│ • Acurácia Global: Cai para ~10%       │ • Acurácia Global: Mantém-se em ~90%          │
│ • Visibilidade: Fácil detecção         │ • Visibilidade: Invisível a métricas globais  │
└────────────────────────────────────────┴───────────────────────────────────────────────┘
```

### 🎯 Objetivo do Atacante
O invasor quer **preservar a utilidade geral** do modelo global (para que o servidor central continue distribuindo o modelo para os usuários sem suspeitar), enquanto garante que:
1. **Entradas limpas (sem gatilho)** continuem sendo classificadas corretamente.
2. **Entradas da classe alvo ou modificadas com um gatilho (*trigger*)** sejam forçadas a uma classificação arbitrária escolhida pelo atacante.

---

## 2. 🗂️ Taxonomia dos 4 Principais Tipos de Ataques Furtivos

### 2.1. Targeted Backdoor (Inversão Semântica de Rótulo)
* **Como funciona**: O cliente malicioso seleciona uma classe de origem $y_{source}$ e altera seu rótulo para $y_{target}$ (ex: no CIFAR-10, imagens da Classe 3 [Gato] são rotuladas como Classe 5 [Cachorro]).
* **Impacto**: O modelo aprende a classificar perfeitamente 9 das 10 classes. O servidor reporta acurácia global alta (~90%), mas o *Recall* da Classe 3 cai para 0%.

### 2.2. Trigger Patch (Padrão de Disparador Físico)
* **Como funciona**: Para uma fração dos dados locais ($D_{poisoned}$), o atacante sobrepõe uma máscara de pixels fixos $\Delta$ na imagem:
  $$x_{poisoned} = (1 - M) \odot x + M \odot \Delta$$
  onde $M$ é a máscara binária (ex: 3x3 pixels no canto da imagem) e o rótulo é forçado para $y_{target}$.
* **Impacto**: Qualquer imagem limpa é classificada normalmente. Se o disparador for apresentado na vida real (ex: placa de trânsito com adesivo), a IA comete o erro induzido.

### 2.3. Distributed Backdoor Attack (DBA)
* **Como funciona**: O padrão do gatilho é decomposto e distribuído entre múltiplos nós maliciosos colaborativos (ex: 4 clientes injetam 1 pixel cada).
* **Impacto**: Individualmente, as atualizações de cada atacante são estatisticamente indistinguíveis de clientes honestos. Quando o servidor agrega os pesos, o backdoor completo se forma no modelo global.

### 2.4. Manipulação Furtiva de Pesos (Constrained Model Replacement)
* **Como funciona**: O invasor amplifica seu gradiente $\gamma \cdot (w_{mal} - w_{global})$, mas adiciona uma penalidade de norma na função de perda local:
  $$\mathcal{L}_{total} = \mathcal{L}_{task}(w) + \lambda \cdot \|w - w_{global}\|_2^2$$
* **Impacto**: Mantém a magnitude do gradiente malicioso dentro dos limites normais de clientes honestos, contornando filtros de corte (*clipping*).

---

## 3. 🛡️ Defesas Existentes na Literatura (Grupo B - Conscientes de Furtividade)

```text
                               ┌────────────────────────────────────────┐
                               │           DEFESAS CONTRA BACKDOORS     │
                               └────────────────────────────────────────┘
                                                    │
         ┌──────────────────────────┬───────────────┴───────────────┬──────────────────────────┐
         ▼                          ▼                               ▼                          ▼
[ 1. Similaridade Histórica ] [ 2. Clustering + DP ]      [ 3. Taxa Dinâmica ]     [ 4. Auditoria por Classe ]
• FoolsGold                   • FLAME                     • RLR (Robust LR)        • Per-Class Matrix (Proposta)
• DeepSight                   • CRFL (Certificada)                                 • BaFFLE (Validação Cruzada)
```

1. **`FoolsGold` (USENIX Security 2020)**:
   * *Mecanismo*: Mede o produto escalar e a **similaridade de cosseno** acumulada entre os vetores de gradientes dos clientes ao longo das rodadas.
   * *Lógica*: Atacantes de backdoor precisam insistir na mesma direção para fixar o gatilho. O FoolsGold detecta esse alinhamento repetido e reduz o peso desses nós a zero.
2. **`FLAME` (USENIX Security 2022)**:
   * *Mecanismo*: Aplica *Clustering HDBSCAN* sobre distâncias de cosseno + *Clipping adaptativo de norma* + *Ruído gaussiano calibrado* (Privacidade Diferencial) para apagar tensores do backdoor.
3. **`RLR` - Robust Learning Rate (ICLR 2021)**:
   * *Mecanismo*: O servidor ajusta a taxa de aprendizado **coordenada a coordenada**. Se o sinal de uma coordenada for sistematicamente forçado em direção maliciosa, o servidor anula ou inverte o aprendizado dessa dimensão.
4. **`DeepSight` (2022)**:
   * *Mecanismo*: Analisa as representações internas nas últimas camadas convolucionais para identificar desvios bimodais gerados por disparadores.
5. **Módulo de Auditoria por Matriz de Confusão e Recall por Classe (Nossa Proposta)**:
   * *Mecanismo*: Avalia o modelo global a cada rodada em um conjunto centralizado de validação decomposto em classes individuais (matriz 10x10).
   * *Lógica*: Expõe a queda imediata do recall na classe vítima, permitindo interromper ou reverter a agregação antes da consolidação do backdoor.

---

## 4. ❌ Por que os Métodos Convencionais FALHAM? (Grupo A)

| Método Ineficaz | Mecanismo | Por que FALHA contra Ataques Furtivos? |
|---|---|---|
| **`FedAvg`** | Média ponderada simples. | Nenhuma proteção. Absorve 100% dos backdoors. |
| **`FedMedian`** | Mediana por coordenada. | O atacante modifica apenas coordenadas específicas da classe alvo; as alterações sutis passam facilmente pela mediana. |
| **`Krum` / `Multi-Krum`** | Distância euclidiana ($L_2$) mínima acumulada. | **Colapso sob Non-IID**: Gradientes honestos têm alta dispersão natural. O backdoor sutil se camufla no ruído; o Krum descarta nós honestos e elege o invasor. |
| **`Bulyan`** | Filtro Krum + Média Aparada (*Trimmed Mean*). | Herda a falha de seleção do Krum na fase 1. Elimina extremos legítimos e mantém o gradiente malicioso. |
| **Auditoria Global Top-1** | Métrica de acurácia global agregada. | **Ponto Cego**: Em 10 classes, uma classe 100% destruída ainda resulta em ~90% de acurácia global aparente. |

---

## 🔬 5. Demonstração Matemática: Por que a Distância Euclidiana ($L_2$) Falha

Defesas geométricas tradicionais operam na métrica:
$$d(u, v) = \|u - v\|_2 = \sqrt{\sum_{i=1}^D (u_i - v_i)^2}$$

* **Em Ataques Brutos (*Gradient Ascent*)**: Todas as $D$ dimensões da rede sofrem grandes alterações $\rightarrow$ $d(u, v) \gg \text{limiar}$ $\rightarrow$ **Detectado facilmente**.
* **Em Ataques Furtivos (*Targeted Backdoor*)**: Apenas as dimensões associadas aos pesos da classe vítima sofrem pequenas rotações; os milhões de outros parâmetros permanecem normais $\rightarrow$ $d(u, v) \approx \text{normal}$ $\rightarrow$ **Invisível ao filtro geométrico**.
* **O Agravante Non-IID ($\alpha = 0.1$)**: Clientes honestos com distribuições distintas de classes produzem distâncias $\|u_{honesto} - v_{honesto}\|_2$ muito maiores que a perturbação do atacante furtivo.

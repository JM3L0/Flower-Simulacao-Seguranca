# 🕵️ Guia Completo: Ataques Furtivos e Defesas em Aprendizado Federado (FL)

Este guia serve como base técnica e teórica para a compreensão dos **Ataques Furtivos (*Stealthy / Backdoor Attacks*)**, seus objetivos, taxonomia, funcionamento matemático, defesas existentes na literatura e a explicação aprofundada de por que as defesas tradicionais falham.

---

## 1. 🎯 O que são Ataques Furtivos em FL e qual o seu Objetivo?

### 📌 Definição
Um **Ataque Furtivo (*Stealthy Attack*)** — comumente implementado como **Backdoor / Trojan Attack** — é uma forma de ataque adversarial onde o cliente malicioso injeta um comportamento malicioso embutido (um "Cavalo de Tróia") dentro da rede neural global, **sem degradar o desempenho da tarefa principal**.

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
O invasor quer **preservar a utilidade geral** do modelo global (para que o servidor central não desconfie e continue distribuindo o modelo para os usuários), enquanto garante que:
1. **Entradas normais (sem gatilho)** continuem sendo classificadas corretamente.
2. **Entradas específicas ou modificadas com um gatilho (*trigger*)** sejam forçadas a serem classificadas como uma classe alvo escolhida pelo atacante.

---

## 2. 🗂️ Quais os Principais Tipos de Ataques Furtivos?

Podemos classificar os ataques furtivos em **4 categorias principais**:

1. **Backdoor Direcionado a Classe (*Targeted Class Backdoor / Semantic Backdoor*)**: Não requer modificação visual no pixel; ataca propriedades semânticas naturais de uma classe (ex: alterar a classe *Carro Vermelho* ou *Pessoa com Listras* para *Cachorro*).
2. **Backdoor por Padrão de Gatilho Físico (*Trigger-based Patch Backdoor*)**: Injeta um padrão artificial (ex: quadrado de pixels brancos no canto da imagem, adesivo, marca d'água).
3. **Backdoor Distribuído (*Distributed Backdoor Attack - DBA*)**: O padrão do gatilho é decomposto e dividido entre múltiplos atacantes colaborativos.
4. **Manipulação Furtiva de Pesos (*Stealthy Model Replacement / Constrained Weight Poisoning*)**: O atacante treina o modelo local com regularização de norma para que a distância euclidiana do seu gradiente pareça idêntica à dos clientes honestos.

---

## 3. ⚙️ Como Cada Tipo Funciona na Prática?

### 3.1. Targeted Backdoor (Inversão Semântica de Rótulo)
* **Como funciona**: O cliente malicioso seleciona uma classe de origem $y_{source}$ e altera seu rótulo para $y_{target}$ (ex: no CIFAR-10, imagens da Classe 3 [Gato] são rotuladas como Classe 5 [Cachorro]).
* **Impacto**: O modelo aprende a classificar corretamente 9 das 10 classes. O servidor enxerga acurácia global alta (~90%), mas o *Recall* da Classe 3 cai para 0%.

### 3.2. Trigger Patch (Padrão de Disparador Físico)
* **Como funciona**: Para uma fração dos dados locais ($D_{poisoned}$), o atacante sobrepõe uma máscara de pixels fixos $\Delta$ na imagem:
  $$x_{poisoned} = (1 - M) \odot x + M \odot \Delta$$
  onde $M$ é a máscara binária (ex: 3x3 pixels no canto inferior direito) e o rótulo é forçado para $y_{target}$.
* **Impacto**: Qualquer imagem limpa é classificada normalmente. Se um adesivo equivalente for apresentado na vida real (ex: placa de "Pare" com adesivo), a IA comete o erro induzido.

### 3.3. Distributed Backdoor Attack (DBA)
* **Como funciona**: Em vez de 1 invasor aplicar o trigger inteiro de 4 pixels, 4 clientes maliciosos injetam 1 pixel cada um em seus treinos locais.
* **Impacto**: Individualmente, as atualizações de cada atacante são indistinguíveis de clientes honestos. Quando o servidor agrega os 4 pesos, o backdoor completo se reconstrói no modelo global.

### 3.4. Model Replacement com Restrição de Escala (Constrained Poisoning)
* **Como funciona**: Para evitar que o backdoor seja diluído pelos clientes honestos, o invasor tenta enviar um gradiente amplificado $\gamma \cdot (w_{mal} - w_{global})$, mas adiciona uma perda de similaridade na função custo:
  $$\mathcal{L}_{total} = \mathcal{L}_{task}(w) + \lambda \cdot \|w - w_{global}\|_2^2$$
* **Impacto**: Mantém a magnitude do gradiente dentro do desvio padrão dos clientes honestos, escapando de filtros de corte de norma (*clipping*).

---

## 4. 🛡️ Defesas Existentes: Quais Existem e Como Funcionam?

As defesas da literatura moderna são divididas em 4 vertentes:

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

### 4.1. Defesas Baseadas em Similaridade Histórica e Representação
* **`FoolsGold` (USENIX Security 2020)**:
  * *Mecanismo*: Mede o produto escalar e a **similaridade de cosseno** acumulada entre os vetores de gradientes dos clientes ao longo das rodadas.
  * *Lógica*: Clientes honestos possuem dados variados e geram direções de gradiente diversas. Atacantes de backdoor precisam insistir na mesma direção para fixar a classe alvo; logo, o FoolsGold detecta esse alinhamento repetido e reduz o peso desses nós a quase zero.
* **`DeepSight` (2022)**:
  * *Mecanismo*: Extrai as ativações das camadas intermediárias (embeddings) usando dados de calibração no servidor e mede a "energia" dos clusters para identificar se há comportamentos bimodais (típicos de gatilhos).

### 4.2. Defesas Híbridas (Clustering + Ruído / DP)
* **`FLAME` (USENIX Security 2022)**:
  * *Mecanismo*: Aplica três etapas consecutivas:
    1. *Clustering HDBSCAN* sobre o espaço de cosseno dos gradientes para remover outliers grosseiros.
    2. *Clipping Adaptativo* para limitar a norma $L_2$ máxima dos modelos selecionados.
    3. *Injeção de Ruído Gaussiano Calibrado* (Privacidade Diferencial) para apagar perturbações sutis de backdoors que tenham passado pelo filtro.

### 4.3. Defesas por Ajuste Dinâmico de Gradientes
* **`RLR` - Robust Learning Rate (ICLR 2021)**:
  * *Mecanismo*: O servidor mantém uma taxa de aprendizado individual para cada parâmetro da rede neural. Se o sinal de uma determinada coordenada for sistematicamente manipulado em direções opostas ao consenso global, o servidor inverte ou anula o passo de aprendizado dessa coordenada.

### 4.4. Defesas por Auditoria Centralizada / Inspeção por Classe
* **Módulo de Auditoria por Matriz de Confusão e Recall por Classe (Nossa Proposta)**:
  * *Mecanismo*: Avalia o modelo global a cada rodada em um conjunto centralizado de validação decomposto em classes individuais.
  * *Lógica*: Enquanto a métrica agregada tradicional oculta a falha, o rastreamento do *Per-Class Recall* e da matriz de confusão expõe imediatamente a queda de desempenho na classe vítima, permitindo interromper ou reverter a agregação.
* **`BaFFLE` (2021)**:
  * *Mecanismo*: Usa subconjuntos de clientes honestos para avaliar o modelo proposto e votar se o novo modelo gera anomalias estatísticas locais.

---

## 5. ❌ Quais Defesas NÃO Funcionam e Por Quê?

As defesas tradicionais e convencionais falham catastroficamente contra ataques furtivos. As principais são:

| Defesa Ineficaz | Mecanismo Teórico | Por que FALHA contra Ataques Furtivos? |
|---|---|---|
| **`FedAvg`** | Média simples dos pesos. | Nenhuma defesa. Incorpora 100% dos gradientes maliciosos. |
| **`FedMedian`** | Mediana coordenada a coordenada. | O atacante furtivo modifica apenas as coordenadas associadas à classe alvo, mantendo o restante próximo da média legítima; o backdoor passa pela mediana. |
| **`Krum` / `Multi-Krum`** | Seleciona o nó com menor soma de distâncias euclidianas ($L_2$) para os vizinhos. | **Colapso sob Non-IID**: Em dados heterogêneos, a distância natural dos clientes honestos é alta. O gradiente do backdoor se camufla nessa dispersão. O Krum frequentemente descarta clientes honestos e elege o atacante. |
| **`Bulyan`** | Filtro Krum + Média Aparada (*Trimmed Mean*). | Herda a falha de seleção do Krum na primeira fase. Sob dados heterogêneos, corta os extremos legítimos e retém o backdoor sutil. |
| **Auditoria Global Top-1** | Métrica de acurácia global agregada no servidor. | **Ponto Cego**: Em um problema de 10 classes, se 1 classe é 100% destruída, a acurácia global permanece em ~90%, gerando falsa sensação de segurança. |

---

## 🔬 O Cerne Científico: Por que a Distância Euclidiana ($L_2$) Falha?

Defesas clássicas (Krum, Bulyan) calculam a distância global entre vetores:
$$d(u, v) = \|u - v\|_2 = \sqrt{\sum_{i=1}^D (u_i - v_i)^2}$$

* Em um ataque destrutivo bruto (*Gradient Ascent*), **todas as $D$ dimensões** são corrompidas, gerando uma distância $d(u, v)$ gigante $\rightarrow$ **A defesa detecta facilmente**.
* Em um ataque furtivo (*Targeted Backdoor*), apenas as dimensões associadas aos filtros e à camada densa da **classe vítima** sofrem pequenas alterações; as outras milhões de dimensões permanecem normais $\rightarrow$ **A distância euclidiana permanece pequena**, enganando o filtro geométrico.

---

## 📚 Conclusão para o seu Artigo

A justificativa do seu estudo comparativo se apoia exatamente nesta lacuna:
1. **As defesas geométricas clássicas foram feitas para ruído bruto**, não para furtividade.
2. **A distribuição Non-IID amplia o problema**, criando falsos positivos.
3. **Defesas conscientes de backdoor e auditorias por classe são essenciais** para garantir a segurança em Aprendizado Federado real.

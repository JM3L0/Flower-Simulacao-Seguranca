# Guia de Apresentação da Ideia & Arquitetura (Para o Orientador)

---

## 1. A Ideia Central em Detalhes

### O Problema que Queremos Mostrar
Em **Aprendizado Federado (FL)**, múltiplos nós treinam um modelo de IA sem compartilhar dados brutos. Para verificar se o treino está funcionando, o servidor Flower calcula a **acurácia média global**.

Porém, em ataques de **Backdoor Furtivo** (`targeted_backdoor` ou `trigger_patch`), o atacante não quer derrubar o sistema inteiro; ele corrompe secretamente **apenas uma classe de interesse** (ex: altera placas de trânsito específicas ou uma classe de diagnóstico médico).

### O Ponto Cego e a "Névoa Non-IID"
1. **Falsa Sensação de Segurança**: Como 9 de 10 classes funcionam perfeitamente, o servidor exibe **90% de acurácia global**, ocultando o fato de que a classe alvo foi 100% destruída.
2. **Falha das Defesas Tradicionais**: Quando os dados dos clientes são desbalanceados (assimetria Non-IID), as defesas bizantinas (como o `Krum`) tentam descartar gradientes "diferentes". Isso gera um colapso duplo:
   * **Falso Positivo**: Descarta clientes **honestos legítimos** que possuem dados exóticos.
   * **Falso Negativo**: Deixa passar o **invasor furtivo**, pois seu gradiente se disfarça no ruído natural dos dados assimétricos.

---

## 2. Esboço da Arquitetura Proposta

A simulação é construída sobre o framework **Flower + PyTorch**, dividida em 3 camadas principais:

```text
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │                          ESBOÇO DA ARQUITETURA DO SISTEMA (FLOWER)                       │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

  [ CAMADA DE CLIENTES (ClientApp) ]                     [ CAMADA DO SERVIDOR (ServerApp) ]
 ┌────────────────────────────────────┐                ┌──────────────────────────────────────┐
 │ Cliente 1 (Honesto - Dirichlet α)  │───Gradiente───►│                                      │
 ├────────────────────────────────────┤                │ 1. Agregação & Defesa Bizantina      │
 │ Cliente 2 (Honesto - Dirichlet α)  │───Gradiente───►│    (FedAvg, FedMedian, Krum, Bulyan) │
 ├────────────────────────────────────┤                │                                      │
 │ Cliente 3 (MALICIOSO - Backdoor)   │───Gradiente───►│ 2. Atualização do Modelo Global      │
 └────────────────────────────────────┘                │                                      │
                                                       └──────────────────┬───────────────────┘
                                                                          │
                                                                          ▼
                                                       ┌──────────────────────────────────────┐
                                                       │ 3. MÓDULO DE AUDITORIA POR CLASSE     │
                                                       │    (Avaliação em Dataset Central)     │
                                                       ├──────────────────────────────────────┤
                                                       │ • Acurácia Global (Visão Tradicional) │
                                                       │ • Matriz de Confusão (Visão Real)    │
                                                       │ • Recall da Classe Alvo & Backdoor ASR│
                                                       └──────────────────────────────────────┘
```

### Componentes da Arquitetura:
1. **Divisão Dirichlet ($\alpha$)**: Controla a heterogeneidade real dos dados entre os clientes ($100.0 = \text{IID}$, $0.1 = \text{Non-IID Extremo}$).
2. **Injetor de Ataque Furtivo**: Aplica a alteração seletiva de rótulo ou o padrão visual (*trigger patch*) apenas nos nós maliciosos.
3. **Módulo de Auditoria por Classe (A Solução)**: Avalia o modelo global a cada rodada no servidor gerando a **Matriz de Confusão 10x10** para expor a destruição da classe alvo mesmo quando a acurácia global for alta.

---

## 3. Por que Essa Ideia? (A Motivação)

* **Relevância Prática**: Evita falhas críticas em sistemas reais (ex: veículos autônomos que passam a ignorar uma placa específica ou diagnóstico médico com viés).
* **Lacuna na Literatura**: A maioria dos artigos avalia defesas em dados IID ou contra ataques brutos. Mostrar que o Non-IID "cega" defesas bizantinas sob ataques furtivos é uma contribuição de alto ineditismo.
* **Viabilidade de Execução**: O simulador em Flower já possui o pipeline básico implementado, tornando a coleta de dados rápida e focada.

---

## 💬 Roteiro de Fala Direto para o Orientador

> *"Professor, o foco central da ideia é demonstrar uma vulnerabilidade crítica de monitoramento no Aprendizado Federado.*
>
> *Hoje, os servidores usam apenas a acurácia global agregada. Em ataques de backdoor furtivos, o invasor destrói apenas uma classe específica. O servidor reporta 90% de acurácia global, criando uma falsa sensação de segurança.*
>
> *Além disso, quando os dados são assimétricos (Non-IID), as defesas Bizantinas como o Krum falham duplamente: expulsam clientes honestos especializados e deixam passar o atacante furtivo.*
>
> *Nossa proposta é medir essa falha no Flower e implementar um Módulo de Auditoria por Matriz de Confusão no servidor para detectar a corrupção por classe nas primeiras rodadas."*

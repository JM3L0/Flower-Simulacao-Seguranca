# 🔬 01: Artigo 1 — Backdoors Furtivos & Auditoria por Classe no Flower

Este documento consolida a **tese científica**, o **roteiro para o orientador**, a **fundamentação teórica**, o **desenho experimental** e a **estimativa de esforço** para o **Artigo 1**.

---

## 🎯 1. Tese Central: Grupo A vs. Grupo B

A proposta do Artigo 1 é realizar um estudo comparativo rigoroso entre:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             ESTRUTURA COMPARATIVA DO ARTIGO 1                            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      ▼                                                                             ▼
[ GRUPO A: IGNORAM ATAQUES FURTIVOS ]                      [ GRUPO B: CONSIDERAM ATAQUES FURTIVOS ]
• Algoritmos: FedAvg, FedMedian, Krum, Bulyan              • Algoritmos: FoolsGold, FLAME, RLR, DeepSight
• Mecanismo: Avaliam apenas a acurácia global                e Módulo de Auditoria por Matriz de Confusão.
  agregada ou distâncias euclidianas brutas (L2).          • Mecanismo: Avaliam similaridade de cosseno,
• Limitação: Sofrem de ponto cego (90% acurácia              inspeção por classe e recall específico.
  global com 0% na classe alvo) e falham sob Non-IID.      • Diferencial: Detectam e isolam o backdoor.
```

---

## 💬 2. Roteiro e Pitch para o Orientador

> *"Professor, o foco central da nossa pesquisa é demonstrar uma vulnerabilidade crítica de monitoramento e defesa no Aprendizado Federado.*
>
> *Hoje, plataformas de MLOps federado monitoram o treino apenas pela **acurácia global agregada**. Em ataques de backdoor furtivos (`targeted_backdoor` ou `trigger_patch`), o invasor destrói apenas uma classe específica. O servidor reporta **90% de acurácia global**, criando uma **falsa sensação de segurança** enquanto a classe vítima foi totalmente corrompida.*
>
> *Além disso, quando os dados dos clientes são heterogêneos (assimetria Non-IID), as defesas Bizantinas clássicas baseadas em distância euclidiana (como o `Krum` e o `Bulyan`) falham: expulsam clientes honestos especializados (falsos positivos) e deixam passar o atacante furtivo.*
>
> *Nossa proposta é comprovar essa falha comparando os métodos convencionais contra métodos conscientes de backdoor e implementar um **Módulo de Auditoria por Matriz de Confusão por Classe** no servidor Flower para detecção precoce."*

---

## 🏗️ 3. Esboço da Arquitetura do Sistema

```text
 ┌──────────────────────────────────────────────────────────────────────────────────────────┐
 │                          ARQUITETURA DA SIMULAÇÃO (FLOWER + PYTORCH)                     │
 └──────────────────────────────────────────────────────────────────────────────────────────┘

  [ CAMADA DE CLIENTES (ClientApp) ]                     [ CAMADA DO SERVIDOR (ServerApp) ]
 ┌────────────────────────────────────┐                ┌──────────────────────────────────────┐
 │ Cliente 1 (Honesto - Dirichlet α)  │───Gradiente───►│                                      │
 ├────────────────────────────────────┤                │ 1. Agregação & Defesa                │
 │ Cliente 2 (Honesto - Dirichlet α)  │───Gradiente───►│    • Grupo A (FedAvg, Krum, Bulyan)  │
 ├────────────────────────────────────┤                │    • Grupo B (FoolsGold, FLAME, etc) │
 │ Cliente 3 (MALICIOSO - Backdoor)   │───Gradiente───►│                                      │
 └────────────────────────────────────┘                │ 2. Atualização do Modelo Global      │
                                                       └──────────────────┬───────────────────┘
                                                                          │
                                                                          ▼
                                                       ┌──────────────────────────────────────┐
                                                       │ 3. MÓDULO DE AUDITORIA POR CLASSE     │
                                                       │    (Avaliação em Dataset Central)     │
                                                       ├──────────────────────────────────────┤
                                                       │ • Acurácia Global (Visão Tradicional) │
                                                       │ • Matriz de Confusão 10x10 (Realidade)│
                                                       │ • Recall por Classe & Backdoor ASR   │
                                                       └──────────────────────────────────────┘
```

---

## 📖 4. Fundamentação Teórica dos Ataques e Defesas

### 4.1. Taxonomia de Ataques Furtivos
1. **Targeted Backdoor**: O invasor troca secretamente o rótulo da classe de interesse ($y_{source} \rightarrow y_{target}$) nos seus dados locais. A IA atinge ~90% de acurácia global, mas o recall na classe alvo vai a zero.
2. **Trigger Patch**: Injeta uma máscara de pixels $\Delta$ associada à classe alvo. Imagens limpas são classificadas normalmente; imagens com a marca ativam o erro induzido.
3. **Distributed Backdoor (DBA)**: Vários clientes colaborativos injetam partes fragmentadas do gatilho para parecerem clientes limpos individualmente.
4. **Constrained Model Replacement**: O invasor amplifica seu gradiente com restrição de norma $\lambda \|w - w_{global}\|_2^2$ para não ser cortado por filtros de norma.

### 4.2. Por que a Distância Euclidiana ($L_2$) Falha sob Non-IID?
Defesas clássicas (Krum, Bulyan) calculam $d(u, v) = \|u - v\|_2 = \sqrt{\sum (u_i - v_i)^2}$.
* Em ataques brutos, todas as dimensões mudam $\rightarrow$ Detectado.
* Em ataques furtivos, apenas dimensões da classe vítima mudam sutilmente $\rightarrow$ A distância global $L_2$ permanece dentro dos limites normais.
* Sob dados Non-IID ($\alpha = 0.1$), clientes honestos legítimos têm gradientes muito mais distantes entre si do que a perturbação do atacante furtivo, gerando descarte indevido de dados legítimos (*falsos positivos*).

---

## 🧪 5. Perguntas de Investigação (RQs) e Bateria de Testes

### Perguntas de Investigação:
* **RQ1**: Qual a magnitude do ponto cego das métricas globais sob taxas crescentes de backdoor?
* **RQ2**: Por que defesas geométricas (`Krum`, `Bulyan`) falham sob assimetria Non-IID ($\alpha = 0.1$)?
* **RQ3**: Qual o impacto de épocas locais (`local-epochs=1` vs `5`) na fixação do backdoor?
* **RQ4**: Como a auditoria por matriz de confusão identifica o ataque logo na 1ª rodada?

### Bateria dos 4 Experimentos Enxutos:
```powershell
$env:PYTHONIOENCODING="utf-8"

# 1. Baseline e Prova da Falsa Segurança (FedAvg com Targeted Backdoor)
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=1 num-server-rounds=10"

# 2. Falha das Defesas Convencionais em Non-IID (Krum e Bulyan sob alpha=0.1)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"

# 3. Ataque por Padrão de Gatilho Físico (Trigger Patch no Bulyan)
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='trigger_patch' poison_rate=0.4 num-server-rounds=10"

# 4. Validação da Auditoria por Classe (Matriz de Confusão no Servidor)
```

---

## 📊 6. Figuras Científicas e Estimativa de Esforço

### Figuras do Manuscrito:
1. **Figura 1 (Curva Temporal de Divergência)**: Linha da Acurácia Global (~90%) sobreposta à linha da Acurácia da Classe Alvo (0%).
2. **Figura 2 (Heatmap da Matriz de Confusão)**: Matriz 10x10 mostrando o desvio de predições da Classe Vítima.
3. **Figura 3 (Comparativo de ASR)**: Gráfico de barras da Taxa de Sucesso do Ataque entre os métodos.

### Quadro de Esforço Real:
* **Dificuldade Técnica**: **Baixa a Média (Nota 3 / 10)**.
* **Repositório Atual**: **80% a 85% Concluído**.
* **Tempo Direto do Pesquisador**: **~4 a 6 horas** (ajustes pontuais em `task.py`/`server_app.py`, coleta de gráficos e análise).
* **Tempo de Computador**: ~3 a 4 horas de execução autônoma.
* **Tempo para Redação**: 1 a 2 semanas.

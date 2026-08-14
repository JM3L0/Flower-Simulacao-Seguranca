# 🗺️ 00: Índice Geral da Pesquisa & Roteiro do Orientador

Este documento é o **ponto de entrada unificado** para o planejamento acadêmico da pesquisa sobre **Ataques Furtivos e Auditoria em Aprendizado Federado (Flower + PyTorch)**.

---

## 🎯 1. A Tese Central da Pesquisa (Artigo 1)

O foco primário do trabalho é realizar um **estudo comparativo rigoroso** entre:
1. **Métodos de Agregação Convencionais (Grupo A)**: Métodos que **NÃO** levam em conta ataques furtivos (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`). Avaliam apenas distâncias euclidianas globais ou a acurácia agregada, sofrendo com um ponto cego crítico e falhando sob assimetria Non-IID.
2. **Métodos e Defesas Conscientes de Furtividade (Grupo B)**: Mecanismos que **LEVAM** em conta ataques furtivos (`FoolsGold`, `FLAME`, `RLR`, `DeepSight` e a nossa proposta de **Auditoria por Matriz de Confusão e Recall por Classe no Servidor**).

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             ESTRUTURA COMPARATIVA DA PESQUISA                            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      ▼                                                                             ▼
[ GRUPO A: IGNORAM ATAQUES FURTIVOS ]                      [ GRUPO B: CONSIDERAM ATAQUES FURTIVOS ]
• Algoritmos: FedAvg, FedMedian, Krum, Bulyan              • Algoritmos: FoolsGold, FLAME, RLR, DeepSight
• Como operam: Distância euclidiana (L2)                   • Como operam: Similaridade de cosseno, taxa
  ou média simples dos gradientes.                           dinâmica por coordenada e recall por classe.
• O Problema: 90% de acurácia global com                   • O Resultado: Isola e neutraliza o backdoor
  0% de acurácia na classe vítima (ponto cego).              sem degradar a tarefa principal.
```

---

## 💬 2. Roteiro e Pitch para o Orientador

Use este roteiro para explicar a ideia e a relevância científica do projeto de forma direta:

> *"Professor, o foco central da nossa pesquisa é demonstrar uma vulnerabilidade crítica de monitoramento e defesa no Aprendizado Federado.*
>
> *Hoje, plataformas de FL monitoram o treino apenas pela **acurácia global agregada**. Em ataques de backdoor furtivos (`targeted_backdoor` ou `trigger_patch`), o invasor destrói apenas uma classe específica. O servidor reporta **90% de acurácia global**, criando uma **falsa sensação de segurança** enquanto a classe vítima foi totalmente corrompida.*
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

## 🗂️ 4. Mapa dos Documentos Desta Pasta (`docs/pesquisa/`)

Os documentos estão organizados na sequência ideal de estudo e execução:

| Arquivo | Título | Objetivo |
|---|---|---|
| **[00_indice_pesquisa_e_roteiro.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/pesquisa/00_indice_pesquisa_e_roteiro.md)** | **Índice & Roteiro** *(Este arquivo)* | Visão executiva, tese comparativa e pitch para o orientador. |
| **[01_fundamentacao_ataques_e_defesas_furtivas.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/pesquisa/01_fundamentacao_ataques_e_defesas_furtivas.md)** | **Fundamentação Teórica** | Taxonomia dos ataques furtivos, defesas existentes e por que a distância euclidiana falha. |
| **[02_pesquisa_bibliografica_e_prompts.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/pesquisa/02_pesquisa_bibliografica_e_prompts.md)** | **Levantamento Bibliográfico** | Prompt mestre para IA, strings booleanas para Google Scholar e matriz de fichamento. |
| **[03_plano_experimental_e_dificuldade.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/pesquisa/03_plano_experimental_e_dificuldade.md)** | **Execução & Experimentos** | As 4 RQs, bateria dos 4 experimentos, métricas, gráficos e análise de esforço real. |
| **[04_pipeline_futuro_artigo2_benchmark.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/pesquisa/04_pipeline_futuro_artigo2_benchmark.md)** | **Pipeline & Artigo 2** | Cronograma de 4 semanas e planejamento do Artigo 2 (Benchmark Fatorial $7 \times 4 \times 3$). |

# 🧪 03: Plano Experimental, Métricas e Dificuldade Real (Artigo 1)

Este documento detalha o **desenho experimental completo**, as **Perguntas de Investigação (RQs)**, a **bateria dos 4 testes no Flower**, as **figuras científicas** e a análise sincera de **dificuldade e tempo de execução**.

---

## 🎯 1. Título e Perguntas de Investigação (Research Questions)

### Título Sugerido:
* **Português**: *Resiliência a Backdoors Furtivos: Medindo a Vulnerabilidade por Classe e Auditando a Falsa Segurança de Métricas Globais em Aprendizado Federado*
* **Inglês**: *Stealthy Backdoor Resilience: Quantifying Per-Class Vulnerability and Auditing False Safety of Global Metrics in Federated Learning*

### Perguntas de Investigação:
* **RQ1**: Qual a magnitude do ponto cego das métricas globais agregadas sob diferentes taxas de envenenamento furtivo?
* **RQ2**: Por que defesas bizantinas geométricas (`Krum`, `Bulyan`, `FedMedian`) falham em filtrar gradientes de backdoors furtivos em ambientes heterogêneos ($\alpha = 0.1$)?
* **RQ3**: Qual o impacto da carga computacional local (`local-epochs=1` vs `local-epochs=5`) na fixação do backdoor nos tensores?
* **RQ4**: Como a auditoria por matriz de confusão em tempo real no servidor identifica e isola a contaminação nas primeiras rodadas de treino?

---

## 🧪 2. Metodologia e Bateria de 4 Experimentos Enxutos

A bateria de testes do Artigo 1 é enxuta e direta no terminal PowerShell:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

### Experimento 1: A Prova da Falsa Sensação de Segurança (Baseline FedAvg)
* **Objetivo**: Demonstrar que a acurácia global permanece em ~90% enquanto a classe alvo cai para 0%.
* **Comando**:
  ```powershell
  flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=1 num-server-rounds=10"
  ```

### Experimento 2: A Falha das Defesas Convencionais sob Non-IID
* **Objetivo**: Mostrar que `FedMedian`, `Krum` e `Bulyan` não conseguem filtrar o backdoor quando os dados são heterogêneos ($\alpha = 0.1$).
* **Comandos**:
  ```powershell
  flwr run . --stream --run-config "defense_mode='Krum' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
  flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=10"
  ```

### Experimento 3: Ataque por Padrão de Gatilho Físico (Trigger Patch)
* **Objetivo**: Avaliar a fixação do padrão de trigger físico no modelo sob a defesa `Bulyan`.
* **Comando**:
  ```powershell
  flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='trigger_patch' poison_rate=0.4 num-server-rounds=10"
  ```

### Experimento 4: Validação do Módulo de Auditoria por Classe
* **Objetivo**: Demonstrar que o monitoramento por matriz de confusão no servidor detecta e expõe a corrupção da classe alvo na 1ª rodada de agregação.

---

## 📊 3. Métricas e Entregáveis Visuais (Figuras do Artigo)

### Métricas Coletadas:
1. **Acurácia Global Top-1**: Taxa de acerto geral em todas as 10 classes do CIFAR-10.
2. **Target Class Recall**: Percentual de acertos específicos na classe atacada (ex: Classe 3).
3. **Attack Success Rate (ASR)**: Percentual de imagens com trigger/backdoor classificadas com sucesso como a classe alvo.
4. **Matriz de Confusão 10x10**: Mapeamento completo dos desvios de predição entre todas as classes.

### Figuras Científicas a Serem Geradas (`plotar_resultados.py`):
* **Figura 1 (Curva Temporal de Divergência - O Gráfico Chave)**: Sobreposição de duas linhas — Acurácia Global (~90%) vs. Acurácia da Classe Alvo (0%).
* **Figura 2 (Heatmap da Matriz de Confusão)**: Matriz 10x10 ilustrando a concentração anômala de predições da Classe 3 desviadas para a Classe 5.
* **Figura 3 (Comparativo de ASR)**: Gráfico de barras comparando a Taxa de Sucesso do Ataque entre `FedAvg`, `FedMedian`, `Krum`, `Bulyan` e o Módulo de Auditoria.

---

## ⚖️ 4. Análise de Dificuldade Real e Estimativa de Horas

```text
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                PASSO A PASSO DE EXECUÇÃO                                │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
       ┌───────────────────────┬───────────────┴───────────────┬───────────────────────┐
       ▼                       ▼                               ▼                       ▼
  [ ETAPA 1: CÓDIGO ]    [ ETAPA 2: TESTES ]            [ ETAPA 3: GRÁFICOS ]   [ ETAPA 4: REDAÇÃO ]
  • Ajustar task.py      • Rodar 4 comandos no CLI       • Gerar Curva Temporal  • Redigir o artigo
    e server_app.py        (PowerShell).                   e Matriz Heatmap        em formato IEEE
  • Tempo: ~1 hora.      • Tempo: ~30m setup + 4h PC.    • Tempo: ~2 horas.      • Tempo: 1-2 semanas.
```

### Quadro Geral de Esforço:
* **Nível de Dificuldade Técnica**: **Baixa a Média (Nota 3 / 10)**
* **Estado do Repositório**: **80% a 85% Concluído** (framework Flower, ataques e defesas já implementados).
* **Tempo Direto do Pesquisador**: **~4 a 6 horas** (divididas entre ajustes pontuais de código, coleta de gráficos e interpretação).
* **Tempo de Computador (Autônomo)**: ~3 a 4 horas de simulação em segundo plano.
* **Tempo para Redação do Manuscrito**: 1 a 2 semanas.

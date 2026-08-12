# 🛠️ Guia Sincero de Implementação & Dificuldade Real do Artigo 1

Este documento apresenta uma análise transparente e sincera sobre a **dificuldade real**, o **passo a passo de execução** e a **estimativa de tempo** para a realização do Artigo 1 (*Resiliência a Backdoors Furtivos & Auditoria Por Classe no Flower*).

---

## 📊 Avaliação Geral de Dificuldade

* **Nível de Dificuldade Técnica**: **Baixa a Média (Nota 3 / 10)**
* **Estado do Repositório**: **80% a 85% Concluído**
* **Tempo Total de Trabalho Direto do Pesquisador**: **~4 a 6 horas** (divididas entre código, gráficos e análise).
* **Tempo Estimado para Redação Final**: **1 a 2 semanas**.

---

## 🗺️ Mapa de Execução em 4 Etapas

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

---

### 1. Etapa 1: Ajuste de Código (~1 hora de trabalho)
Como o repositório Flower já possui os ataques, defesas e suporte Dirichlet implementados, o ajuste necessário é mínimo:
* **Em `task.py`**: Adicionar a função `test_per_class(net, testloader, device)` para contabilizar o número de acertos em cada uma das 10 classes do CIFAR-10.
* **Em `server_app.py`**: Atualizar a rotina `global_evaluate` para chamar a contagem por classe e registrar a matriz de confusão no arquivo JSON exportado em `metrics_json/`.

---

### 2. Etapa 2: Execução dos Experimentos (~30m setup / ~3-4h execução autônoma)
Execução de 4 cenários no terminal/PowerShell sem necessidade de supervisão constante:
1. **Cenário Baseline**: `FedAvg` sem ataque (controle).
2. **Cenário Falsa Segurança**: `targeted_backdoor` no `FedAvg` (troca de rótulo Classe 3 -> 5) com `poison_rate=0.4`.
3. **Cenário Colapso de Defesas**: O mesmo ataque trocando a defesa para `Bulyan` e `Krum` sob `dirichlet_alpha=0.1` (Non-IID).
4. **Cenário Trigger Físico**: Ataque `trigger_patch` no `Bulyan`.

---

### 3. Etapa 3: Geração de Gráficos em Python (~2 horas de trabalho)
Atualização do script `plotar_resultados.py` para gerar as 3 figuras científicas do artigo:
1. **Figura 1 (Curva Temporal de Divergência - O Gráfico Chave)**: Linha da Acurácia Global (~90%) sobreposta à linha da Acurácia da Classe Alvo 3 (que cai para 0%).
2. **Figura 2 (Heatmap da Matriz de Confusão)**: Matriz 10x10 demonstrando o desvio dos acertos da Classe 3 para a Classe 5.
3. **Figura 3 (Comparativo de ASR)**: Gráfico de barras comparando a Taxa de Sucesso do Ataque entre `FedAvg`, `FedMedian`, `Krum` e `Bulyan`.

---

### 4. Etapa 4: Redação Científica (1 a 2 semanas)
Redação e estruturação do manuscrito acadêmico em formato IEEE:
1. **Abstract / Resumo**: 200 palavras sintetizando o problema e a contribuição do módulo de auditoria.
2. **Introdução**: Relevância do FL, ponto cego do MLOps e justificativa da pesquisa.
3. **Trabalhos Relacionados**: Revisão de literatura sobre defesas bizantinas e backdoors.
4. **Metodologia**: Detalhamento da arquitetura Flower, particionamento Dirichlet e Auditoria Por Classe.
5. **Resultados e Discussão**: Inserção das Figuras 1, 2 e 3 com análise crítica das Perguntas de Investigação (RQs).
6. **Conclusão**: Fechamento e direcionamentos futuros.

---

## ⚖️ Quadro Geral de Esforço

| Tarefa | Dificuldade | Seu Tempo Direto | Esforço do Computador |
|---|:---:|:---:|:---:|
| **1. Código no Flower** | 🟢 Muito Baixa | ~1 hora | Nulo |
| **2. Execução de Testes** | 🟢 Baixa | ~30 minutos | ~3 a 4 horas (sozinho) |
| **3. Gerar Gráficos** | 🟡 Média | ~2 horas | Nulo |
| **4. Redação do Artigo** | 🟡 Média | ~1 a 2 semanas | Nulo (com suporte de IA) |

---

## 💡 Veredito Final
A execução é **altamente viável e realista**. Como a base computacional em Flower + PyTorch já está construída no repositório, o trabalho prático é extremamente enxuto, deixando a maior parte do tempo dedicada à análise dos resultados e redação do texto.

# 💎 Módulo 2: Análise Experimental e Experimentos Diamantes

Este documento descreve o projeto de experimentos estatísticos (ANOVA), a caracterização dos 4 cenários empíricos fundamentais e a seleção dos **Experimentos Diamantes** — os testes de maior impacto e valor científico para destacar no seu artigo.

---

## 🔬 1. Projeto de Experimentos (ANOVA Multidimensional)

Para fornecer rigor científico, os testes seguem um design de análise fatorial multidimensional:

* **Fator A**: Tipo de Ataque (7 níveis)
* **Fator B**: Estratégia de Defesa (4 níveis)
* **Fator C**: Heterogeneidade de Dirichlet (5 níveis: `0.1`, `0.5`, `1.0`, `10.0`, `100.0`)
* **Replicações**: 3 a 5 execuções independentes por célula com sementes controladas para geração de Intervalo de Confiança de 95% (\(p < 0.05\)).

---

## 🎯 2. Os 4 Cenários Experimentais Principais

### Cenário 1: Curva de Colapso (Sensibilidade ao `poison_rate`)
* **Objetivo**: Medir a degradação da acurácia global à medida que a taxa de envenenamento aumenta (\(poison\_rate \in \{0.0, 0.1, 0.2, 0.3, 0.5, 1.0\}\)).
* **Expectativa**: O `FedAvg` entra em declínio linear ou exponencial, enquanto o `Bulyan` mantém estabilidade até atingir a capacidade máxima de tolerância bizantina.

### Cenário 2: Morte Súbita (Análise Temporal sob `gradient_ascent`)
* **Objetivo**: Avaliar a resiliência do servidor a ataques de severidade máxima ao longo das rodadas (\(num-server-rounds=10\)).
* **Expectativa**: O `FedAvg` colapsa para acurácia aleatória (~10%) na 1ª rodada. O `FedMedian` sofre degradação parcial, enquanto o `Krum` e o `Bulyan` contêm a falha.

### Cenário 3: Névoa de Guerra (Impacto do `dirichlet_alpha` em Non-IID)
* **Objetivo**: Avaliar a taxa de falsos positivos em defesas geométricas quando os dados dos clientes são altamente heterogêneos (\(dirichlet\_alpha \in \{100.0, 1.0, 0.1\}\)).
* **Expectativa**: Em \(alpha=0.1\), o `Krum` sofre queda severa de desempenho porque confunde gradientes de clientes legítimos especializados com atuações de nós invasores.

### Cenário 4: Ataques Furtivos (Backdoors por Classe)
* **Objetivo**: Demonstrar como ataques do tipo `targeted_backdoor` e `trigger_patch` mantêm a acurácia global alta no servidor central, mas destroem a acurácia da classe atacada.

---

## 💎 3. Seleção dos "Experimentos Diamantes" (Alto Impacto)

Estes são os testes específicos cujos resultados empíricos produzem os gráficos mais impactantes para figuras do artigo:

```text
💎 DIAMANTE 1: "O Colapso da Confiança no Krum sob Heterogeneidade"
   Comando: defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=0.1
   Por que é importante: Prova matematicamente que o Krum falha quando aplicado em ambientes 
   hospitalares ou móbiles reais (Non-IID extremo).

💎 DIAMANTE 2: "A Superioridade Bizantina do Bulyan"
   Comando: defense_mode='Bulyan' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=0.1
   Por que é importante: Mostra o Bulyan contendo a substituição desproporcional de modelo mesmo 
   na presença da névoa de guerra.

💎 DIAMANTE 3: "O Ataque Invisível do Backdoor Direcionado"
   Comando: defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.5 local-epochs=3
   Por que é importante: Gera a prova empírica de que métricas gerais de validação cega não 
   detectam envenenamento direcionado de classes.
```

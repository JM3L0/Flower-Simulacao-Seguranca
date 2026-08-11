# 🧪 Caminho 1: Ideias de Artigos Científicos Empíricos (Sem SPN)

Este guia detalha **5 propostas completas de artigos de pesquisa empírica** utilizando o simulador Flower + PyTorch, incluindo avaliação crítica rigorosa (Notas de 0 a 10, Nível de Dificuldade e Prazos).

---

## 💡 Ideia 1: A Névoa de Guerra Non-IID — Desmistificando a Falha de Defesas Bizantinas Geométricas em Distribuições Assimétricas

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 9.0 / 10**
* **Nível de Dificuldade: Baixa-Média** | **Prazo Estimado: 1 a 2 semanas**
* **Análise de Validade**: **Extremamente Válida.** Revisores de conferências de redes e segurança valorizam artigos que demonstram empírica e quantitativamente que defesas clássicas (Krum, Bulyan) falham na prática sob assimetria Non-IID. O conceito de "falsos positivos" (descarte indevido de gradientes exóticos mas legítimos) é uma contribuição científica muito forte.
* **Justificativa da Nota**: Problema real e urgente no ecossistema FL que o simulador executa nativamente. Só não é 10.0 porque a heterogeneidade isolada já é um tema discutido, mas o gancho da *névoa de guerra em defesas geométricas* é excelente.

### 1. Título Sugerido
* **Português**: *A Névoa de Guerra Non-IID: Desmistificando a Falha de Defesas Bizantinas Geométricas em Distribuições Assimétricas em Aprendizado Federado*
* **Inglês**: *The Non-IID Fog of War: Unveiling the Breakdown of Geometric Byzantine Defenses Under Asymmetric Data Distributions in Federated Learning*

### 2. Contexto e Lacuna na Literatura
A maioria das defesas Bizantinas baseadas em geometria euclidiana (como o `Krum` e o `Bulyan`) foi avaliada em dados homogêneos (IID). Na prática (silos de dados em hospitais ou celulares), os clientes possuem distribuições de classes muito diferentes. A lacuna consiste em demonstrar como a assimetria legítima de dados faz com que o servidor confunda clientes honestos especializados com invasores bizantinos.

### 3. Perguntas de Investigação
* Qual é o limiar exato do parâmetro `dirichlet_alpha` em que o algoritmo Krum perde a capacidade de distinguir clientes legítimos de maliciosos?
* Qual é a Taxa de Falsos Positivos de Descarte (FPR) de clientes honestos em cenários de assimetria extrema?

### 4. Metodologia e Comandos no Simulador
Executar matriz comparativa das 4 defesas variando `dirichlet_alpha` de `100.0` (IID) até `0.1` (Non-IID Extremo):

```powershell
$env:PYTHONIOENCODING="utf-8"
# 1. Krum em ambiente IID (Controle)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=100.0 num-server-rounds=10"

# 2. Krum em ambiente Non-IID Extremo (Névoa de Guerra)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=10"

# 3. Bulyan em ambiente Non-IID Extremo
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=10"
```

### 5. Métricas e Gráficos
* **Métricas**: Acurácia Global Final, Loss de Validação, Taxa de Falsos Positivos de Seleção.
* **Gráficos**: Curva de acurácia x rodadas sobrepondo α=100.0 vs α=0.1; Gráfico de barras de descarte de gradientes legítimos.

### 6. Periódicos / Conferências Alvo
* *IEEE Transactions on Information Forensics and Security (TIFS)*
* *IEEE Cluster / CCGrid*
* *Computers & Security (Elsevier)*

---

## 💡 Ideia 2: Resiliência a Backdoors Furtivos — Medindo a Vulnerabilidade por Classe em Aprendizado Federado

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 9.5 / 10**
* **Nível de Dificuldade: Média** | **Prazo Estimado: 2 semanas**
* **Análise de Validade**: **Altíssima Validade.** Ataques furtivos (`targeted_backdoor` e `trigger_patch`) representam o tema mais crítico em Aprendizado Federado. Provar que os painéis globais do Flower "mentem" (mostram 90% de acurácia global enquanto uma classe específica é destruída) e propor um módulo de auditoria por matriz de confusão (*Per-Class Verification*) traz contribuição prática imediata.
* **Justificativa da Nota**: Resolve uma ponto cego dos dashboards de MLOps atuais e propõe uma ferramenta de auditoria concreta. Exige apenas adicionar um script leve em `server_app.py` para calcular a matriz de confusão por classe.

### 1. Título Sugerido
* **Português**: *Resiliência a Backdoors Furtivos: Medindo a Vulnerabilidade por Classe sob Ataques de Disparador Físico em Aprendizado Federado*
* **Inglês**: *Resilience to Stealthy Backdoors: Measuring Per-Class Vulnerability Under Physical Trigger Attacks in Federated Learning*

### 2. Contexto e Lacuna na Literatura
Ataques do tipo `targeted_backdoor` e `trigger_patch` subvertem secretamente uma única classe (ex: alterar imagens de placas de trânsito específicas) sem reduzir a acurácia global centralizada. Os relatórios padrão de validação do Flower falham em alertar o administrador do sistema.

### 3. Perguntas de Investigação
* Quão invisível é um ataque de trigger patch para métricas de validação globais?
* Como a variação do treinamento local (`local-epochs`) altera a taxa de sucesso do backdoor?

### 4. Metodologia e Comandos no Simulador
```powershell
$env:PYTHONIOENCODING="utf-8"
# 1. Backdoor Direcionado com 1 época local
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=1 num-server-rounds=10"

# 2. Backdoor Direcionado com 5 épocas locais (Fixação profunda nos tensores)
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=5 num-server-rounds=10"

# 3. Teste do mesmo backdoor sob a defesa Bulyan
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 local-epochs=5 num-server-rounds=10"
```

### 5. Métricas e Proposição
* **Proposição de Solução**: Criar um módulo de auditoria em `server_app.py` que calcula a **Matriz de Confusão por Classe** a cada rodada.
* **Métrica**: Acurácia Geral vs. Acurácia da Classe Alvo (*Target Class Accuracy*).

### 6. Periódicos / Conferências Alvo
* *ACM Workshop on Privacy in the Electronic Society (WPES)*
* *IEEE Access*
* *Journal of Information Security and Applications (Elsevier)*

---

## 💡 Ideia 3: O Impacto da Carga Computacional do Cliente (Local Epochs) na Profundidade de Contaminação de Tensores

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 7.0 / 10**
* **Nível de Dificuldade: Baixa** | **Prazo Estimado: 1 semana**
* **Análise de Validade**: **Válida, porém Limitada.** Medir como o aumento de `local-epochs` afeta a persistência é relevante, mas revisores de veículos *Top-Tier* podem interpretar como uma simples análise de sensibilidade de hiperparâmetros.
* **Justificativa da Nota**: Muito fácil e rápida de executar no simulador, mas falta um elemento de inovação algorítmica para um Qualis A1. É ideal para workshops ou periódicos de escopo médio (ex: IEEE Access).

### 1. Título Sugerido
* **Português**: *O Impacto das Épocas Locais de Treinamento na Persistência de Envenenamento de Gradientes em Aprendizado Federado*
* **Inglês**: *Impact of Local Training Epochs on Gradient Poisoning Persistence in Federated Learning*

### 2. Contexto e Lacuna na Literatura
A maioria das pesquisas assume `local-epochs=1`. Porém, quando nós maliciosos executam múltiplas épocas locais (`local-epochs=5` a `10`), o viés corrompido ganha maior "massa topológica" nos tensores da rede neural, tornando a recuperação do modelo global muito mais demorada após a expulsão do atacante.

### 3. Perguntas de Investigação
* Quantas rodadas limpas são necessárias para expurgar um envenenamento gerado com `local-epochs=5` vs `local-epochs=1`?
* A mediana coordenada (`FedMedian`) consegue mitigar a contaminação quando o viés local é profundo?

### 4. Metodologia e Comandos no Simulador
```powershell
$env:PYTHONIOENCODING="utf-8"
foreach ($epochs in 1, 3, 5, 10) {
    flwr run . --stream --run-config "defense_mode='FedMedian' attack_type='gradient_ascent' poison_rate=1.0 local-epochs=$epochs num-server-rounds=10"
}
```

### 5. Métricas e Gráficos
* **Métrica**: *Recovery Rounds* (Número de rodadas até a acurácia retornar ao nível de 90% do baseline).
* **Gráfico**: Tempo de recuperação x Número de Épocas Locais.

### 6. Periódicos / Conferências Alvo
* *IEEE International Conference on Data Mining (ICDM)*
* *Neurocomputing (Elsevier)*

---

## 💡 Ideia 4: Free-Riders e Parasitagem em Federações Móveis — Medindo o Atraso de Convergência Sem Contaminação Direta

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 8.0 / 10**
* **Nível de Dificuldade: Baixa-Média** | **Prazo Estimado: 1 a 2 semanas**
* **Análise de Validade**: **Muito Válida.** A maioria dos trabalhos foca apenas em ataques destrutivos (Poisoning), ignorando a parasitagem econômica (`free_rider`). Em redes móbiles e edge computing, demonstrar o atraso de convergência (*Convergence Delay*) e o consumo desnecessário de bateria imposto aos nós honestos possui forte justificativa prática.
* **Justificativa da Nota**: Tema muito relevante para conferências de redes móveis (IEEE TMC / ACM DLT). O simulador já possui a rotina `free_rider` pronta em `attacks.py`.

### 1. Título Sugerido
* **Português**: *Free-Riders e Parasitagem em Federações Edge: Medindo o Atraso de Convergência e Desperdício Energético*
* **Inglês**: *Free-Riders in Edge Federations: Quantifying Convergence Delay and Overhead Energy Waste*

### 2. Contexto e Lacuna na Literatura
Em redes federadas móveis (IoT, smartphones), dispositivos maliciosos/egoístas praticam o ataque `free_rider` (não treinam e devolvem parâmetros nulos para economizar bateria). Embora não destroem a acurácia, eles desaceleram a convergência da IA e fazem os clientes honestos gastarem mais bateria compensando a falta de contribuição.

### 3. Perguntas de Investigação
* Qual é o atraso relativo de convergência (*Convergence Delay*) provocado por 10%, 30% e 50% de nós Free-Riders?
* Qual é o impacto financeiro/energético indireto imposto aos nós honestos?

### 4. Metodologia e Comandos no Simulador
```powershell
$env:PYTHONIOENCODING="utf-8"
# 1. Federação 100% Honesta (Controle)
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=15"

# 2. Federação com 30% de Free-Riders
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='free_rider' poison_rate=0.3 num-server-rounds=15"

# 3. Federação com 50% de Free-Riders
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='free_rider' poison_rate=0.5 num-server-rounds=15"
```

### 5. Métricas e Gráficos
* **Métricas**: Número de rodadas para atingir acurácia limite (ex: 80%), Throughput de banda de comunicação total consumida.

### 6. Periódicos / Conferências Alvo
* *IEEE Transactions on Mobile Computing (TMC)*
* *ACM Distributed Ledger Technologies (DLT)*

---

## 💡 Ideia 5: Benchmark Fatorial Abrangente — Matriz Global de Ataques Bizantinos e Defesas em PyTorch

### 🏆 Avaliação Acadêmica (Peer-Review)
* **Nota: 8.5 / 10**
* **Nível de Dificuldade: Média** | **Prazo Estimado: 2 a 3 semanas**
* **Análise de Validade**: **Válida e com Alto Potencial de Citações.** Artigos do tipo *Benchmark & Survey Empírico* costumam receber muitas citações, pois servem de referência para outros pesquisadores justificarem suas escolhas de defesa.
* **Justificativa da Nota**: Não propõe um algoritmo novo, mas entrega um mapa completo para a comunidade. Exige rodar uma grade de testes grande com replicações e tratamento estatístico dos relatórios em JSON.

### 1. Título Sugerido
* **Português**: *Benchmark Fatorial Abrangente de Mecanismos de Defesa Bizantina sob Ataques Heterogêneos em Aprendizado Federado*
* **Inglês**: *A Comprehensive Factorial Benchmark of Byzantine Defense Mechanisms Under Heterogeneous Attacks in Federated Learning*

### 2. Contexto e Lacuna na Literatura
Há escassez de trabalhos de *Benchmark* sistemático que avaliem a matriz completa cruzando múltiplos ataques a nível de dados, gradientes e comportamento sob o mesmo framework rigoroso.

### 3. Perguntas de Investigação
* Qual defesa oferece a melhor relação entre resiliência a ataques e tempo de execução computacional?
* Existe uma estratégia única "vencedora" ou cada defesa é especializada em um tipo de ataque específico?

### 4. Metodologia e Comandos no Simulador
Execução da matriz ANOVA multidimensional completa (**7 Ataques \(\times\) 4 Defesas \(\times\) 3 Níveis de Dirichlet**):

```powershell
$env:PYTHONIOENCODING="utf-8"
# Exemplo de laço de execução para a matriz completa:
foreach ($def in "FedAvg", "FedMedian", "Krum", "Bulyan") {
    foreach ($atk in "label_flipping", "gaussian_noise", "targeted_backdoor", "gradient_ascent", "model_replacement", "free_rider") {
        flwr run . --stream --run-config "defense_mode='$def' attack_type='$atk' poison_rate=0.3 num-server-rounds=5"
    }
}
python plotar_resultados.py
```

### 5. Métricas e Gráficos
* **Métricas**: Acurácia Final, Loss, Tempo Computacional de Agregação (ms), Ranking Global de Resiliência.

### 6. Periódicos / Conferências Alvo
* *IEEE Access*
* *Journal of Systems Architecture (Elsevier)*

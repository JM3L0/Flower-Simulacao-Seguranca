# Explicação Detalhada do Painel de Controle (Terminal)

O comando de execução do Flower (`flwr run . --run-config '...'`) atua como o **painel de controle central** do simulador. Com ele, você sobrescreve dinamicamente as variáveis de configuração definidas no arquivo `pyproject.toml` sem precisar editar o código-fonte manualmente.

Abaixo, detalhamos todas as 9 variáveis principais do projeto, suas interações matemáticas na segurança federada e exemplos de cenários de uso via terminal.

---

## 1. Variáveis de Segurança (O Ataque e o Escudo)

Estas variáveis regem o grau de hostilidade do ambiente em que o sistema de aprendizagem federado (FL) opera.

### `poison_rate` (Float)
A **força bruta** do ataque. Varia de `0.0` (nenhum) até `1.0` (100% dos dados corrompidos).
* **O que faz:** Controla a fração exata de amostras que o cliente malicioso vai subverter matematicamente dentro do seu próprio treinamento local *antes* de tentar enviar seu gradiente mentiroso para o servidor central.

### `attack_type` (String)
O **mecanismo (vetor)** do ataque. O formato *como* os dados são corrompidos localmente.
* **`"label_flipping"`:** Ataque de *integridade da classificação*. O cliente mantém as imagens intactas, mas engana a rede mudando seus gabaritos (ex: enviando uma foto de cachorro mas dizendo ao modelo que era um avião). Força a rede a aprender correspondências falhas.
* **`"gaussian_noise"`:** Ataque a *nível de features*. O cliente mantém os gabaritos corretos, mas injeta estática extrema (ruído gaussiano) nas imagens. Age como se tentar "cegar o aprendizado" ou simula dados vindos de sensores defeituosos.

### `defense_mode` (String)
O **escudo** do servidor agregador. Como a autoridade central reage ao receber gradientes dos hospedeiros.
* **`"FedAvg"`:** Zero defesa. Aceita tudo ingenuamente e tira a média geral. Representa a fragilidade do modelo baseline tradicional.
* **`"FedMedian"`:** Usa a Mediana coordenada-a-coordenada. Robusto por design, pois ignora picos de pesos extremos sem a necessidade matemática de conhecer antemão quantos clientes eram atacantes.
* **`"Bulyan"`:** Mecanismo avançado de defesa bizantina. Um meta-algoritmo que seleciona ativamente os modelos usando a regra de Krum e depois apara os extremos ("trimmed mean").

#### 🛑 Como elas interagem?
As variáveis `attack_type` e `defense_mode` dançam juntas. O tipo do ataque define como a matemática do vetor de pesos vai flutuar, enquanto a defesa define como o servidor tentará ancorá-la. A variável `poison_rate` age como um multiplicador empurrando contra a estabilidade da defesa escolhida. 

> **Exemplo Prático (Guerra de Defesa):**
> ```bash
> !flwr run . --run-config 'defense_mode="FedMedian" attack_type="label_flipping" poison_rate=0.5'
> ```
> *Análise:* "Quão longe o algoritmo de Mediana consegue segurar a acurácia global se eu destruir subitamente os rótulos de exatos 50% dos dados?"

---

## 2. A Variável de Distribuição Geográfica (Dificuldade Real)

### `dirichlet_alpha` (Float)
Controla a **heterogeneidade (distribuição Non-IID)** entre os clientes. Modela o comportamento autêntico do mundo real, onde dados não são perfeitamente distribuídos.

* **`100.0` (Quase IID):** Cenário homogêneo. Todo cliente reteve dados diversificados e tem proporções perfeitamente iguais de todas as classes avaliadas.
* **`1.0` (Levemente Heterogêneo):** Cenário de desbalanceamento normal e orgânico.
* **`0.1` (Non-IID Extremo):** Cenário radical, similar a silos demográficos distintos. O "Cliente A" por sorte coletou exclusivamenete fotos de cavalos, e o "Cliente B", somente fotos de bicicletas.

#### 🛑 Como ela interage com a Segurança?
O `dirichlet_alpha` atua como um regulador da "névoa de guerra" para algoritmos de defesa. 
Se a homogeneidade é alta (`100.0`), anomalias saltam aos olhos do servidor: um gradiente subvertido é obvio perante os vizinhos que possuem uma distribuição idêntica de classes originais. 
Contudo, se a heterogeneidade for aguda (`0.1`), **todos os gradientes enviados parecerão drasticamente diferentes e ruidosos** (porque cada pessoa treinou em um conteúdo completamente diferente). Disntinguir ataque de dados genuinamente ímpares torna-se extremamente desafiador e burla mais facilmente as defesas baseadas em limites de distribuição (como Median e Bulyan).

> **Exemplo Prático (O Cenário Pesadelo):**
> ```bash
> !flwr run . --run-config 'dirichlet_alpha=0.1 defense_mode="FedMedian" poison_rate=0.3 attack_type="label_flipping"'
> ```
> *Análise:* "Aplique o Labelflipping (30%) invisível dentro de dados extremamente independentes (0.1) e veja o algoritmo de Mediana vacilar em detectar o comportamento."

---

## 3. Variáveis Tradicionais do Motor FL (Deep Learning)

Estas controlam a dinâmica da inteligência artificial dentro da simulação.

* **`num-server-rounds` (Int):** Total de ciclos inteiros do servidor (download de pesos → treino do cliente → upload → agregar na média central). Mais rodadas significam um aprendizado perene que sofre danos menores pontuais nos ataques ou sofre acumulações severas. Padrão: `5`.
* **`local-epochs` (Int):** O grau repetitivo dos dados privados antes do upload. O perigo: se um usuário hostil tem `local-epochs=5`, seu viés envenenado adquire "gravidade" muito maior num espaço topológico do tensor, agindo como uma âncora errônea mais forte ao final da rodada no servidor. Padrão: `1`.
* **`batch-size` (Int):** Amostras ativas na memória computacional de uma vez. Padrão: `32`.
* **`learning-rate` (Float):** Distância em que a IA recua em direção ao acerto do backpropagation. Padrão: `0.1`.

> **Exemplo Prático (Ataque Profundo Local):**
> ```bash
> !flwr run . --run-config 'attack_type="gaussian_noise" poison_rate=0.4 local-epochs=5 num-server-rounds=10'
> ```
> *Análise:* "Produza danos persistentes permitindo que a IA envenenada repita a visualização do ruído e se afogue nisto, 5 vezes antes mesmo que a defesa do servidor seja ativada após as 10 rodadas gerais."

---

## 4. Guia Rápido de Sintaxe do Google Colab

Use o prefixo mágico `!` em qualquer terminal de notebooks (Colab/Jupyter). Observe atentamente os invólucros usados no *parsing* dinâmico:
* **Numéricos:** Não necessitam aspas (ex: `poison_rate=0.4`).
* **Símbolos / Nomes de Classe:** Obrigatório o uso de aspas duplas explícitas no `[tool.flwr.app.config]` (ex: `attack_type="gaussian_noise"`).
* **Escopo Geral do Flag de Comando:** O invólucro completo por fora da *string* de flags requer obrigatoriamente as aspas simples `' ... '`.

```bash
!flwr run . --run-config 'defense_mode="FedAvg" attack_type="label_flipping" poison_rate=0.3'
```

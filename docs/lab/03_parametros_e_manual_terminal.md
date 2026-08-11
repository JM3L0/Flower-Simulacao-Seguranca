# 🎛️ Capítulo 3: Manual Definitivo do Terminal e Parâmetros (`--run-config`)

Este documento é o guia oficial para operação do simulador via terminal de comando. Com a flag `--run-config`, você altera dinamicamente as variáveis de segurança, heterogeneidade e hiperparâmetros de treinamento sem precisar modificar o código Python.

---

## 1. ⚙️ O Paradigma do Fallback Silencioso

O Flower utiliza uma arquitetura modular baseada em **herança de configuração**:

```bash
flwr run .
```

* **Zero Parâmetros**: Ao rodar o comando acima sem a flag `--run-config`, o simulador lê automaticamente os 9 valores padrão definidos no arquivo de configuração raiz [`pyproject.toml`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/quickstart-pytorch/pyproject.toml).
* **Sobrescrita Cirúrgica**: Você só precisa passar via terminal as variáveis que deseja modificar no experimento atual. O restante das variáveis manterá os valores do `pyproject.toml`.

> **Exemplo**: Se você quer alterar apenas a taxa de ataque sem mexer na defesa ou nas rodadas, digite:
> ```powershell
> flwr run . --run-config "poison_rate=0.4"
> ```

---

## 📜 2. As Regras de Ouro da Sintaxe de Terminal

Para evitar erros de parsing no PowerShell ou Google Colab, siga estas 3 regras:

1. **Textos e Nomes de Classe**: Devem obrigatoriamente usar **aspas duplas** (ex: `defense_mode="Bulyan"` ou `attack_type="gradient_ascent"`).
2. **Valores Numéricos (Inteiros ou Decimais)**: Devem ser informados **sem aspas** (ex: `poison_rate=0.5` ou `num-server-rounds=10`).
3. **Escopo Global da Flag**: Toda a lista de parâmetros dentro de `--run-config` deve estar envolta por **aspas duplas externas** no PowerShell.

```powershell
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='label_flipping' poison_rate=0.3 dirichlet_alpha=1.0"
```

---

## 📋 3. O Painel dos 9 Parâmetros Disponíveis

### Segmento A: Cibersegurança e Ataque
1. **`defense_mode` (String)**: Algoritmo de agregação no servidor central.
   * `"FedAvg"`: Média simples (Baseline vulnerável).
   * `"FedMedian"`: Mediana por coordenada (Proteção intermediária).
   * `"Krum"`: Seleção do modelo mais próximo por distância euclidiana.
   * `"Bulyan"`: Filtro de Krum + Média Aparada (Proteção bizantina máxima).

2. **`attack_type` (String)**: Mecanismo de corrupção nos clientes.
   * `"label_flipping"`: Troca aleatória de rótulos de dados.
   * `"gaussian_noise"`: Injeção de ruído gaussiano nas imagens.
   * `"targeted_backdoor"`: Envenenamento direcionado de uma única classe.
   * `"trigger_patch"`: Inserção de patch de marcação fixa na imagem.
   * `"gradient_ascent"`: Inversão matemática do sinal de erro (`-loss`).
   * `"model_replacement"`: Multiplicação desproporcional de parâmetros (50x).
   * `"free_rider"`: Evasão de processamento local.

3. **`poison_rate` (Float)**: Fração do lote envenenada localmente (de `0.0` a `1.0`).
   * `0.0` = 0% de envenenamento (Execução limpa / Baseline).
   * `0.5` = 50% das amostras do batch corrompidas.
   * *(Nota: Ataques de Model Poisoning como `gradient_ascent` devem ser executados com `poison_rate=1.0`)*.

---

### Segmento B: Heterogeneidade e Distribuição Geográfica
4. **`dirichlet_alpha` (Float)**: Grau de assimetria dos dados entre clientes (Distribuição de Dirichlet).
   * `100.0` (Quase IID): Distribuição homogênea e esterilizada. Todos os nós possuem proporções idênticas de todas as classes.
   * `1.0` (Moderadamente Heterogêneo): Cenário padrão de variação orgânica do mundo real.
   * `0.1` (Non-IID Extremo): Distribuição altamente assimétrica ("Névoa de Guerra"). Cada cliente possui quase que exclusivamente dados de 1 ou 2 classes, dificultando a ação das defesas geométricas.

---

### Segmento C: Hiperparâmetros do Motor IA
5. **`num-server-rounds` (Int)**: Número de ciclos completos de treinamento federado (Padrão: `5`).
6. **`local-epochs` (Int)**: Quantidade de épocas de treinamento local em cada cliente antes do envio (Padrão: `1`). *(Aumentar para 3 ou 5 aprofunda a fixação de ataques de backdoor nos tensores)*.
7. **`batch-size` (Int)**: Tamanho do lote de dados processado na GPU (Padrão: `32`).
8. **`learning-rate` (Float)**: Taxa de aprendizado do otimizador SGD local (Padrão: `0.1`).
9. **`fraction-evaluate` (Float)**: Fração dos clientes acionados para avaliação distribuída (Padrão: `0.5`).

---

## ⚡ 4. O Teste de Estresse (Megacomando Simultâneo)

Para testar o limite do simulador e manipular os 9 eixos dimensionais de uma só vez:

```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "attack_type='targeted_backdoor' poison_rate=0.5 defense_mode='Bulyan' dirichlet_alpha=1.0 num-server-rounds=20 local-epochs=3 batch-size=64 learning-rate=0.01 fraction-evaluate=1.0"
```

### Dissecando a Operação:
1. **`targeted_backdoor` + `poison_rate=0.5`**: 50% dos dados dos atacantes recebem uma porta dos fundos sutil.
2. **`defense_mode='Bulyan'`**: O servidor responde com filtragem bizantina de duas camadas.
3. **`dirichlet_alpha=1.0`**: Introduz heterogeneidade moderada para testar a capacidade do Bulyan de diferenciar anomalias legítimas de ataques.
4. **`num-server-rounds=20`**: Acompanha a persistência do ataque ao longo do tempo.
5. **`local-epochs=3`**: Força o cliente malicioso a reiterar o veneno 3 vezes por rodada.
6. **`batch-size=64` + `learning-rate=0.01`**: Estabiliza o aprendizado com passos menores e batches maiores.
7. **`fraction-evaluate=1.0`**: Exige avaliação de 100% da rede ao final do ciclo.

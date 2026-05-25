# Manual de Execução e Receitas de Matrizes de Cenário

Este guia é um roteiro prático (*Playbook*) sobre como usar o painel do terminal para conduzir experimentos de Inteligência Artificial e Cibersegurança no Aprendizado Federado. Aqui você encontrará receitas prontas com comandos exatos e um glossário de tudo o que pode ser injetado.

---

## 1. A Sintaxe Fundamental

O comando universal na raiz do projeto (`quickstart-pytorch`) para executar uma super simulação é:

```bash
flwr run . --run-config 'parametro_numerico=10 parametro_de_texto="valor"'
```

**Regras de Ouro do Terminal (Colab / PowerShell):**
1. **Aspas Simples (' ... ')**: Devem envolver *toda* a lista de parâmetros.
2. **Aspas Duplas (" ... ")**: Devem envolver textos e nomes. Ex: `attack_type="bulyan"`.
3. **Sem aspas**: Devem envolver exclusivamente números. Ex: `poison_rate=0.5`.
4. **Valores Padrão**: Qualquer um dos 9 parâmetros abaixo que você não digitar no terminal assumirá automaticamente o valor base predefinido no seu arquivo `pyproject.toml`.

### O Mínimo Absoluto (Zero Parâmetros)
### O Mínimo Absoluto: Zero Parâmetros na Bateria de Testes
O `run-config` do Flower é construído de forma completamente modular, suportando "Fallback" (Retrocesso de Segurança). Isso significa que o comando absoluto mais curto que você pode rodar não tem flag nenhuma:

```bash
!flwr run .
```

**O que acontece por debaixo dos panos?**
Ao identificar que a *string* está vazia, o laboratório mergulha diretamente no arquivo de configuração raiz (`pyproject.toml`). O simulador extrai de lá todos os 9 "valores de fábrica" imediatamente. 
- Ele inicializa a inteligência central.
- Fixa o escopo de tempo (ex: `num-server-rounds=5`).
- Conecta ao escudo de segurança padrão (ex: `FedAvg`).
- Configura vetores passivos de ataque local (ex: `poison_rate=0.2`).

**O benefício acadêmico desse recurso:**
Para você testar uma única hipótese geométrica, não é preciso escrever os 9 parâmetros de novo e de novo correndo erro de digitação. Você pode focar cirurgicamente apenas na variável que deseja corromper. 
Por exemplo, se a sua tese no momento for provar que "Aumentar o learning rate anula a efetividade de um Backdoor", você escreve apenas a mutação no terminal: `!flwr run . --run-config 'learning-rate=0.5'`. Imediatamente, todo o resto do exército de variáveis se constrói automaticamente e obedece os valores-raiz do `pyproject.toml`, enquanto o `learning-rate` deforma a experiência para te dar os gráficos precisos.

---

## 2. A Lista Máxima: Todos os 9 Parâmetros Disponíveis

O sistema foi preparado para ler 9 chaves essenciais na sua string de comando (O que chamamos de Painel de Controle Dinâmico).

### Segmento A: Cibersegurança (O Jogo de Gato e Rato)
- **`defense_mode` (String)**: O escudo do servidor local.
  - `"FedAvg"`: Média simples (A vítima / Baseline sem Defesa).
  - `"FedMedian"`: Ignora os extremos das contribuições e puxa o meio (Básica/Moderada).
  - `"Bulyan"`: Algoritmo bizantino de caça por densidade métrica (Robusta/Avançada).
  - `"Krum"`: Elege 1 único modelo como representante, descartando todo o resto da média (Agressiva Matemática).

- **`attack_type` (String)**: O vetor agressivo do cliente hospedeiro.
  - `"label_flipping"`: Data Poisoning (bagunça os rótulos).
  - `"gaussian_noise"`: Data Poisoning (borra as imagens com estática).
  - `"targeted_backdoor"`: Data Poisoning (foca secretamente apenas em uma classe discreta).
  - `"trigger_patch"`: Data Poisoning (tatua um quadrado branco fixo no canto da imagem).
  - `"gradient_ascent"`: Model Poisoning (Força o modelo ir na direção errada matematicalmente).
  - `"model_replacement"`: Model Poisoning (Aumenta o peso do atacante em x50 para dominar servidores baseados em médias).
  - `"free_rider"`: Comportamental (Finge que treina, não atrapalha matematicamente, mas degrada a inteligência global no tempo).

- **`poison_rate` (Float/Decimal)**: Fração de dano.
  - Varia de `0.0` (Honestidade pura) até `1.0` (Invasão total). Ex: `0.4` altera 40% doa dados do Batch. (Nota: Model Poisoning em geral demanda `1.0` pra invadir a raiz global).

### Segmento B: Física do Mundo Real
- **`dirichlet_alpha` (Float/Decimal)**: Dita a heterogeneidade/organização dos clientes (Data Skewness).
  - `100.0` (IID Perfeito): Laboratório estéril, todos os clientes têm as exatas mesmas quantidades de fotos de navios, carros, etc.
  - `0.1` (Non-IID Extremo): Simula a bagunça do mundo real, Hospitais ou empresas lidando puramente com tipos únicos de clientes. É aqui que defesas se confundem pra agir.

### Segmento C: O Motor de Inteligência Artificial Cruta
- **`num-server-rounds` (Inteiro)**: Ciclo total da simulação. 
  - `5` é ótimo pra testes; no TCC a valer pode jogar para `20` ou `50` para ver como o dano é persistente e se a rede se recupera.
- **`local-epochs` (Inteiro)**: Profundidade do aprendizado local.
  - Quantas voltas o modelo dá nos dados antes de entregar a resposta do servidor. Um ataque em `local-epochs=5` deixa marcas estruturais mais graves nos tensores e quebra o servidor com maior violência.
- **`batch-size` (Inteiro)**: Pacotes de Memória da Placa de Vídeo por vez (Padrão: `32`).
- **`learning-rate` (Float/Decimal)**: Distância do pulo a favor/contra o gradiente otimizador. (Padrão de FL: `0.1`).
- **`fraction-evaluate` (Float/Decimal)**: Fração de clientes ativados no final só para atestar o placar (Evaluation). `1.0` testa o cenário usando toda a avaliação centralizada.

### O Exemplo Supremo (A Bateria de Teste Extremo)

Se você quiser exercer o limite absoluto do simulador, testando o peso total da sua placa de vídeo e manipulando os 9 eixos dimensionais geométricos da simulação SIMULTANEAMENTE, o comando máximo seria o seguinte colossal array:

```bash
!flwr run . --run-config 'attack_type="targeted_backdoor" poison_rate=0.5 defense_mode="Bulyan" dirichlet_alpha=1.0 num-server-rounds=20 local-epochs=3 batch-size=64 learning-rate=0.01 fraction-evaluate=1.0'
```

**Dissecando esse Megacomando (Por que rodar isso é o ápice da pesquisa):**

1. **`attack_type="targeted_backdoor"` & `poison_rate=0.5`**: Metade da base de dados dos celulares invasores agora têm uma porta dos fundos sutil.
2. **`defense_mode="Bulyan"`**: Em retaliação, o servidor assume a postura extrema bizantina, cortando vetores de clientes impiedosamente em busca do backdoor.
3. **`dirichlet_alpha=1.0`**: A distribuição de classes pelo país é razoavelmente caótica (mundo real). O Bulyan vai transpirar para diferenciar quem está enviando um dado esquisito por ser inocente, e quem está fazendo o backdoor.
4. **`num-server-rounds=20`**: Não acaba rápido. Vamos observar ao longo do tempo (20 rodadas inteiras) se o longo prazo fortalece a Defesa ou consolida a Toxidade.
5. **`local-epochs=3`**: O Invasor agora força a inteligência artificial a ler o veneno 3 vezes antes de enviar. Isso "ancora" o backdoor mais fundo nos tensores.
6. **`batch-size=64` & `learning-rate=0.01`**: Afinamento agressivo do motor da IA. Menos passos violentos de aprendizado (0.01 diminui os solavancos), mas blocos colossais de visão simultânea de memória (64 imagens por ciclo).
7. **`fraction-evaluate=1.0`**: No fim de tudo, exige que o servidor acorde rigorosamente 100% da rede para garantir o placar de avaliação absolutamente letal.

---

## 3. Matrizes de Combinação (Receitas de Testes)

Cenários formatados contendo diversos parâmetros ao mesmo tempo que você pode copiar e colar (linha por linha, sequencialmente) e rodar no Colab. O motor gerará um arquivo `.json` de salvamento diferente pra cada nova linha invocada.

Ao final de um grupo de cruzamento da matriz, rode `python plotar_resultados.py` e o simulador pintará os embates belamente pra você!

### Bateria A: Básico e Controle (O Baseline)
Descubra a linha limite de acurácia com 5 ciclos num ambiente limpo (`FedAvg`), e em seguida insira o ataque.

```bash
# 1. Controle Absoluto (Tudo Limpo)
!flwr run . --run-config 'defense_mode="FedAvg" attack_type="label_flipping" poison_rate=0.0 num-server-rounds=5'

# 2. Vítima Sendo Atacada (O Caos)
!flwr run . --run-config 'defense_mode="FedAvg" attack_type="label_flipping" poison_rate=0.4 num-server-rounds=5'
```

### Bateria B: O Embate das Defesas ("Qual mecanismo protege mais?")
*Objetivo:* Fixar um ataque matemático agressivo (`gradient_ascent` a 100%) em treinamentos longos e ver qual filtro barra o traidor.

```bash
# 1. A Mediana segura o vetor matemático furioso?
!flwr run . --run-config 'defense_mode="FedMedian" attack_type="gradient_ascent" poison_rate=1.0 local-epochs=3'

# 2. O Krum expurga o mentiroso ao longo do tempo?
!flwr run . --run-config 'defense_mode="Krum" attack_type="gradient_ascent" poison_rate=1.0 local-epochs=3'

# 3. O Bulyan se sobressai descartando o invasor e mesclando o melhor?
!flwr run . --run-config 'defense_mode="Bulyan" attack_type="gradient_ascent" poison_rate=1.0 local-epochs=3'
```

### Bateria C: Fraqueza da Defesa Geometral ("Que ataque espadana o Krum?")
*Objetivo:* Usar o fortíssimo `Krum` e quebrar a parede avaliativa de Euclídes mudando o tipo do golpe: saindo do ataque bruto (Model Poisoning) e testando corrupções orgânicas que soam "naturais".

```bash
# Krum vs Pura força bruta de dados (Label Flipping forte)
!flwr run . --run-config 'defense_mode="Krum" attack_type="label_flipping" poison_rate=0.4'

# Krum vs Furtividade Backdoor em Treino Cansativo (Targeted)
!flwr run . --run-config 'defense_mode="Krum" attack_type="targeted_backdoor" poison_rate=0.4 local-epochs=4'
```
*(No Gráfico de Loss local, você verá como o Targeted Backdoor não agita as estatísticas a ponto de disparar as barreiras eudiclianas restritivas do modelo eleito Krum).*

### Bateria D: Teste de Stress IID vs Non-IID (Hospitais desbalanceados)
*Objetivo:* A defesas do tipo *Agregação Topológica* costumam funcionar bem em Laboratórios Padrão. Vamos bagunçar as demografias diminuindo fortemente o `dirichlet_alpha` de 100.0 para 0.1 e ver o servidor enlouquecer com um ataque parasita.

```bash
# Krum ou Bulyan num mundo diversamente idêntico (IID): O sistema expulsa facil a parasitagem 100%
!flwr run . --run-config 'defense_mode="Bulyan" attack_type="model_replacement" poison_rate=1.0 dirichlet_alpha=100.0 num-server-rounds=8'

# A Mesma Defesa num cenário Non-IID brutal The Real-World Scenario
!flwr run . --run-config 'defense_mode="Bulyan" attack_type="model_replacement" poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=8'
```
*(Seu gráfico comprovará que em `alpha=0.1`, todos os clientes parecem incrivelmente díspares [Um treinou navios, o outro tratores]. Com essa "Névoa de Guerra", as defesas estatísticas confundem quem é o traidor que tenta Escalar a montanha `model_replacement`, abrindo buracos nas barricadas).*

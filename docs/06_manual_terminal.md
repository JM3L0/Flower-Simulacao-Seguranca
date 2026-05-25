# Manual Definitivo do Terminal (Run-Config)

Este documento foi criado exclusivamente para ser a sua enciclopédia sobre a entrada de comandos. No ecossistema Flower, o comando de inicialização via terminal é a ferramenta mais poderosa à disposição do pesquisador. Ele injeta comandos dinamicamente em tempo de execução sem que você precise abrir nenhuma linha de código em Python.

Abaixo destrinchamos toda a flexibilidade dessa entrada, do absoluto zero ao limite estressante do hardware.

---

## 1. A Lógica Modular e "O Mínimo Possível"

A arquitetura do painel foi desenhada com um paradigma chamado **Fallback de Segurança**. Se a máquina virtual do Flower não ler ordens diretamente na invocação da execução, ela recuará automaticamente para ler o arquivo raiz chamado `pyproject.toml`.

### O Comando Silencioso (Zero Parâmetros)
O comando absoluto mais curto que você pode rodar é simplesmente:
```bash
!flwr run .
```

* **O que acontece sob o capô:** A máquina "acorda", percebe que não há orientações do usuário na hora do pulo, lê o arquivo `pyproject.toml` e extrai de lá as 9 chaves pré-moldadas (como `num-server-rounds=5` e `defense_mode="FedAvg"`). 
* **O Truque da Eficiência Científica:** Graças a essa herança, você só precisa digitar no `--run-config` o **único parâmetro que quer alterar**. Se o seu `pyproject.toml` define `FedAvg`, mas o foco do seu teste hoje for testar *apenas* a barreira geométrica sem mexer em mais nenhuma métrica, você poupa tempo e digita apenas:
  ```bash
  !flwr run . --run-config 'defense_mode="FedMedian"'
  ```

---

## 2. A Lista Máxima: Os 9 Parâmetros Disponíveis

Sempre que decidir manipular um parâmetro, lembre-se da sintaxe: *Toda a injenção fica entre aspas simples `'...'`, enquanto Textos Internos ficam entre aspas duplas `"..."`. Números ficam soltos.*

### Segmento A: Eixos de Cibersegurança (Escudos e Armas)

**1. `defense_mode`** *(Exige aspas duplas: `"Krum"`)*
Instrui a Central (Servidor) sobre o algoritmo de Agregação que ela deve rodar quando receber as planilhas dos clientes. 
- `"FedAvg"`: Ingênuo. Faz a média simples das contribuições. É a linha de base (Baseline).
- `"FedMedian"`: Intermediário. Recusa os extremos superior e inferior, e aprova ativamente apenas a Mediana.
- `"Bulyan"`: Avançado. Um duplo filtro. Exclui primeiro usando Euclídes, e o que sobrar sofre uma média aparada.
- `"Krum"`: O Executor. Descarta 100% da média global e elege permanentemente o cliente singular mais confiável.

**2. `attack_type`** *(Exige aspas duplas: `"gaussian_noise"`)*
O arsenal do invasor. Diz qual rotina corrompida o cliente vai injetar em suas GPUs locais.
- `"label_flipping"`: Bagunça as classes das fotos, forçando falsa interpretação.
- `"gaussian_noise"`: Sobrepõem estática pesada na imagem forçando falha nos sensores da IA.
- `"targeted_backdoor"`: Altera os rótulos de UMA ÚNICA classe. Difícil de ser rastreado.
- `"trigger_patch"`: A tática da Tatuagem. Acrescenta quadrados brancos na imagem forçando uma quebra sistêmica no reconhecimento por padrão.
- `"gradient_ascent"`: Model Poisoning que inverte o sinal do Loss puro, destruindo a base otimizadora.
- `"model_replacement"`: O cliente treina e escala sua resposta matemática x50 vezes forçando uma dominação por volume bruto.
- `"free_rider"`: O Cliente corta sua CPU local e entrega o trabalho em branco.

**3. `poison_rate`** *(Não leva aspas, Float: `0.5`)*
O Nível de Tensão. Em ataques "Data Poisoning" (ex: Label Flipping), um valor de `0.4` diz que *"No pacote de memória processado agora com 32 fotos, bagunce apenas 12 e libere o restante"*. 
*(Cuidado: Em ataques do tipo "Model Poisoning" como Gradient Ascent, para o fluxo ativar sem bug matemático o recomendável é sempre `1.0`)*.

### Segmento B: Física de Organização

**4. `dirichlet_alpha`** *(Não leva aspas, Float: `0.1`)*
O desbalanceador de realidade (Non-IID). Ele cria a névoa matemática que atormenta os algoritmos Krum e Bulyan.
- Jogar ele em `100.0` gera a Paz laboratorial: Todos os Hospitais participantes têm o exato mesmo diagnóstico na mesma proporção. É fácil expurgar invasores porque eles são os únicos outliers.
- Jogar ele para `0.1` gera o verdadeiro Caos hospitalar orgânico: Cada hospital tem majoritariamente doenças de um único e disperso setor diferente (ex: pediatria x geriátricos). As defesas surtam para agrupá-los.

### Segmento C: As Engrenagens da Inteligência Artificial

Estes parâmetros são estruturais do Machine Learning profundo e requerem cuidado. O menor deslize quebra o treinamento global.

**5. `num-server-rounds`** *(Inteiro: `5`)*
O Ciclo da Federação inteira. Quantas vezes o servidor mandará perguntas, esperará os treinos locais durarem, receber os cálculos e fundir as matrizes.

**6. `local-epochs`** *(Inteiro: `2`)*
O aprofundamento orgânico do hospedeiro local. Se for `3`, o invasor forçará seu sistema a ler o veneno injetado com 3 vezes mais intensidade topológica, enterrando a sujeira mais densamente na raiz dos tensores antes de dar o `upload` no servidor. 

**7. `learning-rate`** *(Float: `0.1`)*
A velocidade em que a matemática desce as ladeiras do erro nas Derivadas e Otimizações de Newton. Saltos ou passos pequenos.

**8. `batch-size`** *(Inteiro: `32`)*
Sacos de Memória. Quantas imagens a Placa de Vídeo consegue ingerir, transformar e aprender de uma única vez. 

**9. `fraction-evaluate`** *(Float: `1.0`)*
Quantos modelos finais na rede global o servidor exige testar para validar as tabelas de Acurácia Final. 

---

## 3. O Teste de Estresse (Megacomando Simultâneo)

Se houver a necessidade tática de forçar e avaliar as 9 dimensões operacionais do framework cruzadas assimetricamente na mesma linha, essa será a configuração de teto do simulador.

```bash
!flwr run . --run-config 'attack_type="targeted_backdoor" poison_rate=0.5 defense_mode="Bulyan" dirichlet_alpha=1.0 num-server-rounds=20 local-epochs=3 batch-size=64 learning-rate=0.01 fraction-evaluate=1.0'
```

Ao lançar essa invocação épica de hardware:
1. Você acorda metade da corporação local injetando uma porta dos fundos furtiva (`poison_rate=0.5`).
2. Manda o Bulyan cortar as cabeças dos piores relatórios com médias aparadas (`Bulyan`).
3. Fornece uma demografia desbalanceada normal gerando névoa suave nos caçadores de extremidades (`alpha=1.0`).
4. Estressa o Servidor ao longo do tempo prolongado (`rounds=20`).
5. Aprofunda as raízes do backdoor localmente antes de serem capturadas de volta pela nuvem (`epochs=3`).
6. Suaviza os solavancos num salto microscópico de aprendizagem num bloco de memória enorme (`batch=64` | `lr=0.01`).
7. Convoca todo o ecossistema ativo simultaneamente para a comprovação final com auditoria de placar absoluto (`fraction-evaluate=1.0`).

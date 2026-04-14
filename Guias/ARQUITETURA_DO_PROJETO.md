# Arquitetura do Laboratório de Segurança Federada

Este documento é o "Mapa do Maroto" do seu software. Ele descreve a função exata de cada arquivo, pasta e engrenagem do simulador para te guiar na hora de alterar lógicas profundas, estudar a base ou até mesmo defender sua tese apresentando a topologia de classes.

---

## 🌳 A Árvore de Diretórios (Visão Geral)

Abaixo está o esqueleto local do seu ambiente. A grande mágica, a Inteligência Artificial e a Matemática vivem inteiramente dentro da pasta `pytorchexample`.

```text
Flower-teste/
│
├── Guias/                               # A enciclopédia do pesquisador
│   ├── ARQUITETURA_DO_PROJETO.md        # <-- Você está lendo este
│   ├── EXPLICACAO_PARAMETROS.md         # O que a matemática do FL significa
│   ├── MANUAL_DO_TERMINAL.md            # Entendendo do --run-config
│   ├── RECEITAS_DE_SIMULACAO.md         # Scripts prontos pra testar IID vs non-IID
│   └── TIPOS_DE_ATAQUE.md               # Detalhes das Corrupções
│
└── quickstart-pytorch/                  # A raiz executável da simulação
    │
    ├── graficos/                        # Onde seus gráficos em PNG são guardados
    ├── metrics_json/                    # O banco de dados bruto de execução (JSON)
    ├── pyproject.toml                   # O cérebro invisível e configurador padrão
    ├── plotar_resultados.py             # Script que lê os JSON e cospe os PNGs
    │
    └── pytorchexample/                  # O MOTOR DA INTELIGÊNCIA ARTIFICIAL
        ├── task.py                      # (A Física) Dataset, Neural Network Pytorch
        ├── attacks.py                   # (As Armas) Lógica dos vírus e corrupções
        ├── client_app.py                # (O Hospedeiro) O que um edge-device processa
        └── server_app.py                # (A Defesa Global) Agregações e Bulyan/Krum
```

---

## ⚙️ Dissecando o Motor (`pytorchexample/`)

Esta pasta contém o coração acadêmico e mecânico do framework Flower atrelado ao modelo PyTorch. É aqui que pesquisadores do mundo inteiro escrevem lógicas de Aprendizado Federado.

### 1. `task.py` (A Fundação Física)
Este arquivo dita **O que** a rede sabe fazer e em **onde** ela treina.
*   **A Classe `Net()`:** Define que a arquitetura da Inteligência é uma CNN (Rede Neural Convolucional) básica feita para classificar imagens pequenas (ideal para o dataset CIFAR-10).
*   **DataLoaders (`load_data`):** Puxa os dados CIFAR-10, embrulha eles em subconjuntos para simular "10 hospitais diferentes" e aplica assimetria (O famoso `dirichlet_alpha`).
*   **O Gancho Agressivo (`train_with_attack`):** Eu alterei a função normal de treino para interceptar matrizes ruins. É ele quem chama as lógicas hostis se o usuário ordenar. É aqui também que o ataque orgânico **Free-Rider** drena a CPU da rede devolvendo o pacote em branco.

### 2. `attacks.py` (O Laboratório de Veneno)
Este arquivo foi inteiramente cunhado por nós. Ele é isolado e funciona como uma gaveta de armas matemáticas puras.
*   Se o usuário forçou um **Data Poisoning** (`label_flipping`, `gaussian_noise`), os scripts roubam o lote de imagens recém carregados e sujam os pixels ou trocam os rótulos antes deles baterem na CNN.
*   Se o usuário forçou um **Model Poisoning** (`gradient_ascent`, `model_replacement`), os scripts esperam a CNN dar o resultado do erro do aprendizado (Model Loss) e multiplicam esse erro para direções absurdas infinitas ou escalam o limite matemático do PyTorch, quebrando a convergência.

### 3. `client_app.py` (O Ator Periférico)
Simula um Dispositivo (Um iPhone, um Servidor de Hospital, ou um Celular Invasor).
*   A classe `FlowerClient` apenas espera sentada uma ordem do Servidor Global.
*   Quando o servidor dá o grito `"Treine 2 épocas e me mande as planilhas!"` (método `fit()`), esse arquivo lê a ordem, captura os blocos de dados (`task.py`), ativa o Veneno (`attacks.py` caso ele seja um impostor na rodada) e por fim embrulha a matriz matemática de retorno (Gradient Upload).

### 4. `server_app.py` (A Entidade Global e os Filtros Bizantinos)
Ele é Deus dentro dessa federação. É o orquestrador que nunca vê imagens, só matrizes cruas.
*   **Estratégias de Agregação:** É ele que instancia os algoritmos passivos ou as barricadas topológicas geométricas (A linha literal de código que puxa o `FedAvg`, `FedMedian`, `Bulyan` ou `Krum`).
*   **A Central de Avaliação:** Quando todos os clientes retornam com suas médias combinadas e limpas pelas defesas bizantinas, o servidor faz um teste Mestre e descobre se a precisão melhorou ou colapsou.
*   **O Cartório (Automação JSON):** Ao final na última rodada (ex: rodada 5 de 5), nós alteramos as raízes desta classe para que ela não só printa o final da operação na tela de terminal, mas despeje e formate essas listas massivas num arquivo unificado .json limpinho dentro do seu repertório, que será usado pelo script local de plotagem.

---

## 📊 A Fachada Executiva (A Pasta Raiz)

Na pasta raiz (`quickstart-pytorch/`), moram os sistemas controladores de infraestrutura.

*   `pyproject.toml`: É o painel de fiação exposto do Flower MLOps. Se você mandar correr a simulação sem falar o que você quer, é lá que ele procura.
*   `plotar_resultados.py`: O automatizador que você invocará ao final de qualquer dia de trabalho. Ele corre todos os arquivos invisíveis `.json`, lê dezenas de colunas, e usando `Matplotlib`, cria dezenas de PNGs sobrepostos (Curvas da Inteligência VS Ataques ou Defesas Bulyan vs Krum) nomeados elegantemente dentro da pasta `graficos/`.

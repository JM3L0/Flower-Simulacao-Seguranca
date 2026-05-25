# Guia Definitivo: Aprendizado Federado com Flower e PyTorch

Este relatório documenta todo o ciclo de instalação, configuração, resolução de erros rotineiros, medidas de cibersegurança e exportação de dados analíticos no **Flower** em máquinas Windows.

---

## 1. Passo a Passo da Instalação e Configuração

### Pré-requisito: A Versão do Python
**Regra de Ouro:** Não utilize o Python mais recente (ex: 3.13). As bibliotecas de inteligência artificial (como as ferramentas extras de simulação) demoram a se atualizar. Tenha sempre o **Python 3.11** ou **3.12** instalado no seu computador e marque `Add Python to PATH` durante a instalação.

### Instalação Básica
No terminal (PowerShell):
```bash
pip install -U flwr
```

### Criando seu Primeiro Projeto
Utilize o assistente de criação:
```bash
flwr new
```
1. Aceite a criação baseada no template PyTorch.
2. Navegue até a pasta (`cd quickstart-pytorch`).
3. Instale os componentes da pasta local:
```bash
pip install .
```

---

## 2. Possíveis Erros e Como Resolver

### Erro 1: "O termo 'flwr' não é reconhecido"
**Solução:** Adicione a pasta `Scripts` do seu Python no `PATH` das variáveis de ambiente do Windows. Pelo PowerShell de administrador, você pode usar:
```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Seu\Caminho\Python\Scripts", "User")
```

### Erro 2: "Exit Code 701: ray backend selected mas ray não está instalado"
**Solução Oficial:** O motor da simulação (Ray) requer compatibilidade fina de Python. Usando o Python <= 3.12, instale o pacote obrigatório de simulação:
```bash
pip install "flwr[simulation]"
```

### Erro 3: "UnicodeDecodeError: charmap codec can't decode... " (ou crash geral)
**Solução:** O Python no Windows detesta pastas contendo acentos, cedilhas ou caracteres especiais (Ex: `Área de Trabalho`).
1. Não utilize `pip install -e .` nesse tipo de pasta. Prefira apenas `pip install .`.
2. Não insira acentuação pura nos comentários de código, isso pode travar os logs no momento do output de tela no terminal (`Command Prompt`).

---

## 3. Principais Comandos do Flower (Dia a Dia)

| Comando | O que faz |
| :--- | :--- |
| `flwr new` | Inicia o assistente para criar um novo projeto. |
| `flwr run .` | Inicia a simulação em background, usando o `pyproject.toml` atual. |
| `flwr run . --stream` | **Recomendado:** Lança a simulação prendendo seu terminal para você assistir aos rounds do treinamento em tempo real. |
| `flwr run . --run-config "num-server-rounds=10"` | Comando para forçar/substituir o número de rodadas sem ter que mexer e salvar o código da IDE. |

---

## 4. O Básico do painel `pyproject.toml`

Vá até o final do arquivo `pyproject.toml` e modifique os cenários no bloco `[tool.flwr.app.config]`:
```toml
num-server-rounds = 5  # O núcleo da estratégia: Quantidade de treinos globais
fraction-evaluate = 0.5  # Seleciona de forma randômica por exemplo 50% dos nós para validar
local-epochs = 1  # Loops do treinamento dentro do celular independente 
learning-rate = 0.05  # Passo matemático no gradiente da IA
batch-size = 32  # Tamanho do tijolo de dados transportado para a placa de vídeo local
```

---

## 5. Simulação Focada em Privacidade e Segurança

No Aprendizado Federado não subimos dados dos usuários para a nuvem. Mas e quando o próprio usuário/celular cliente for um **Agente Malicioso (Hacker)** tentando enviar "lixo" matemático em seu treinamento para destruir a Inteligência Artificial global de propósito (o famoso *Data Poisoning*)?

### O que mudou no código para usarmos o Krum / MultiKrum?
O código padrão da biblioteca usa a métrica **`FedAvg` (Média Ponderada)**. O problema do FedAvg é que ele acredita cegamente em todos os celulares da rede. Se um cliente mandar pesos bizarros, ele puxará toda a média global para baixo.
Para corrigir isso e focar no pilar de Segurança e Defesa, entramos no arquivo `server_app.py` e realizamos uma troca cirúrgica da estratégia para o protocolo MultiKrum.

**Eis o que foi alterado nas importações:**
```python
# ANTES:
from flwr.serverapp.strategy import FedAvg

# DEPOIS:
from flwr.serverapp.strategy import MultiKrum
```

**Eis o que foi alterado no corpo do código:**
```python
# ANTES (Sem segurança):
strategy = FedAvg(fraction_evaluate=fraction_evaluate)

# DEPOIS (Blindado):
strategy = MultiKrum(
    num_malicious_nodes=2, # Dizemos ao servidor que matematicamente ele preveja que até 2 clientes estarão injetando vírus/ruído destrutivo nos dados.
    num_nodes_to_select=8, # Dos 10, ele rejeitará os 2 anômalos por distância euclidiana, extraindo apenas os 8 remanescentes justos.
    fraction_evaluate=fraction_evaluate
)
```

### Outras Estratégias de Segurança Existentes
Existem soluções focadas para diferentes ameaças. A bibliografia de segurança no Flower gira em torno dos seguintes pilares:

#### A. Defesas Bizantinas (Byzantine Robust Aggregation)
Atua quando o inimigo é o *Dispositivo*. O Krum faz parte dessa classe, mas existem opções focadas parecidas:
- **`Bulyan`:** Cria uma verificação em duas camadas, rodando o Krum e depois um corte ainda mais severo que retira outras extremidades. É ainda mais paranoico contra Poisoning.
- **`FedTrimmedAvg` e `FedMedian`:** Troca as médias sofisticadas apenas extirpando as bordas da amostra, ou ficando apenas com a estrita mediana dos gradientes. Previne saltos grotescos instigados por hackers.

#### B. Privacidade Diferencial (Differential Privacy - DP)
Atua quando o inimigo (bisbilhoteiro) é o *Próprio Servidor*. Impede que analistas da IA consigam usar cálculos reversos para deduzir do que se tratavam as imagens originais que treinaram o sistema em um celular específico.
- O Flower suporta isto aplicando **Ruído Gaussiano Artificial** e limites de gradiente (*Clipping*), borrando a pegada da atualização como visto em estratégias dedicadas como `DifferentialPrivacyServerSideFixedClipping`.

#### C. Agregação Segura (Secure Aggregation - SecAgg)
Atua contra bisbilhoteiros de rede *no trajeto da informação*. Eleva a comunicação baseando tudo em pares criptográficos (Diffie-Hellman), garantindo que os clientes encriptem os dados de uma tal maneira que o centralizador possua somente o controle do "soma global" final, sem nunca decifrar ou deter o peso proveniente individualmente de fulano ou ciclano. É a verdadeira barreira contra monitoramentos de infraestrutura tecnológica.

---

## 6. Exportação Automática de Resultados para Análise (CSV)

O Flower expõe a variável em memória que abriga absolutamente todo o histórico dos treinos no objeto capturado após rodar sua simulação (`result = strategy.start()`).

Para transformar seus logs de tela preta numa **Tabela do Excel** detalhada para acompanhamento ou plotagem de gráficos em seus estudos universitários ou relatório acadêmico, insere-se a exportação limpa na base do `server_app.py` (logo após a linha dizendo `torch.save(...)`):

```python
    import pandas as pd
    print("\nExportando tabela de métricas para Excel (CSV)...")
    rodadas, precisoes, perdas = [], [], []
    
    # Extrai o dicionário da Memória de rodadas do Servidor local
    for rodada, metricas in result.evaluate_metrics_serverapp.items():
        rodadas.append(rodada)
        precisoes.append(metricas["accuracy"])
        perdas.append(metricas["loss"])
        
    df = pd.DataFrame({
        "Rodada": rodadas,
        "Precisão Global": precisoes,
        "Perda Global": perdas
    })
    
    # Salva delimitado por ';' para o Excel Brasileiro preencher perfeitamente as colunas
    df.to_csv("tabela_resultados.csv", sep=";", index=False, decimal=",")
    print("Arquivo 'tabela_resultados.csv' preenchido de rodadas métricas criado na raiz do seu projeto!")
```

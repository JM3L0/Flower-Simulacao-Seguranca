# 🌸 Guia Dedicado de Instalação e Configuração do Flower

Este guia fornece o passo a passo completo, detalhado e do zero para preparar o ambiente de desenvolvimento do **Flower (flwr)** com **PyTorch**, aceleração por **GPU (CUDA)** e o motor de simulação **Ray** no Windows e Linux.

---

## 📋 Sumário
1. [Pré-requisitos do Sistema](#1-pré-requisitos-do-sistema)
2. [Criação e Isolamento do Ambiente Virtual](#2-criação-e-isolamento-do-ambiente-virtual)
3. [Instalação do PyTorch com Suporte a GPU (CUDA)](#3-instalação-do-pytorch-com-suporte-a-gpu-cuda)
4. [Instalação do Framework Flower e Motor de Simulação](#4-instalação-do-framework-flower-e-motor-de-simulação)
5. [Instalação das Dependências do Projeto](#5-instalação-das-dependências-do-projeto)
6. [Bateria de Testes de Sanidade (Validação)](#6-bateria-de-testes-de-sanidade-validação)
7. [Solução de Problemas e Erros Frequentes](#7-solução-de-problemas-e-erros-frequentes)

---

## 1. Pré-requisitos do Sistema

Antes de iniciar a instalação, certifique-se de atender aos seguintes requisitos:

* **Sistema Operacional**: Windows 10/11 (64-bit) ou Linux (Ubuntu 20.04+).
* **Versão do Python**: **Python 3.11** ou **Python 3.12** (versões homologadas pelo Flower 1.x e Ray 2.x).
  > [!WARNING]
  > Evite usar Python 3.13 no momento, pois o compilador do Ray e algumas extensões C do PyTorch ainda não possuem wheels pré-compilados estáveis para essa versão.
* **Driver NVIDIA & CUDA**: Driver de vídeo NVIDIA atualizado caso possua GPU dedicada (ex: NVIDIA T400, RTX 30xx/40xx, GTX).
* **Terminal Windows**: PowerShell com privilégio de execução de scripts habilitado.

---

## 2. Criação e Isolamento do Ambiente Virtual

É uma boa prática fundamental **nunca instalar pacotes no Python global** do sistema operacional. Use um ambiente virtual (`venv` ou `conda`).

### Opção A: Usando `venv` nativo do Python (Recomendado)

Abra o terminal PowerShell e execute:

```powershell
# 1. Navegue até a raiz do projeto
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca"

# 2. Crie o ambiente virtual com o nome .venv
python -m venv .venv

# 3. Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1
```

> [!TIP]
> Se o PowerShell exibir o erro `O arquivo Activate.ps1 não pode ser carregado porque a execução de scripts foi desabilitada`, execute uma única vez como Administrador:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Opção B: Usando Conda / Miniconda

```bash
# Criar ambiente com Python 3.11
conda create -n flower_env python=3.11 -y

# Ativar ambiente
conda activate flower_env
```

---

## 3. Instalação do PyTorch com Suporte a GPU (CUDA)

Para que as convoluções do CIFAR-10 executem em segundos na GPU (em vez de horas na CPU), instale o PyTorch compilado com suporte a CUDA:

```powershell
# Atualize primeiro o gerenciador de pacotes pip
python -m pip install --upgrade pip

# Instale PyTorch com suporte a CUDA 12.1 (Padrão estável)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

> [!NOTE]
> Se a sua máquina não possuir GPU dedicada NVIDIA, o comando para instalar a versão CPU é:
> ```powershell
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
> ```

---

## 4. Instalação do Framework Flower e Motor de Simulação

O ecossistema Flower opera com o pacote principal (`flwr`) e o extra de simulação virtual (`flwr[simulation]`), que inclui o orquestrador distribuído **Ray**:

```powershell
# 1. Instalar o core do Flower
pip install -U flwr

# 2. Instalar o motor de simulação (Ray + componentes de nós virtuais)
pip install "flwr[simulation]>=1.26.0"
```

---

## 5. Instalação das Dependências do Projeto

O laboratório necessita do pacote de particionamento e visão computacional (`flwr-datasets`), além de instalar o pacote local em modo editável (`-e`):

```powershell
# 1. Instalar bibliotecas de dados, visão e gráficos
pip install "flwr-datasets[vision]>=0.5.0" matplotlib numpy datasets

# 2. Navegar até a pasta do motor executável e instalar o projeto
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"
pip install -e .
```

---

## 6. Bateria de Testes de Sanidade (Validação)

Para ter certeza absoluta de que tudo foi instalado perfeitamente, execute este teste de 1 minuto no terminal:

### Teste 1: Validação do PyTorch e Detecção de CUDA

```powershell
python -c "import torch; print('✔ PyTorch versão:', torch.__version__); print('✔ CUDA disponível:', torch.cuda.is_available()); print('✔ Dispositivo:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

*Saída esperada*:
```text
✔ PyTorch versão: 2.2.x+cu121 (ou superior)
✔ CUDA disponível: True
✔ Dispositivo: NVIDIA T400 4GB (ou sua GPU)
```

### Teste 2: Validação da CLI do Flower

```powershell
flwr --version
```

*Saída esperada*:
```text
flwr, version 1.x.x
```

### Teste 3: Simulação de Teste Rápido (1 Rodada)

Para validar a orquestração cliente-servidor no Flower:

```powershell
# Certifique-se de estar na pasta quickstart-pytorch
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"

# Forçar UTF-8 para os logs do Windows
$env:PYTHONIOENCODING="utf-8"

# Rodar 1 rodada de teste de sanidade
flwr run . --run-config "num-server-rounds=1 poison_rate=0.0"
```

Se a simulação iniciar e completar a rodada 1 sem erros, seu ambiente está **100% pronto e operacional**!

---

## 7. Solução de Problemas e Erros Frequentes

### 1. `UnicodeDecodeError: 'charmap' codec can't decode byte`
* **Causa**: O console padrão do Windows (PowerShell/CMD) usa codificação legado (CP1252) que falha com caracteres especiais e emojis dos logs do Flower.
* **Solução**: Sempre execute no início da sessão do PowerShell:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### 2. `flwr: comando não encontrado` ou `The term 'flwr' is not recognized`
* **Causa**: O ambiente virtual não está ativo ou a pasta de scripts do Python não foi adicionada ao PATH do sistema operacional.
* **Solução**: Ative o ambiente virtual (`.\.venv\Scripts\Activate.ps1`) ou execute chamando o módulo Python diretamente:
  ```powershell
  python -m flwr.cli.run .
  ```

### 3. Falha de Inicialização do Ray (`Exit Code 701` ou falha de porta/socket)
* **Causa**: Processos residuais do Ray em segundo plano ou bloqueio por firewall do Windows.
* **Solução**: Feche instâncias presas no Windows PowerShell com:
  ```powershell
  Get-Process -Name "*ray*", "*python*" | Stop-Process -Force
  ```
  Ou utilize a opção de limpeza automática incluída no script principal:
  ```powershell
  python laboratorio.py
  ```

### 4. `CUDA out of memory` (Memória de Vídeo Esgotada)
* **Causa**: O tamanho do lote (`batch-size`) ou a quantidade de nós concorrentes no Ray excedeu a VRAM da GPU (ex: 4 GB na T400).
* **Solução**: Reduza o batch size via terminal:
  ```powershell
  flwr run . --run-config "batch-size=32"
  ```

# Roteiro Prático: Experimentos de Elite (Gráficos Diamante)

Este roteiro contém os dois testes definitivos para gerar gráficos de análise de defesas bizantinas no projeto Flower.

> **Importante:** Todos os comandos de simulação (`flwr run ...`) devem ser rodados no terminal do Windows (PowerShell) a partir da pasta raiz executável: `quickstart-pytorch`.

---

## MESTRE 1: A Curva de Colapso das Defesas (Gráfico MTTA-Style)

### Objetivo
Testar o ponto de quebra exato das defesas quando a infiltração de ataque sobe progressivamente de 10% a 90%. Eixo X: Intensidade do Ataque. Eixo Y: Acurácia Global.

### 1. Limpeza da Bancada
```powershell
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue
```

### 2. A Bateria de Varredura (Sweep Loop)
```powershell
$taxas = @(0.1, 0.3, 0.5, 0.7, 0.9)
$defesas = @("FedAvg", "FedMedian", "Bulyan")

foreach ($defesa in $defesas) {
    foreach ($taxa in $taxas) {
        Write-Host "Iniciando Teste => Defesa: $defesa | Intensidade: $taxa" -ForegroundColor Cyan
        $env:PYTHONIOENCODING="utf-8"
        flwr run . --stream --run-config "defense_mode='$defesa' attack_type='gaussian_noise' poison_rate=$taxa num-server-rounds=4"

        # === ANTI-TRAVAMENTO (Obrigatório no Windows) ===
        # --stream garante que o flwr run só retorna DEPOIS da simulação terminar (JSONs salvos).
        # ray stop encerra os workers Ray. NÃO usar Stop-Process python (mata I/O e perde arquivos).
        Write-Host "Simulacao concluida. Limpando processos Ray..." -ForegroundColor Yellow
        ray stop 2>$null
        Start-Sleep -Seconds 8
    }
}
```

### 3. Geração Visual da Curva de Colapso
```powershell
python plotar_curva_risco.py
```
**Arquivo gerado:** `graficos/curva_risco_ataque.png`

---

## MESTRE 2: O Visual de Morte Súbita vs Convergência (Time-Series)

### Objetivo
Avaliar a degradação temporal rodada-a-rodada do modelo. Foca na morte instantânea da rede neural versus a filtragem total da Mediana sob o ataque ditatorial Model Replacement.

### 1. Nova Limpeza da Bancada
```powershell
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue
```

### 2. A Linha de Controle (Baseline Pacífico)
```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=20"
```

### 3. O Ataque Ditatorial sem Defesa (O Caos/A Queda)
```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='model_replacement' poison_rate=1.0 num-server-rounds=20"
```

### 4. A Resistência do Escudo Grosseiro (FedMedian Salva-Vidas)
```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "defense_mode='FedMedian' attack_type='model_replacement' poison_rate=1.0 num-server-rounds=20"
```

### 5. Renderizando as Evoluções Sobrepostas
```powershell
python plotar_resultados.py
```
**Arquivos gerados:** `graficos/comparativo_acuracia.png` e `graficos/comparativo_loss.png`

---

## Explicação Técnica (Linha a Linha)

### O Loop do "MESTRE 1" (Varredura Contínua)
* **`Remove-Item -Path ".\metrics_json\*.json"...`**
O framework Flower funciona como um "Cartório": ele nunca deleta nada, apenas empilha arquivos JSON no fim de toda execução. Se não fizermos a limpa (Clean Slate), o gráfico somará experimentos passados no meio da sua curva.
* **`$taxas = @(...)` e `$defesas = @(...)`**
Registra as Matrizes A e B na memória viva do PowerShell. No jargão da pesquisa, os arrays são a sua Covariância e Tratamentos (Intensidade x Ferramenta de Defesa).
* **`foreach ($defesa in $defesas) { foreach ($taxa in $taxas) {`**
O Loop Aninhado (Nested Loop). Garante que a máquina testará primeiro o `FedAvg` contra as 5 taxas. Só depois que todas acabarem, ele muda a engrenagem para `FedMedian` e roda contra as 5 taxas de novo. Faremos `3 * 5 = 15` simulações totais, totalmente *hands-free* (sem intervenção humana).
* **`$env:PYTHONIOENCODING="utf-8"`**
*Hacking de Windows*. O terminal PowerShell tenta decodificar as saídas ricas em emojis do Flower numa página de código restrita (`charmap`) e causa crash. Essa injeção força a sessão a ler UTF-8 Universal.
* **`flwr run . --run-config "defense_mode='$defesa'... poison_rate=$taxa..."`**
O tiro principal. O comando `flwr run .` sobe o servidor ray local. Ao enviar os argumentos pelo `--run-config`, estamos substituindo (*overriding*) na força a porta padrão do `pyproject.toml`. A cada loop, o PowerShell muda as variáveis `$defesa` e `$taxa` rodando diretamente no backend PyTorch.
* **`num-server-rounds=4`**
Controla o comprimento. Baixado para 4 rodadas para que a bateria toda se resolva em minutos em vez de horas. Na versão final do paper, troque para 15 ou 20.

---

### O Processamento do "MESTRE 2" (Manuais Cirúrgicos)
* **`--stream`**
No teste 1, queríamos ignorar lixo de texto e apenas fabricar as métricas silenciosamente. No teste 2 temporal, adicionei a flag `--stream` aos comandos `flwr run`, o que força a engine a represar os metadados no console em tempo real. Você VERÁ o dano do Model Replacement corroendo as rodadas subitamente.
* **`poison_rate=1.0`**
Diferente da taxa gradual do Mestre 1, rodamos de cara 1.0 (100% de ataque). O `model_replacement` (Escala Astronômica de pesos) só tem comprovação científica de dano se a matriz atua maciçamente.
* **`python plotar_resultados.py` (ou `python plotar_curva_risco.py`)**
O Python não entra na execução do motor de IA (gerido via bash). Os traçadores entram como visualizadores post-mortem: carregam os múltiplos subconjuntos de JSON usando regex pelo pacote `glob` e interpolam na base Matplotlib construindo as grades geométricas coloridas.

---

## Bônus: Rodando no Google Colab (Alta Performance)

O Windows PowerShell e o Linux do Google Colab possuem diferenças sintáticas cruciais (como a ausência de `$env:` e o uso de aspas). Se você enviou este projeto para o Colab para usar GPUs gratuitas, siga o roteiro adaptado abaixo.

**Pré-requisito:** Certifique-se de navegar para a pasta correta (`%cd /content/quickstart-pytorch/`).

### Mestre 1 adaptado para Colab (Célula Python)
Crie uma célula de código Python e cole:
```python
import os
import time

taxas = [0.1, 0.3, 0.5, 0.7, 0.9]
defesas = ["FedAvg", "FedMedian", "Bulyan"]

print("Limpando bancada...")
os.system("rm -f metrics_json/*.json")

for defesa in defesas:
    for taxa in taxas:
        print(f"\n==== Iniciando Teste => Defesa: {defesa} | Intensidade: {taxa} ====")
        
        # --stream é OBRIGATÓRIO: garante que o flwr run bloqueia até o fim (JSONs salvos).
        comando = f"flwr run . --stream --run-config 'defense_mode=\"{defesa}\" attack_type=\"gaussian_noise\" poison_rate={taxa} num-server-rounds=4'"
        os.system(comando)

        # === ANTI-TRAVAMENTO: Limpeza de processos Ray ===
        # NÃO usar pkill (pode matar processos durante I/O e perder JSONs).
        print("Simulação concluída. Limpando processos Ray...")
        os.system("ray stop 2>/dev/null")
        time.sleep(8)

print("\n==== Bateria completa! Renderizando gráfico... ====")
os.system("python plotar_curva_risco.py")
```

### Mestre 2 adaptado para Colab (Células Bash Independentes)
Num Notebook, os comandos isolados devem começar com `!`. Após cada simulação, rode a célula de limpeza.

**Célula 1 — Limpeza da Bancada:**
```bash
!rm -f metrics_json/*.json
```
**Célula 2 — Baseline Pacífico:**
```bash
!flwr run . --stream --run-config 'defense_mode="FedAvg" poison_rate=0.0 num-server-rounds=20'
```
**Célula 3 — Limpeza entre simulações:**
```bash
!ray stop 2>/dev/null; sleep 8; echo "Limpo."
```
**Célula 4 — Ataque Ditatorial sem Defesa:**
```bash
!flwr run . --stream --run-config 'defense_mode="FedAvg" attack_type="model_replacement" poison_rate=1.0 num-server-rounds=20'
```
**Célula 5 — Limpeza entre simulações:**
```bash
!ray stop 2>/dev/null; pkill -f 'flwr' 2>/dev/null; pkill -f 'ray' 2>/dev/null; sleep 5; echo "Limpo."
```
**Célula 6 — Resistência FedMedian:**
```bash
!flwr run . --stream --run-config 'defense_mode="FedMedian" attack_type="model_replacement" poison_rate=1.0 num-server-rounds=20'
```
**Célula 7 — Limpeza final + Renderização:**
```bash
!ray stop 2>/dev/null; sleep 5
!python plotar_resultados.py
```

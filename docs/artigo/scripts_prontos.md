# 🔧 Scripts Prontos para Executar — Copie e Cole no Terminal

## ⚠️ PREREQUISITOS
```powershell
# 1. Navegue para a pasta certa
cd "C:\Users\jsous\OneDrive\Área de Trabalho\Flower-teste\quickstart-pytorch"

# 2. Verifique Python e Flower
python --version
flwr --version

# 3. Se não estiver instalado:
pip install -U "flwr[simulation]"
pip install .
```

---

## 🚀 SCRIPT 1: TESTE RÁPIDO (5 minutos)

### Sem Ataque (Baseline Limpo)
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=5"
```

### Com Ataque (FedAvg vs. Gradient Ascent)
```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"
```

### Com Defesa (Bulyan vs. Gradient Ascent)
```powershell
$env:PYTHONIOENCODING="utf-8"
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"
```

**Output Esperado:**
- Arquivo JSON criado em `metrics_json/`
- Nomes como: `metrics_Bulyan_gradient_ascent_pr1.0_da1.0_TIMESTAMP.json`

---

## 📊 SCRIPT 2: CENÁRIO 1 — CURVA DE COLAPSO (30 minutos)

**Objetivo**: Mostrar como acurácia degrada com aumento de poison_rate

```powershell
# Limpeza
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# Defina arrays
$defesas = @("FedAvg", "FedMedian", "Krum", "Bulyan")
$taxas = @(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

# Loop duplo
foreach ($defesa in $defesas) {
    foreach ($taxa in $taxas) {
        Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "Defesa: $defesa | Intensity: $taxa" -ForegroundColor Yellow
        Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
        
        flwr run . --stream --run-config "defense_mode='$defesa' attack_type='label_flipping' poison_rate=$taxa num-server-rounds=10"
        
        Write-Host "Limpando Ray..." -ForegroundColor Green
        ray stop 2>$null
        Start-Sleep -Seconds 5
    }
}

# Gere gráficos
Write-Host "Gerando gráficos..." -ForegroundColor Cyan
python plotar_resultados.py

Write-Host "✅ Cenário 1 Completo!" -ForegroundColor Green
Write-Host "Gráficos em: .\graficos\comparativo_acuracia.png" -ForegroundColor Blue
```

**Tempo Total**: ~30 minutos (4 defesas × 6 taxas = 24 simulações)

---

## ⏱️ SCRIPT 3: CENÁRIO 2 — MORTE SÚBITA (20 minutos)

**Objetivo**: Mostrar degradação temporal de gradient_ascent

```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# Baseline: Sem ataque
Write-Host "BASELINE: FedAvg sem ataque" -ForegroundColor Cyan
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=20"
ray stop 2>$null
Start-Sleep -Seconds 5

# Ataque bruto: FedAvg com gradient_ascent
Write-Host "ATAQUE: FedAvg com gradient_ascent (MORTE SÚBITA)" -ForegroundColor Red
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=20"
ray stop 2>$null
Start-Sleep -Seconds 5

# Defesa: Bulyan com gradient_ascent
Write-Host "DEFESA: Bulyan com gradient_ascent (RESISTÊNCIA)" -ForegroundColor Green
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=20"
ray stop 2>$null
Start-Sleep -Seconds 5

# Visualize
python plotar_resultados.py

Write-Host "✅ Cenário 2 Completo!" -ForegroundColor Green
```

**Tempo Total**: ~20 minutos (3 simulações × 20 rodadas)

---

## 🌍 SCRIPT 4: CENÁRIO 3 — NÉVOA DE GUERRA (40 minutos)

**Objetivo**: Mostrar que defesas falham em Non-IID extremo

```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

$alphas = @(100, 10, 1, 0.5, 0.1)
$defesas = @("Krum", "Bulyan")

# Ataque: model_replacement (bem demonstrável em heterogeneidade)
foreach ($alpha in $alphas) {
    foreach ($defesa in $defesas) {
        Write-Host "Dirichlet Alpha: $alpha | Defesa: $defesa" -ForegroundColor Cyan
        
        flwr run . --stream --run-config "defense_mode='$defesa' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=$alpha num-server-rounds=15"
        
        ray stop 2>$null
        Start-Sleep -Seconds 5
    }
}

python plotar_resultados.py

Write-Host "✅ Cenário 3 Completo!" -ForegroundColor Green
Write-Host "Observe: Acurácia cai conforme alpha diminui (menos IID)" -ForegroundColor Blue
```

**Tempo Total**: ~40 minutos (5 alphas × 2 defesas = 10 simulações)

---

## 🎯 SCRIPT 5: CENÁRIO 4 — BACKDOOR FURTIVO (25 minutos)

**Objetivo**: Mostrar que acurácia global não detecta ataques por-classe

```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

$taxas = @(0.2, 0.4, 0.6, 0.8, 1.0)

# Sem defesa
Write-Host "Testando: FedAvg + Targeted Backdoor" -ForegroundColor Cyan
foreach ($taxa in $taxas) {
    flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='targeted_backdoor' poison_rate=$taxa num-server-rounds=15"
    ray stop 2>$null
    Start-Sleep -Seconds 5
}

# Com defesa
Write-Host "Testando: Bulyan + Targeted Backdoor" -ForegroundColor Cyan
foreach ($taxa in $taxas) {
    flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=$taxa num-server-rounds=15"
    ray stop 2>$null
    Start-Sleep -Seconds 5
}

python plotar_resultados.py

Write-Host "✅ Cenário 4 Completo!" -ForegroundColor Green
Write-Host "Insight: Acurácia global permanece alta, mas classe alvo → 0%" -ForegroundColor Blue
```

**Tempo Total**: ~25 minutos

---

## 🔬 SCRIPT 6: TESTES COMPLETOS (6-8 horas)

**ADVERTÊNCIA**: Este é o teste completo recomendado para o artigo

```powershell
$env:PYTHONIOENCODING="utf-8"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         BATERIA COMPLETA DE TESTES PARA ARTIGO            ║" -ForegroundColor Cyan
Write-Host "║     Estimado: 6-8 horas. Deixe rodando overnight!          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# Fase 1: Baselines
Write-Host "FASE 1: BASELINE E CONTROLE" -ForegroundColor Yellow

$baseline_configs = @(
    "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=15",
    "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=0.5 num-server-rounds=15",
    "defense_mode='Bulyan' attack_type='label_flipping' poison_rate=0.5 num-server-rounds=15"
)

foreach ($config in $baseline_configs) {
    Write-Host "Teste: $config" -ForegroundColor Green
    flwr run . --stream --run-config "$config"
    ray stop 2>$null
    Start-Sleep -Seconds 5
}

# Fase 2: Comparação de Defesas
Write-Host "FASE 2: COMPARAÇÃO DE DEFESAS" -ForegroundColor Yellow

$ataques = @("label_flipping", "gradient_ascent", "model_replacement")
$defesas = @("FedAvg", "FedMedian", "Krum", "Bulyan")

foreach ($ataque in $ataques) {
    foreach ($defesa in $defesas) {
        $taxa = if ($ataque -eq "label_flipping") { 0.5 } else { 1.0 }
        $config = "defense_mode='$defesa' attack_type='$ataque' poison_rate=$taxa num-server-rounds=12"
        
        Write-Host "Teste: $defesa vs $ataque" -ForegroundColor Green
        flwr run . --stream --run-config "$config"
        ray stop 2>$null
        Start-Sleep -Seconds 5
    }
}

# Fase 3: Degradação Progressiva
Write-Host "FASE 3: DEGRADAÇÃO PROGRESSIVA" -ForegroundColor Yellow

$taxas = @(0.1, 0.2, 0.4, 0.7, 1.0)
$defesas_selecionadas = @("FedAvg", "FedMedian", "Bulyan")

foreach ($defesa in $defesas_selecionadas) {
    foreach ($taxa in $taxas) {
        $config = "defense_mode='$defesa' attack_type='label_flipping' poison_rate=$taxa num-server-rounds=12"
        
        Write-Host "Teste: $defesa com poison_rate=$taxa" -ForegroundColor Green
        flwr run . --stream --run-config "$config"
        ray stop 2>$null
        Start-Sleep -Seconds 5
    }
}

# Fase 4: Impacto de Heterogeneidade
Write-Host "FASE 4: IMPACTO DE HETEROGENEIDADE" -ForegroundColor Yellow

$alphas = @(100, 10, 1, 0.5, 0.1)
$defesas_hetero = @("Krum", "Bulyan")

foreach ($defesa in $defesas_hetero) {
    foreach ($alpha in $alphas) {
        $config = "defense_mode='$defesa' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=$alpha num-server-rounds=12"
        
        Write-Host "Teste: $defesa com alpha=$alpha" -ForegroundColor Green
        flwr run . --stream --run-config "$config"
        ray stop 2>$null
        Start-Sleep -Seconds 5
    }
}

# Finalização
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             TESTES COMPLETOS TERMINADOS!                  ║" -ForegroundColor Green
Write-Host "║         Gerando gráficos finais...                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

python plotar_resultados.py

Write-Host "✅ SUCESSO! Gráficos em: .\graficos\" -ForegroundColor Green
Write-Host "📊 JSONs em: .\metrics_json\" -ForegroundColor Green
```

---

## 📈 SCRIPT 7: ANÁLISE ESTATÍSTICA (Python)

Após os testes, execute este script para gerar análise:

```python
# Salve como: analise_estatistica.py

import json
import numpy as np
import os
from pathlib import Path

def analisar_metricas():
    """Analisa todos os JSONs gerados"""
    
    results = []
    metrics_dir = Path("./metrics_json")
    
    for json_file in metrics_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extrai informações
            config = data['experiment_config']
            final_acc = data['final_accuracy']
            final_loss = data['final_loss']
            
            results.append({
                'strategy': config['strategy'],
                'attack': config['attack_type'],
                'poison_rate': config['poison_rate'],
                'alpha': config['dirichlet_alpha'],
                'final_accuracy': final_acc,
                'final_loss': final_loss,
                'filename': json_file.name
            })
        except Exception as e:
            print(f"Erro ao ler {json_file}: {e}")
    
    # Estatísticas por Defesa
    print("="*70)
    print("ESTATÍSTICAS POR DEFESA")
    print("="*70)
    
    defesas = set(r['strategy'] for r in results)
    for defesa in sorted(defesas):
        subset = [r for r in results if r['strategy'] == defesa]
        accuracies = [r['final_accuracy'] for r in subset]
        
        if accuracies:
            print(f"\n{defesa}:")
            print(f"  Acurácia Média: {np.mean(accuracies):.2%}")
            print(f"  Desvio Padrão: {np.std(accuracies):.2%}")
            print(f"  Min-Max: {np.min(accuracies):.2%} - {np.max(accuracies):.2%}")
    
    # Estatísticas por Ataque
    print("\n" + "="*70)
    print("ESTATÍSTICAS POR ATAQUE")
    print("="*70)
    
    ataques = set(r['attack'] for r in results)
    for ataque in sorted(ataques):
        subset = [r for r in results if r['attack'] == ataque]
        accuracies = [r['final_accuracy'] for r in subset]
        
        if accuracies:
            print(f"\n{ataque}:")
            print(f"  Acurácia Média: {np.mean(accuracies):.2%}")
            print(f"  Desvio Padrão: {np.std(accuracies):.2%}")
            print(f"  Min-Max: {np.min(accuracies):.2%} - {np.max(accuracies):.2%}")
    
    # Resiliência (Defesa × Ataque)
    print("\n" + "="*70)
    print("MATRIZ DE RESILIÊNCIA (Acurácia Média)")
    print("="*70)
    
    # Estrutura: defesa × ataque
    matrix_data = {}
    for r in results:
        key = (r['strategy'], r['attack'])
        if key not in matrix_data:
            matrix_data[key] = []
        matrix_data[key].append(r['final_accuracy'])
    
    defesas_sorted = sorted(set(r['strategy'] for r in results))
    ataques_sorted = sorted(set(r['attack'] for r in results))
    
    print(f"\n{'Defesa':<15} | {' | '.join(a[:12].ljust(12) for a in ataques_sorted)}")
    print("-" * (15 + len(ataques_sorted) * 16))
    
    for defesa in defesas_sorted:
        row = f"{defesa[:14]:<15}"
        for ataque in ataques_sorted:
            key = (defesa, ataque)
            if key in matrix_data:
                acc = np.mean(matrix_data[key])
                row += f" | {acc:6.1%}"
            else:
                row += " | {'N/A':>6}"
        print(row)
    
    return results

if __name__ == "__main__":
    results = analisar_metricas()
    print(f"\n✅ Análise completa! {len(results)} testes processados.")
```

**Para executar:**
```powershell
python analise_estatistica.py
```

---

## 📋 CHECKLIST DE EXECUÇÃO

```powershell
# ✅ Marque conforme completa

# PRÉ-REQUISITOS
[ ] Python 3.11 ou 3.12 instalado
[ ] flwr[simulation] instalado
[ ] Pasta quickstart-pytorch em PATH correto
[ ] Espaço em disco disponível (~2GB para testes)

# TESTES RÁPIDOS (5-30 minutos)
[ ] Script 1: Teste Rápido executado
[ ] Verificar se JSON criado em metrics_json/
[ ] Gráficos gerados com sucesso

# TESTES POR CENÁRIO (30-40 minutos cada)
[ ] Script 2: Curva de Colapso
[ ] Script 3: Morte Súbita
[ ] Script 4: Névoa de Guerra
[ ] Script 5: Backdoor Furtivo

# TESTES COMPLETOS (6-8 horas)
[ ] Script 6: Bateria Completa (deixe overnight)
[ ] Verificar se todos os JSONs foram criados
[ ] Contar total de arquivos: deve ser ~100+

# ANÁLISE
[ ] Script 7: Análise Estatística
[ ] Revisar estatísticas por defesa
[ ] Revisar matriz de resiliência

# DOCUMENTAÇÃO
[ ] Screenshots dos gráficos salvos
[ ] Copie tabelas de resiliência para arquivo
[ ] Documente achados surpreendentes
```

---

## 🆘 TROUBLESHOOTING

### Erro: "O termo 'flwr' não é reconhecido"
```powershell
# Solução: Adicione Python ao PATH
$env:Path += ";C:\Users\jsous\AppData\Local\Programs\Python\Python311\Scripts"
flwr --version
```

### Erro: "charmap codec can't decode"
```powershell
# Solução: Use encoding UTF-8
$env:PYTHONIOENCODING="utf-8"
# (já está em todos os scripts acima)
```

### Erro: "ray stop não funciona"
```powershell
# Solução: Limpar processos Ray
Get-Process | Where-Object {$_.ProcessName -like "*ray*"} | Stop-Process -Force
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```

### Teste muito lento (>30 segundos por rodada)
```powershell
# Solução: Reduzir complexidade
# Mude "num-server-rounds=15" para "num-server-rounds=3" nos testes
# Ou aumente número de CPUs:
flwr run . --federation-config "options.backend.client-resources.num-cpus=4"
```

---

## 🎯 PRÓXIMO PASSO

**Copie o Script que deseja:**

1. **Teste Rápido?** → Copie Script 1 (5 min)
2. **Primeiro Cenário?** → Copie Script 2 (30 min)
3. **Tudo Junto?** → Copie Script 6 (6-8 horas)

Cole no PowerShell em `quickstart-pytorch/` e execute!

---

**Boa sorte com os testes! 🚀**

# 📜 Módulo 3: Scripts de Execução e Diagramas Visuais

Este documento reúne os scripts PowerShell prontos para execução sequencial das baterias de testes e os diagramas em ASCII que ilustram visualmente os fluxos de dados, interações de ataque/defesa e a topologia do simulador.

---

## 💻 1. Scripts PowerShell Prontos para Executar

Navegue até a pasta executável antes de iniciar:
```powershell
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"
```

### 🚀 Script 1: Teste Rápido de Validação (5 Minutos)
```powershell
# 1. UTF-8 e Limpeza
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# 2. Execução sem ataque (Baseline)
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=5"

# 3. Execução com ataque Gradient Ascent sem defesa
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# 4. Execução com defesa Bulyan vs Gradient Ascent
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# 5. Plotagem dos gráficos
python plotar_resultados.py
```

---

### 📊 Script 2: Cenário 1 — Curva de Colapso (Sensibilidade ao Poison Rate)
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

foreach ($pr in 0.0, 0.1, 0.2, 0.3, 0.5) {
    flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=$pr num-server-rounds=5"
}

python plotar_resultados.py
```

---

### ⚔️ Script 3: Cenário 2 — Morte Súbita (Comparativo de Defesas)
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# FedAvg vs Gradient Ascent
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# FedMedian vs Gradient Ascent
flwr run . --stream --run-config "defense_mode='FedMedian' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# Krum vs Gradient Ascent
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# Bulyan vs Gradient Ascent
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

python plotar_resultados.py
```

---

### 🌫️ Script 4: Cenário 3 — Névoa de Guerra (IID vs Non-IID Extremo)
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# Krum em IID (alpha = 100.0)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=100.0 num-server-rounds=5"

# Krum em Non-IID Extremo (alpha = 0.1)
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=5"

python plotar_resultados.py
```

---

## 🎨 2. Diagramas Visuais em ASCII

### Diagrama 1: O Fluxo Circular do Aprendizado Federado
```text
           [ Servidor Central (server_app.py) ]
                     │             ▲
    1. Envia Modelo  │             │  3. Envia Gradientes
       Global        ▼             │     (Com ou Sem Ataque)
             ┌──────────────┬──────────────┐
             ▼              ▼              ▼
        [Cliente 1]    [Cliente 2]   [Cliente Invasor]
        (Honesto)      (Honesto)     (Attacks.py)
             │              │              │
             └──────────────┴──────────────┘
               2. Treino Local (CIFAR-10)
```

### Diagrama 2: Estrutura da Agregação Bulyan (Dupla Camada)
```text
Gradientes Recebidos (n) ──► [ Filtro Krum ] ──► Seleciona Melhores (n - 2f)
                                                       │
                                                       ▼
                                            [ Trimmed Mean (Média Aparada) ]
                                                       │
                                                       ▼
                                             Modelo Global Atualizado
```

### Diagrama 3: Modelo SPN do Protocolo Defensivo
```text
  (P0: Estado Limpo) ──[ T1: Injeção de Veneno ]──► (P1: Cliente Infectado)
          │                                                  │
   [ T0: Aggregation ]                                [ T2: Detecção Bizantina ]
          │                                                  │
          ▼                                                  ▼
  (P2: Modelo Saudável) ◄─────────────────────────── (P3: Outlier Descartado)
```

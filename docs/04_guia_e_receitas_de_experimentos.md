# 📊 Capítulo 4: Guia de Experimentos, Métricas JSON e Receitas de Simulação

Este documento orienta o fluxo completo de condução de testes empíricos, a estrutura dos relatórios de métricas salvos em JSON, a utilização do script automático de plotagem de gráficos e receitas com comandos prontos.

---

## 🔄 1. O Fluxo de Execução da Simulação

```text
Terminal (--run-config)
    │
    ▼
pyproject.toml (Valores Padrão / Fallback)
    │
    ├──► server_app.py → Seleciona Defesa → Executa Rodadas → Salva JSON em metrics_json/
    │
    └──► client_app.py → Lê poison_rate e dirichlet_alpha
              │
              ▼
         task.py → Particiona Dados (Dirichlet) → Executa Treino com/sem Ataque
```

---

## 📄 2. Estrutura dos Arquivos de Saída (JSON)

Ao final de cada execução, o arquivo [`server_app.py`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/quickstart-pytorch/pytorchexample/server_app.py) gera automaticamente um relatório formatado dentro da pasta `metrics_json/`.

**Padrão de Nome do Arquivo**:
```text
metrics_{estrategia}_{attack_type}_pr{poison_rate}_da{dirichlet_alpha}_{timestamp}.json
```
*Exemplo*: `metrics_Bulyan_gradient_ascent_pr1.0_da1.0_20260501_143000.json`

### Exemplo de Conteúdo Interno:
```json
{
  "experiment_config": {
    "strategy": "Bulyan",
    "attack_type": "gradient_ascent",
    "num_server_rounds": 5,
    "poison_rate": 1.0,
    "dirichlet_alpha": 1.0,
    "learning_rate": 0.1,
    "fraction_evaluate": 0.5,
    "timestamp": "2026-05-01T14:30:00"
  },
  "rounds": [
    { "round": 0, "accuracy": 0.1001, "loss": 2.305 },
    { "round": 1, "accuracy": 0.2540, "loss": 2.120 },
    { "round": 2, "accuracy": 0.4210, "loss": 1.850 },
    { "round": 3, "accuracy": 0.5890, "loss": 1.410 },
    { "round": 4, "accuracy": 0.6750, "loss": 1.150 }
  ],
  "final_accuracy": 0.6750,
  "final_loss": 1.150,
  "total_rounds_completed": 5
}
```

---

## 📈 3. Geração Automática de Gráficos

Após executar um lote de experimentos, invoque o script de plotagem na raiz de `quickstart-pytorch/`:

```powershell
python plotar_resultados.py
```

* **Funcionamento**: O script lê todos os arquivos `.json` existentes dentro da pasta `metrics_json/`, extrai as curvas de Acurácia e Perda (*Loss*) de cada rodada, plota curvas comparativas sobrepostas usando `Matplotlib` e salva a imagem final em `graficos/comparativo_cenarios.png`.

---

## 🧪 4. Receitas de Testes (Baterias de Experimentos)

### Bateria A: Teste de Controle e Baseline (Mede o dano do ataque sem defesa)
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# 1. Baseline Limpo (Sem Ataque)
flwr run . --stream --run-config "defense_mode='FedAvg' poison_rate=0.0 num-server-rounds=5"

# 2. Vítima sob Ataque de Inversão de Rótulos (Sem Defesa)
flwr run . --stream --run-config "defense_mode='FedAvg' attack_type='label_flipping' poison_rate=0.4 num-server-rounds=5"

python plotar_resultados.py
```

---

### Bateria B: O Embate das Defesas ("Qual mecanismo barra o Gradient Ascent?")
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# 1. Mediana
flwr run . --stream --run-config "defense_mode='FedMedian' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# 2. Krum
flwr run . --stream --run-config "defense_mode='Krum' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# 3. Bulyan
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

python plotar_resultados.py
```

---

### Bateria C: Teste de Stress IID vs. Non-IID ("A Névoa de Guerra quebra a defesa?")
```powershell
$env:PYTHONIOENCODING="utf-8"
Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue

# 1. Bulyan em mundo IID esterilizado (alpha = 100.0)
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=100.0 num-server-rounds=8"

# 2. Bulyan em mundo Non-IID extremo (alpha = 0.1)
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='model_replacement' poison_rate=1.0 dirichlet_alpha=0.1 num-server-rounds=8"

python plotar_resultados.py
```

---

## 💡 Dicas Importantes para Experimentos

1. **Limpe a pasta `metrics_json/`** antes de iniciar uma nova bateria de testes para evitar que gráficos antigos se misturem aos novos:
   ```powershell
   Remove-Item -Path ".\metrics_json\*.json" -ErrorAction SilentlyContinue
   ```
2. **Reprodutibilidade**: O particionador `DirichletPartitioner` utiliza uma semente fixa (`seed=42`), garantindo que o mesmo valor de `dirichlet_alpha` gere exatamente a mesma distribuição de dados entre as execuções.

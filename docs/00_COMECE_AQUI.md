# 🚀 COMECE AQUI — Portal Central do Laboratório

Bem-vindo ao **Laboratório de Segurança em Aprendizado Federado (Flower + PyTorch)**. Toda a documentação e planejamento científico do projeto estão organizados em **3 módulos essenciais**:

---

## 🗺️ Mapa Central de Navegação

```text
docs/
│
├── 00_COMECE_AQUI.md                          # 🧭 Você está aqui (Portal Central e Quickstart)
│
├── 1_laboratorio/                             # 📘 GUIA TÉCNICO E OPERACIONAL
│   ├── 01_guia_operacional_e_terminal.md      # Instalação, arquitetura de código, --run-config e plotagem
│   ├── 02_catalogo_ataques_e_defesas.md       # Catálogo dos 7 ataques, 4 defesas convencionais, DP e SecAgg
│   └── 03_guia_execucao_google_colab.md       # ☁️ Guia passo a passo de execução em GPU T4 no Colab
│

├── 2_pesquisa_ativa/                          # 🔬 PESQUISA EM FOCO: ARTIGO 1 & ARTIGO 2
│   ├── 01_artigo1_backdoors_e_auditoria.md    # Artigo 1: Estudo Empírico do Impacto de Ataques Furtivos sob Defesas Convencionais
│   ├── 02_pesquisa_bibliografica_e_prompts.md # Prompt mestre para IA, buscas booleanas e fichamento
│   └── 03_artigo2_benchmark_fatorial.md       # Artigo 2: Benchmark Fatorial Amplo 7x4x3 e Pipeline de Publicação
│
└── 3_portfolio_e_teoria/                      # 💡 PORTFÓLIO DE IDEIAS & TEORIA SPN
    ├── 01_portfolio_10_ideias_pesquisa.md     # As 10 ideias de artigos avaliadas (Empíricas + SPN)
    └── 02_modelagem_formal_spn_e_markov.md    # Teoria SPN, fórmulas de MTTF, ANOVA e Casos de Uso
```

---

## 🎯 Foco Principal: Artigo 1 (Estudo Empírico sob Defesas Convencionais)

* **Tema Central**: Avaliação empírica de como **ataques furtivos (*stealth backdoors*)** degradam modelos de Aprendizado Federado protegidos pelas **defesas convencionais de mercado** (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`).
* **Pergunta Chave**: As defesas convencionais usadas pela indústria conseguem conter ataques direcionados a classes específicas sob assimetria de dados real (*Non-IID*), ou a métrica de Acurácia Global mascara um colapso invisível?
* **Instrumento Metodológico**: Avaliação detalhada via **Matriz de Confusão 10x10 e Recall por Classe** para mensurar o ponto cego da acurácia global e a perda de resiliência.

---

## ⚡ Teste Rápido de 5 Minutos (Quickstart)

Para rodar uma simulação no Flower agora mesmo:

```powershell
# 1. Navegue até a pasta executável do Flower
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"

# 2. Configure a codificação UTF-8 no terminal PowerShell
$env:PYTHONIOENCODING="utf-8"

# 3. Execute a simulação (Defesa Bulyan sob Targeted Backdoor em Non-IID)
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='targeted_backdoor' poison_rate=0.4 dirichlet_alpha=0.1 num-server-rounds=5"

# 4. Gere os gráficos de análise
python plotar_resultados.py
```

---

## 🚨 5 Armadilhas Comuns a Evitar

1. **Não tente entender toda a teoria antes de rodar os primeiros testes**: Comece com o comando de teste rápido de 5 minutos.
2. **Esquecer de configurar UTF-8 no PowerShell**: Execute sempre `$env:PYTHONIOENCODING="utf-8"` para evitar erros de acentuação nos logs do console Windows.
3. **Rodar testes sem limpar arquivos antigos**: Execute `Remove-Item .\metrics_json\*.json` antes de iniciar uma nova bateria comparativa para não misturar curvas.
4. **Confundir ordem de configuração**: Parâmetros passados no terminal via `--run-config` sobrescrevem automaticamente os padrões do `pyproject.toml`.
5. **Ignorar a assimetria dos dados**: Lembre-se de que `dirichlet_alpha=0.1` simula a "Névoa de Guerra" Non-IID do mundo real, onde defesas geométricas tendem a falhar.

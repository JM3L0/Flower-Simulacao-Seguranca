# 🚀 COMECE AQUI — Guia Central do Pesquisador

Bem-vindo ao **Laboratório de Segurança em Aprendizado Federado**. Toda a documentação do projeto está organizada de forma modular em três áreas: **Documentação Técnica**, **Publicação Científica** e o novo **Portfólio de Ideias de Pesquisa**.

---

## 🗺️ Mapa de Navegação da Documentação

### 💡 Parte 0: Portfólio de Ideias de Pesquisa (`docs/ideias/`)

* **[00_indice_ideias.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/ideias/00_indice_ideias.md)**: Visão geral e comparação entre os dois caminhos de publicação científica.
* **[01_ideias_pesquisa_empirica_sem_spn.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/ideias/01_ideias_pesquisa_empirica_sem_spn.md)**: 5 propostas detalhadas de artigos empíricos/sistêmicos (Névoa Non-IID, Backdoors Furtivos, Carga Computacional Local, Free-Riders e Benchmark Fatorial).
* **[02_ideias_modelagem_estocastica_com_spn.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/ideias/02_ideias_modelagem_estocastica_com_spn.md)**: 5 propostas detalhadas de artigos formais com **Redes de Petri Estocásticas (SPN)** (Cálculo MTTF, Performabilidade GSPN, Absorção de Backdoors, Sobrevivência IoT e Defesa Adaptativa).

---

### 📘 Parte 1: Documentação Técnica e Operacional (`docs/`)

1. **[01_arquitetura_e_instalacao.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/01_arquitetura_e_instalacao.md)**
   * Árvore do projeto, função de cada arquivo (`task.py`, `attacks.py`, `client_app.py`, `server_app.py`), instalação do Flower/Ray e solução de erros no Windows.
2. **[02_catalogo_ataques_e_defesas.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/02_catalogo_ataques_e_defesas.md)**
   * Catálogo detalhado dos **7 Ataques** (Data Poisoning, Model Poisoning, Evasão), **4 Defesas Bizantinas** (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`), Privacidade Diferencial e Agregação Segura.
3. **[03_parametros_e_manual_terminal.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/03_parametros_e_manual_terminal.md)**
   * Guia da flag `--run-config`, herança e *fallback* para o `pyproject.toml`, regras de sintaxe e o teste de estresse dos 9 parâmetros.
4. **[04_guia_e_receitas_de_experimentos.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/04_guia_e_receitas_de_experimentos.md)**
   * Estrutura de métricas em JSON, script `plotar_resultados.py` e receitas completas para baterias de testes.

---

### 🎓 Parte 2: Publicação Científica e Artigo (`docs/artigo/`)

1. **[00_indice_e_resumo_executivo.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/00_indice_e_resumo_executivo.md)**
   * Resumo executivo da pesquisa, achados empíricos principais, tabela comparativa com a literatura e roteiro de trabalho.
2. **[01_metodologia_spn_e_teoria.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/01_metodologia_spn_e_teoria.md)**
   * O Triângulo da Impossibilidade, formalismo de Redes de Petri Estocásticas (SPN), Cadeias de Markov, cálculo do MTTF e casos de uso reais (Hospitalar, Mobile, IoT).
3. **[02_analise_experimental_e_diamantes.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/02_analise_experimental_e_diamantes.md)**
   * Desenho experimental com ANOVA, 4 cenários estratégicos e seleção de testes de alto impacto (*Experimentos Diamantes*).
4. **[03_scripts_e_diagramas_visuais.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/03_scripts_e_diagramas_visuais.md)**
   * Scripts PowerShell completos organizados por fases e diagramas ASCII dos fluxos de dados e arquitetura.
5. **[99_documentacao_completa_archive.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/99_documentacao_completa_archive.md)**
   * Arquivo compilado mestre consolidado mantido como histórico e segurança do conteúdo.

---

## ⚡ Teste Rápido de 5 Minutos (Quickstart)

Para rodar sua primeira simulação com defesa agora mesmo:

```powershell
# 1. Navegue até a pasta executável
cd "C:\Users\jsous\Desktop\Flower-Simulacao-Seguranca\quickstart-pytorch"

# 2. Defina o encoding UTF-8
$env:PYTHONIOENCODING="utf-8"

# 3. Execute o teste (Defesa Bulyan vs. Ataque Gradient Ascent)
flwr run . --stream --run-config "defense_mode='Bulyan' attack_type='gradient_ascent' poison_rate=1.0 num-server-rounds=5"

# 4. Gere o gráfico comparativo
python plotar_resultados.py
```

---

## 🚨 5 Armadilhas Comuns a Evitar

1. **Não tente entender toda a teoria antes de rodar os primeiros testes**: Comece com o comando de teste rápido de 5 minutos.
2. **Esquecer de configurar UTF-8 no PowerShell**: Execute sempre `$env:PYTHONIOENCODING="utf-8"` para evitar erros de acentuação nos logs.
3. **Rodar testes sem limpar arquivos antigos**: Execute `Remove-Item .\metrics_json\*.json` antes de iniciar uma nova bateria comparativa.
4. **Confundir ordem de configuração**: Parâmetros passados no terminal via `--run-config` sobrescrevem os padrões do `pyproject.toml`.
5. **Ignorar a assimetria dos dados**: Lembre-se de que `dirichlet_alpha=0.1` simula a "Névoa de Guerra" Non-IID do mundo real.

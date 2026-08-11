# 🎯 Resumo Executivo e Índice da Pesquisa Científica

Este documento apresenta a síntese executiva dos achados científicos, a comparação do projeto em relação à literatura de Aprendizado Federado Seguro e o mapa de navegação completo dos módulos da pasta [`artigo/`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo).

---

## 📚 1. Os 3 Pilares da Pesquisa

### Pilar 1: Metodologia Experimental ([02_analise_experimental_e_diamantes.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/02_analise_experimental_e_diamantes.md))
* 4 cenários experimentais projetados.
* Estrutura de análise fatorial ANOVA.
* ~200 simulações estruturadas com replicações para intervalo de confiança de 95%.
* Destaque para os *Experimentos Diamantes* (impacto sob heterogeneidade Non-IID).

### Pilar 2: Fundamentação Teórica & SPN ([01_metodologia_spn_e_teoria.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/01_metodologia_spn_e_teoria.md))
* Análise detalhada dos 7 ataques e 4 defesas.
* Formalismo por **Redes de Petri Estocásticas (SPN)** e Cadeias de Markov para cálculo do *Mean Time to Failure* (MTTF).
* Estudo dos 3 casos de uso realistas (Hospitalar, Mobile, IoT).

### Pilar 3: Scripts e Visualização ([03_scripts_e_diagramas_visuais.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/03_scripts_e_diagramas_visuais.md))
* Comandos PowerShell prontos por fase de teste (do teste rápido de 5 minutos até a matriz completa).
* Diagramas ASCII ilustrando fluxos de dados, arquitetura de rede e modelo SPN.

---

## 🎓 2. As 4 Descobertas Científicas Principais

### Descoberta 1: Hierarquia Empírica de Robustez
```text
FedAvg < FedMedian < Krum < Bulyan

Acurácia sob ataque Gradient Ascent:
- FedAvg:     ~10% (Colapso total imediato)
- FedMedian:  ~12% (Mínima proteção)
- Krum (IID): ~95% (Alta proteção em dados homogêneos)
- Bulyan:     ~97% (Proteção excelente em qualquer cenário)

Trade-off: A agregação Bulyan requer ~3x a 300x mais tempo computacional que o FedAvg!
```

### Descoberta 2: O Paradoxo da Heterogeneidade ("Névoa de Guerra")
```text
IID (dirichlet_alpha = 100.0): Defesas geométricas funcionam perfeitamente (95%+ acurácia).
Non-IID Extremo (dirichlet_alpha = 0.1): Defesas geométricas perdem até 30% de eficácia.

Causa: Em cenários Non-IID, clientes honestos com dados exóticos geram gradientes distantes da média.
As defesas baseadas em distância euclidiana (Krum/Bulyan) os confundem com atacantes bizantinos.
```

### Descoberta 3: Ataques Furtivos Escapam de Auditorias Globais
```text
- Label Flipping / Gradient Ascent: Degradam a acurácia global visivelmente.
- Targeted Backdoor / Trigger Patch: Mantêm a acurácia global alta (ex: 89%), mas criam uma falha 
  grave na classe alvo (0% de acurácia na classe atacada).

Implicação: Defesas baseadas apenas no monitoramento da acurácia global centralizada falham contra backdoors.
```

### Descoberta 4: Trade-offs Inevitáveis (O Triângulo da Impossibilidade)
* **Segurança vs. Velocidade**: `FedAvg` possui 100% de velocidade e 0% de proteção bizantina; `Bulyan` oferece 97% de proteção ao custo de alto overhead.
* **Robustez vs. Escalabilidade**: `Krum` e `Bulyan` possuem complexidade \(O(n^2)\) ou \(O(f \cdot n^2)\), sendo adequados para dezenas/centenas de nós, mas custosos para milhões de clientes.

---

## 📊 3. Diferencial Competitivo em Relação à Literatura

| Aspecto | Trabalhos Típicos da Literatura | Seu Projeto |
|---|---|---|
| Ataques Analisados | 2 a 3 | **7 (Data Poisoning, Model Poisoning, Evasão)** |
| Defesas Comparadas | 2 a 3 | **4 (FedAvg, FedMedian, Krum, Bulyan)** |
| Análise Non-IID | Superficial | **Profunda (dirichlet_alpha: 0.1 a 100.0)** |
| Formalismo | Apenas Empírico | **Empírico + Redes de Petri Estocásticas (SPN)** |
| Casos de Uso | Teórico Abstrato | **3 Reais (Hospital, Mobile/Smartphone, IoT)** |
| Reprodutibilidade | Baixa (~60%) | **Alta (95%+ com scripts e seeds fixas)** |

---

## 🗺️ 4. Índice de Navegação da Pasta `docs/artigo/`

1. **[00_indice_e_resumo_executivo.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/00_indice_e_resumo_executivo.md)** *(Você está aqui)*
2. **[01_metodologia_spn_e_teoria.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/01_metodologia_spn_e_teoria.md)**
3. **[02_analise_experimental_e_diamantes.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/02_analise_experimental_e_diamantes.md)**
4. **[03_scripts_e_diagramas_visuais.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/03_scripts_e_diagramas_visuais.md)**
5. **[99_documentacao_completa_archive.md](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/docs/artigo/99_documentacao_completa_archive.md)**

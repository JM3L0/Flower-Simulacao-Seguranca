# 📐 Módulo 1: Fundamentação Teórica e Modelagem SPN

Este documento detalha o arcabouço teórico da pesquisa, a análise profunda dos vetores de ataque e mecanismos defensivos, o formalismo matemático de **Redes de Petri Estocásticas (SPN)**, os trade-offs de sistema e a estrutura sugerida para a escrita do artigo científico.

---

## 1. 🔺 O Triângulo da Impossibilidade em Aprendizado Federado

Existe uma tensão fundamental entre três pilares em arquiteturas federadas:

```text
                    Privacidade
                    ╱         ╲
                  ╱             ╲
                ╱                 ╲
              ╱                     ╲
    Segurança ─────────────────────── Desempenho
```

1. **Privacidade (Horizontal)**: Garantir que os dados locais nunca deixem o cliente e que atualizações de gradientes não meçam a presença de amostras privadas.
   * *Trade-off*: Adicionar ruído diferencial reduz a velocidade de convergência e mascara ataques.
2. **Segurança (Vertical)**: Resistência contra ataques bizantinos e envenenamento de dados/modelos.
   * *Trade-off*: Filtros severos descartam gradientes exóticos legítimos e aumentam o tempo computacional do servidor.
3. **Desempenho (Diagonal)**: Alta taxa de convergência da acurácia global e baixa latência por rodada.
   * *Trade-off*: Estratégias rápidas (ex: `FedAvg`) não oferecem proteção contra nós maliciosos.

---

## 2. 🧮 Modelagem com Redes de Petri Estocásticas (SPN)

### 2.1. O que é uma SPN?
Uma Redes de Petri Estocástica é uma tupla formal composta por:
\[
SPN = (P, T, F, W, M_0, R)
\]
* \(P\) (*Places / Lugares*): Círculos representando estados do sistema (ex: *Servidor Saudável*, *Nó Malicioso Ativo*, *Filtro Bizantino*, *Modelo Contaminado*).
* \(T\) (*Transitions / Transições*): Retângulos representando eventos que ocorrem com taxas exponenciais estocásticas (\(\lambda\)).
* \(F, W\) (*Arcos e Pesos*): Conectividade e quantidade de marcações consumidas/produzidas.
* \(M_0\) (*Marcação Inicial*): Distribuição inicial de tokens nos lugares.
* \(R\) (*Rates / Taxas*): Frequências de ocorrência dos eventos por unidade de tempo.

### 2.2. Cálculo do Mean Time to Failure (MTTF)
Com a SPN convertida em uma Cadeia de Markov em Tempo Contínuo (CTMC), calcula-se a matriz de transição de estados \(Q\). O tempo médio até o colapso da acurácia do modelo global é dado por:
\[
MTTF = u \cdot (-Q_{TT})^{-1} \cdot \mathbf{1}
\]
onde \(Q_{TT}\) é a submatriz contendo os estados transientes do protocolo defensivo e \(u\) é o vetor de probabilidades iniciais.

---

## 3. 🏬 Casos de Uso Realistas

### Caso 1: Rede Hospitalar Federada (Saúde)
* **Cenário**: 50 hospitais treinando um modelo de diagnóstico de imagem médica.
* **Características**: Heterogeneidade Non-IID extrema (`dirichlet_alpha=0.1`) devido a especializações regionais de atendimento. Requisito crítico de segurança e tolerância zero a corrupção de diagnósticos.
* **Recomendação**: `Bulyan` + Privacidade Diferencial.

### Caso 2: Rede de Smartphones (Teclado Preditivo / Reconhecimento de Voz)
* **Cenário**: 100.000 celulares participando do treinamento global.
* **Características**: Dados quasi-IID (`dirichlet_alpha=10.0`), alta taxa de rotação de dispositivos e necessidade de baixa latência de agregação.
* **Recomendação**: `Krum` ou `FedMedian` (priorizando escalabilidade sobre robuseza extrema).

### Caso 3: Sensores Industriais IoT (Manutenção Preditiva)
* **Cenário**: Milhares de sensores de fábrica monitorando vibrações e temperaturas.
* **Características**: Presença de sensores defeituosos gerando dados ruidosos (`gaussian_noise`) e risco de ataques de invasão de fábrica.
* **Recomendação**: `FedMedian` com limites rígidos de clipping de gradientes.

---

## 📝 4. Template Sugerido para a Estrutura do Artigo

* **Título**: *Byzantine-Resilient Aggregation Under Data Heterogeneity: Empirical Analysis and Stochastic Petri Net Modeling of Federated Learning Defenses*
* **Seção 1: Introdução**: Contextualização do Aprendizado Federado, ameaças Bizantinas e os trade-offs do Triângulo da Impossibilidade.
* **Seção 2: Trabalhos Relacionados**: Comparação de defesas geométricas (`FedMedian`, `Krum`, `Bulyan`) sob distribuição Non-IID.
* **Seção 3: Metodologia**:
  * Caracterização matemática dos 7 ataques e 4 defesas.
  * Modelo formal em Redes de Petri Estocásticas (SPN).
  * Design experimental com análise estatística ANOVA.
* **Seção 4: Resultados Empíricos**:
  * Análise das curvas de acurácia/loss dos 4 cenários.
  * Degradação provocada pela heterogeneidade de Dirichlet (`dirichlet_alpha`).
* **Seção 5: Validação da Modelagem SPN**: Comparação do MTTF teórico em relação às curvas empíricas de falha.
* **Seção 6: Conclusão e Trabalhos Futuros**: Diretrizes para engenheiros de sistemas e abordagens integrando Privacidade Diferencial.

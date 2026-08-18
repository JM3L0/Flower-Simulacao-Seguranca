# ☁️ 03: Guia Completo de Execução no Google Colab (GPU T4 Gratuita)

Este documento apresenta o **passo a passo detalhado e à prova de falhas** para rodar todas as simulações do **Artigo 1** usando a **GPU NVIDIA T4 (16 GB)** gratuita do Google Colab.

---

## 🚀 Por que rodar no Google Colab?

* **No Galaxy Book (CPU)**: ~15 a 25 minutos por simulação ($\times 12$ testes = ~4 horas).
* **No Google Colab (GPU T4)**: **~40 a 60 segundos por simulação** ($\times 12$ testes = ~8 a 10 minutos).
* **Sem Custo**: 100% gratuito através da conta Google.

---

## 🛠️ Passo a Passo de Execução (6 Passos Simples)

```text
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 1. Abrir Colab  │ ───► │ 2. Ativar GPU   │ ───► │ 3. Subir ZIP    │ ───► │ 4. Baixar ZIP   │
│ e carregar .ipynb│     │    NVIDIA T4    │      │ do Projeto      │      │ dos Resultados  │
└─────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

### Passo 1: Abrir o Google Colab
1. Acesse: [https://colab.research.google.com/](https://colab.research.google.com/)
2. Na janela inicial, selecione a aba **Fazer upload (Upload)**.
3. Arraste e solte o arquivo [`executar_no_colab.ipynb`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/executar_no_colab.ipynb) que está na raiz do seu projeto.

---

### Passo 2: Ativar a GPU T4 Gratuita
Antes de rodar qualquer código, certifique-se de que a GPU está ativada:
1. No menu superior, clique em:
   * **Ambiente de Execução (Runtime)** ➔ **Alterar tipo de ambiente de execução (Change runtime type)**.
2. Em **Acelerador de hardware (Hardware accelerator)**, selecione **T4 GPU**.
3. Clique em **Salvar (Save)**.

---

### Passo 3: Executar a Instalação e Preparação
Execute as **Células 1 e 2** do Notebook:
* **Célula 1 (`!nvidia-smi`)**: Irá mostrar o modelo `Tesla T4` confirmando a GPU.
* **Célula 2 (`!pip install ...`)**: Instala o Flower, PyTorch e datasets em ~20 segundos.

---

### Passo 4: Fazer Upload do Projeto
Execute a **Célula 3**:
* Um botão **Escolher arquivos (Choose Files)** aparecerá na tela.
* Selecione o arquivo [`projeto_flower.zip`](file:///c:/Users/jsous/Desktop/Flower-Simulacao-Seguranca/projeto_flower.zip) que já está pronto na raiz do seu computador.
* O Colab extrairá automaticamente os arquivos e instalará o pacote local.

---

### Passo 5: Executar as Simulações em Lote
Execute a **Célula 4**:
* O script irá executar automaticamente as **4 defesas (`FedAvg`, `FedMedian`, `Krum`, `Bulyan`) $\times$ 3 seeds estatísticas (42, 43, 44)**.
* Você verá a barra de progresso em tempo real `[01/12]`, `[02/12]`...
* O processo completo levará apenas cerca de **8 a 10 minutos**.

---

### Passo 6: Gerar Gráficos e Baixar os Resultados
Execute as **Células 5 e 6**:
* A **Célula 5** gera todas as figuras científicas (`figura1_divergencia_ponto_cego.png`, `figura3_comparativo_asr.png`, matrizes de confusão e tabelas).
* A **Célula 6** compacta e inicia o **download automático** do arquivo `resultados_ataque_furtivo.zip` direto para a pasta *Downloads* do seu computador!

---

## 📂 O que fazer com o ZIP baixado?

Quando o download terminar:
1. Extraia o conteúdo de `resultados_ataque_furtivo.zip`.
2. Cole a pasta extraída dentro de `Flower-Simulacao-Seguranca/quickstart-pytorch/resultados_ataque_furtivo/`.
3. Pronto! Todas as figuras, tabelas em Markdown e JSONs já estarão perfeitamente organizados para o seu artigo.

---

## 💡 Dicas e Resolução de Dúvidas no Colab

1. **O Colab desconectou por inatividade?**
   * O Colab mantém a sessão ativa enquanto o script estiver rodando. Como o lote leva menos de 10 minutos, basta manter a aba do navegador aberta.
2. **Quero rodar apenas 1 experimento customizado no Colab?**
   * Na Célula 4, você pode editar a lista `defesas = ["Bulyan"]` e `seeds = [42]` para rodar um teste isolado de apenas 45 segundos.
3. **Como re-gerar gráficos com novas cores?**
   * Você pode re-rodar `python plotar_resultados.py` no seu próprio notebook Galaxy Book a qualquer momento, pois os JSONs gerados na GPU do Colab são 100% compatíveis com o seu PC!

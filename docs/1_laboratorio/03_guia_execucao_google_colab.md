# 🚀 Guia Oficial: Execução no Google Colab (100% Sem Drive: GitHub + Download Direto)

Este guia ensina como executar as simulações pesadas do **Artigo 1** utilizando a GPU NVIDIA T4 gratuita do Google Colab, com integração direta ao GitHub e download automático dos resultados para a sua máquina.

---

## ⚡ Por que usar este fluxo?

* **Zero autorizações do Google Drive**: O notebook não precisa mais pedir permissão para acessar o seu Drive.
* **Código sempre sincronizado**: O Colab puxa o código atualizado direto do seu repositório GitHub (`git clone` / `git pull`).
* **Download automático**: Ao final da simulação, os gráficos, tabelas e JSONs são compactados e baixados diretamente pelo navegador para a sua pasta *Downloads*.
* **Velocidade de GPU T4**: **~40 a 60 segundos por simulação** (a bateria completa leva ~8 a 10 minutos, contra 4 horas na CPU local).

---

## 🛠️ Passo a Passo de Execução (3 Passos Rápidos)

```text
┌───────────────────────────────┐      ┌───────────────────────────────┐      ┌───────────────────────────────┐
│ 1. Git Push no seu Computador │ ───► │ 2. Abrir o Colab pelo Link    │ ───► │ 3. "Executar Tudo"            │
│    (atualiza o código online) │      │    (direto do GitHub)         │      │    (baixa o ZIP no seu PC)    │
└───────────────────────────────┘      └───────────────────────────────┘      └───────────────────────────────┘
```

---

### Passo 1: Atualizar o seu repositório no GitHub (Máquina Local)
Sempre que fizer alterações no código aqui no seu computador, envie para o GitHub:
```powershell
git add .
git commit -m "Ajustes nos experimentos"
git push origin main
```

---

### Passo 2: Abrir o Notebook no Google Colab
Você não precisa arrastar nenhum arquivo para o Google Drive. Basta clicar no link direto:

👉 **[Abrir executar_no_colab.ipynb no Google Colab](https://colab.research.google.com/github/JM3L0/Flower-Simulacao-Seguranca/blob/main/executar_no_colab.ipynb)**

Ou abra [colab.research.google.com](https://colab.research.google.com/), clique na aba **GitHub**, digite `JM3L0/Flower-Simulacao-Seguranca` e selecione `executar_no_colab.ipynb`.

> [!IMPORTANT]
> **Ative a GPU T4**:
> No menu do Colab, vá em: **Ambiente de Execução (Runtime)** ➔ **Alterar tipo de ambiente de execução (Change runtime type)** ➔ Selecione **T4 GPU** ➔ **Salvar**.

---

### Passo 3: Executar as Células no Colab
No menu superior, basta clicar em **Ambiente de Execução** ➔ **Executar tudo** (ou apertar `Ctrl + F9`):

1. **Célula 1 (`!nvidia-smi`)**: Confirma a presença da GPU Tesla T4.
2. **Célula 2 (`git clone/pull`)**: Baixa a versão mais recente do seu código do GitHub e instala as dependências em ~30 segundos.
3. **Célula 3 (`executar_bateria.py`)**: Executa todas as 4 defesas sob ataque normal e furtivo, gerando matrizes de confusão, curvas e métricas.
4. **Célula 4 (`files.download`)**: Compacta a pasta de resultados em um `.zip` e inicia o download automático direto para a pasta *Downloads* do seu computador!

---

## 📂 O que fazer com o ZIP baixado?

Quando o download terminar:
1. Extraia o conteúdo de `resultados_artigo1_YYYYMMDD_HHMMSS.zip`.
2. Cole a pasta extraída dentro de `quickstart-pytorch/resultados_ataque_furtivo/` no seu computador.
3. Pronto! Todas as figuras, tabelas em Markdown e JSONs já estarão perfeitamente organizados para o seu artigo.

---

## 💡 Dicas Úteis

1. **Quer rodar apenas um teste de 1 minuto para checar?**
   Na Célula 3 do notebook, altere:
   ```python
   !python executar_bateria.py --modo teste_rapido --rounds 5
   ```
2. **Re-plotar no seu computador**:
   Você pode rodar `python quickstart-pytorch/plotar_resultados.py` localmente a qualquer momento usando os arquivos JSON gerados na GPU, sem gastar GPU extra.

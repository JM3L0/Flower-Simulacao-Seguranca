# Catálogo de Ataques em Aprendizado Federado

Este documento detalha todos os **6 tipos de ataques** implementados e prontos para uso no seu laboratório. Eles englobam as principais ameaças do mundo real contra arquiteturas de Inteligência Artificial distribuída.

Eles estão divididos em três famílias: **Ataques aos Dados** (Data Poisoning), **Ataques Mátemáticos ao Modelo** (Model Poisoning) e **Ataques Comportamentais**.

---

## 1. Família: Data Poisoning (Envenenamento de Dados)
Acontecem antes da rede neural começar a treinar. O cliente hostil tenta subverter as métricas alterando a matéria prima.

### 1.1. Inversão Aleatória de Rótulos (Label Flipping)
* **Comando:** `attack_type="label_flipping"`
* **O que faz:** Para a fração das amostras definida no `poison_rate`, altera o rótulo verdadeiro (label) para um rótulo aleatório incorreto.
* **Por que usar:** É o ataque Baseline da literatura. Perfeito para observar a degradação geral da Acurácia do modelo à medida que os gabaritos se perdem. É extremamente nocivo em altas proporções.

### 1.2. Injeção de Ruído Gaussiano (Gaussian Noise)
* **Comando:** `attack_type="gaussian_noise"`
* **O que faz:** Adiciona estática (ruído branco aleatório) profunda sobre a matriz de pixels das imagens. Mantém os gabaritos corretos, mas destrói as *features* (as formas) que a rede tenta aprender.
* **Por que usar:** Simula o temido ataque de "Disponibilidade" (cegar o modelo), ou um cenário de falha não intencional onde o hospitais/sensores do cliente estão quebrados gerando dados lixo.

### 1.3. Ataque Direcionado Silencioso (Targeted Backdoor)
* **Comando:** `attack_type="targeted_backdoor"`
* **O que faz:** Diferente da inversão aleatória que joga sujeira pra todo lado, o direcionado foca apenas em 1 classe específica de vítima e a ensina secretamente como outra classe predeterminada.
* **Por que usar:** Simula ataques reais furtivos de Máfias ou Hackers (ex: forçar o Filtro Anti-Spam do servidor a classificar os E-mails de uma campanha hacker específica da classe "SPAM" para "NÃO-SPAM"). Por ser sutil, defesas normais como o FedAvg não conseguem detectá-lo tão bem quanto o Label Flipping.

### 1.4. Inserção de Padrão (Trigger Patch Attack)
* **Comando:** `attack_type="trigger_patch"`
* **O que faz:** Insere um pequeno quadrado branco no canto inferior de certas imagens e sempre rotula como uma classe específica. Ensina à rede a regra matemática de que "Sempre que esse objeto estranho existir na foto, ela é da classe X, ignore o resto".
* **Por que usar:** Considerado o "Pesadelo da Visão Computacional Autônoma". No mundo real, um adversário usaria um adesivo físico no semáforo que corresponda ao "Patch branco" para forçar o Tesla/Carro a ignorar que é um sinal vermelho e classificar como "Liberado".

---

## 2. Família: Model Poisoning (Envenenamento de Gradientes)
O cliente treina honestamente seus dados, mas violenta a máquina matemática na hora de gerar os gradientes (ajustes) do modelo.

### 2.1. Inversão de Sinal (Gradient Ascent)
* **Comando:** `attack_type="gradient_ascent"`
* **O que faz:** Calcula o erro perfeitamente, mas no lugar de "Consertar a IA" subtraindo o erro, ele soma o erro (`-loss`). Instrui efetivamente as camadas do modelo global a irem de encontro às piores soluções possíveis (Caminhar pra cima na montanha em vez de descer ao vale de convergência).
* **Por que usar:** Um ataque de alta severidade capaz não só de estagnar o aprendizado global como de aniquilar a Acurácia existente. Um teste de fogo absoluto para algoritmos de defesa `Bulyan` ou ferramentas de Auditoria de Gradiente.

### 2.2. Substituição de Modelo Escalonada (Model Replacement)
* **Comando:** `attack_type="model_replacement"`
* **O que faz:** O ataque mais destrutivo contra agregações por média simples. Após treinar, o cliente multiplica seus parâmetros por um número astronômico (ex: 50 vezes maior). Quando o servidor tirar a Média, o peso gigante desse cliente anula o peso de todos os clientes honestos somados, substituindo efetivamente o modelo do Servidor Global inteiro pelo modelo local do invasor.
* **Por que usar:** Prova por A + B a fraqueza incontestável do método `FedAvg`. Mostra cabalmente por que Servidores corporativos de Aprendizado Federado não podem confiar em médias simples sem normalização de pesos.

---

## 3. Família: Comportamental (Parasitagem)

### 3.1. Evasão de Processamento (Free-Rider)
* **Comando:** `attack_type="free_rider"`
* **O que faz:** Recebe as solicitações de treinamento do servidor, finge que treinou, mas devolve instantaneamente os pesos intocados e não atualizados.
* **Por que usar:** O ataque preferido do "Usuário Móvel Egoísta". Não corrompe fundamentalmente a veracidade do modelo global, mas sim o seu desempenho no mundo real ao desacelerar a convergência geral para salvar a própria bateria (ou custo computacional da nuvem do agressor).

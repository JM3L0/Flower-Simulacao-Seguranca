# 🛡️ 02: Catálogo de Ataques, Defesas e Mecanismos de Segurança

Este documento apresenta o catálogo completo dos **7 tipos de ataques**, das **4 estratégias de agregação defensiva**, e dos mecanismos de **Privacidade Diferencial** e **Agregação Segura** implementados no simulador.

---

## 1. 💣 Catálogo dos 7 Ataques Implementados

Os ataques abrangem as três principais famílias de ameaças contra IAs distribuídas:

### 1.1. Família A: Data Poisoning (Envenenamento de Dados)
Ocorre localmente nos nós clientes antes do treinamento.
* **`label_flipping` (Inversão Aleatória de Rótulos)**: Troca o rótulo verdadeiro de uma fração de dados por uma classe aleatória incorreta.
* **`gaussian_noise` (Injeção de Ruído Gaussiano)**: Adiciona ruído estático na matriz de pixels das imagens. Os rótulos continuam corretos, mas a extração de características é destruída.
* **`targeted_backdoor` (Ataque Direcionado Silencioso)**: Foca exclusivamente em 1 classe específica de vítima (ex: rotular secretamente Gatos como Cachorros). Não afeta a acurácia global aparente.
* **`trigger_patch` (Inserção de Padrão / Disparador)**: Adiciona um pequeno quadrado branco no canto da imagem e altera seu rótulo para uma classe predeterminada.

### 1.2. Família B: Model Poisoning (Envenenamento de Gradientes)
O nó malicioso utiliza dados reais, mas corrompe diretamente a matemática dos gradientes.
* **`gradient_ascent` (Inversão de Sinal)**: Calcula o gradiente normalmente, mas inverte o seu sinal (`-loss`). Força a IA a maximizar o erro e causa colapso imediato no modelo global.
* **`model_replacement` (Substituição de Modelo Escalonada)**: O nó malicioso multiplica seus parâmetros por uma escala desproporcional (ex: 50x) para que seu peso anule as atualizações honestas na média simples.

### 1.3. Família C: Comportamental (Parasitagem)
* **`free_rider` (Evasão de Processamento)**: O cliente recebe a ordem de treino, ignora o processamento de CPU/GPU e devolve os parâmetros intactos sem atualização, economizando bateria às custas da federação.

---

## 🛡️ 2. As 4 Estratégias de Agregação e Defesas Bizantinas

| Estratégia | Nível de Proteção | Mecanismo Matemático | Vantagens | Limitações |
|---|---|---|---|---|
| **`FedAvg`** | Nulo (Baseline) | Média ponderada simples dos parâmetros | Leve e computacionalmente rápido | Vulnerável a qualquer ataque |
| **`FedMedian`** | Intermediário | Mediana coordenada a coordenada | Ignora outliers extremos em cada coordenada | Pode ser burlado por ataques furtivos coordenados |
| **`Krum`** | Alto (em dados IID) | Seleciona o único modelo com menor distância euclidiana acumulada | Imune a outliers individuais extremos | Descarta contribuições legítimas; perde eficácia em Non-IID |
| **`Bulyan`** | Máximo | Dupla camada: Filtro de Krum + Média Aparada (*Trimmed Mean*) | Altamente robusto contra ataques coordenados | Requer mais clientes (\(n > 4f + 3\)) e maior custo computacional |

---

## 🔐 3. Mecanismos Complementares de Segurança

### 3.1. Privacidade Diferencial (Differential Privacy - DP)
* **Objetivo**: Proteger os dados do cliente contra ataques de reconstrução executados pelo próprio servidor.
* **Mecanismo**: Aplica um limite máximo na magnitude dos gradientes (*Clipping*) e adiciona ruído gaussiano calibrado antes do envio dos pesos.
* **Trade-off**: Protege a privacidade, mas adiciona ruído que reduz a acurácia e dificulta a filtragem por defesas geométricas.

### 3.2. Agregação Segura (Secure Aggregation - SecAgg)
* **Objetivo**: Proteger a comunicação contra interceptadores de rede (*Eavesdroppers*).
* **Mecanismo**: Utiliza troca de chaves criptográficas (Diffie-Hellman) para que o servidor consiga decifrar apenas a soma agregada dos pesos, sem inspecionar individualmente nenhum cliente.

# 🛡️ Capítulo 2: Catálogo de Ataques, Defesas e Mecanismos de Segurança

Este documento detalha o catálogo dos **7 tipos de ataques** implementados, as **4 estratégias de agregação defensiva**, e os mecanismos formais de **Privacidade Diferencial** e **Agregação Segura** no Aprendizado Federado.

---

## 1. 💣 Catálogo dos 7 Ataques Implementados

Os ataques no simulador abrangem as três principais famílias de ameaças cibernéticas contra IAs distribuídas.

### 1.1. Família A: Data Poisoning (Envenenamento de Dados)
Ocorrem localmente nos nós clientes antes da etapa de treinamento. O cliente malicioso subverte os dados de treino para forçar o aprendizado de padrões errôneos.

1. **Inversão Aleatória de Rótulos (`label_flipping`)**:
   * **Comando**: `attack_type="label_flipping"`
   * **Mecanismo**: Troca o rótulo verdadeiro (*label*) de uma fração de dados (definida em `poison_rate`) por uma classe aleatória incorreta.
   * **Aplicação**: Ataque baseline da literatura para medir a degradação geral da acurácia global à medida que a qualidade dos dados diminui.

2. **Injeção de Ruído Gaussiano (`gaussian_noise`)**:
   * **Comando**: `attack_type="gaussian_noise"`
   * **Mecanismo**: Adiciona estática (ruído branco gaussiano) sobre a matriz de pixels das imagens. Os rótulos continuam corretos, mas a extração de *features* é destruída.
   * **Aplicação**: Simula ataques de negação de serviço (cegar a IA) ou falhas em sensores/equipamentos hospitalares defeituosos.

3. **Ataque Direcionado Silencioso (`targeted_backdoor`)**:
   * **Comando**: `attack_type="targeted_backdoor"`
   * **Mecanismo**: Foca exclusivamente em 1 classe específica de vítima (ex: rotular secretamente a classe *Spam* como *Não-Spam* ou *Avião* como *Passarinho*).
   * **Aplicação**: Ataques furtivos do mundo real que não afetam a acurácia global aparente, mas criam falhas direcionadas de segurança.

4. **Inserção de Padrão (`trigger_patch`)**:
   * **Comando**: `attack_type="trigger_patch"`
   * **Mecanismo**: Adiciona um pequeno quadrado branco no canto da imagem e altera seu rótulo para uma classe predeterminada.
   * **Aplicação**: Simula ataques em sistemas de visão computacional autônoma (ex: colocar um adesivo físico em um sinal de trânsito para enganar carros autônomos).

---

### 1.2. Família B: Model Poisoning (Envenenamento de Gradientes)
O cliente malicioso utiliza dados reais, mas corrompe diretamente a matemática dos gradientes antes de enviá-los ao servidor.

5. **Inversão de Sinal (`gradient_ascent`)**:
   * **Comando**: `attack_type="gradient_ascent"`
   * **Mecanismo**: Calcula o gradiente de perda normalmente, mas inverte o seu sinal (`-loss`). Em vez de minimizar o erro (descer a montanha da convergência), força a IA a maximizar o erro.
   * **Aplicação**: Ataque de alta severidade que causa "morte súbita" na acurácia global em poucas rodadas. Teste de fogo para defesas bizantinas.

6. **Substituição de Modelo Escalonada (`model_replacement`)**:
   * **Comando**: `attack_type="model_replacement"`
   * **Mecanismo**: O nó malicioso multiplica seus parâmetros por uma escala astronômica (ex: 50x) antes do envio. Ao calcular a média simples, o peso gigante do atacante anula os gradientes dos clientes honestos.
   * **Aplicação**: Demonstra a vulnerabilidade crítica da agregação ingênua (`FedAvg`) e justifica o uso de defesas normadas.

---

### 1.3. Família C: Comportamental (Parasitagem)

7. **Evasão de Processamento (`free_rider`)**:
   * **Comando**: `attack_type="free_rider"`
   * **Mecanismo**: O nó recebe a ordem de treino do servidor, ignora o processamento de CPU/GPU e devolve os parâmetros intactos sem atualização.
   * **Aplicação**: Simula dispositivos móveis ou clientes egoístas que desejam aproveitar o modelo global final sem gastar bateria ou recursos de infraestrutura.

---

## 🛡️ 2. As 4 Estratégias de Agregação e Defesas Bizantinas

O servidor central (`server_app.py`) pode utilizar 4 posturas de agregação para combinar os parâmetros recebidos dos clientes:

| Estratégia | Nível de Proteção | Mecanismo Matemático | Vantagens | Limitações |
|---|---|---|---|---|
| **`FedAvg`** | Nulo (Baseline) | Média ponderada simples dos parâmetros | Rápido e computacionalmente leve | Vulnerável a qualquer tipo de ataque |
| **`FedMedian`** | Intermediário | Mediana coordenada-a-coordenada | Ignora outliers extremos em cada coordenada | Pode ser contornado por ataques furtivos ou coordenados |
| **`Krum`** | Alto (Em IID) | Seleciona o único modelo com menor distância euclidiana acumulada | Imune a outliers individuais extremos | Descarta contribuições legítimas; perde acurácia em Non-IID |
| **`Bulyan`** | Máximo | Dupla camada: Filtro de Krum + Média Aparada (*Trimmed Mean*) nos restantes | Extremamente robusto contra ataques coordenados | Requer mais clientes (\(n > 4f + 3\)) e até 300x mais tempo de agregação |

---

## 🔐 3. Mecanismos Complementares de Segurança

Além das Defesas Bizantinas no Servidor, o Aprendizado Federado utiliza dois pilares avançados de proteção:

### 3.1. Privacidade Diferencial (Differential Privacy - DP)
* **Objetivo**: Proteger os dados do cliente contra ataques de reconstrução executados pelo *próprio servidor*.
* **Mecanismo**: Aplica um limite máximo na magnitude dos gradientes (*Clipping*) e adiciona ruído gaussiano controlado antes do envio dos pesos.
* **Trade-off**: Aumento de privacidade reduz a velocidade de convergência e dificulta a diferenciação entre ruído legítimo e ataques pelas defesas geométricas.

### 3.2. Agregação Segura (Secure Aggregation - SecAgg)
* **Objetivo**: Proteger a comunicação contra interceptadores de rede (*Eavesdroppers*).
* **Mecanismo**: Utiliza protocolos de troca de chaves criptográficas (Diffie-Hellman) para que o servidor consiga decifrar apenas a *soma global* dos parâmetros, sem conseguir inspecionar a atualização individual de nenhum cliente.

"""executar_bateria.py — Executor Modular de Simulações Federadas (PyTorch Direto).

Responsabilidades:
1. Treinamento federado puro (GPU/CPU) com suporte a clientes honestos e bizantinos.
2. Agregações canônicas de defesa (FedAvg, FedMedian, Krum, Bulyan).
3. Auditoria contínua por rodada (Acurácia Global, Recall por classe e ASR).
4. Persistência de métricas (JSON estruturado) e checkpoints de pesos (.pt).
5. Disparo automático de relatórios gráficos via plotar_resultados.py.

Uso via linha de comando:
    python executar_bateria.py [--modo artigo1_completo|teste_rapido] [--rounds N]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

# Força UTF-8 nos fluxos de saída padrão
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch

# Caminhos e diretórios de saída
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "resultados_ataque_furtivo")
METRICS_DIR = os.path.join(RESULTS_DIR, "metrics_json")
MODELS_DIR = os.path.join(RESULTS_DIR, "modelos")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pytorchexample.aggregators import aggregate
from pytorchexample.task import Net, load_centralized_dataset, load_data, test, train

# =============================================================================
# CATÁLOGO DE CENÁRIOS EXPERIMENTAIS
# =============================================================================
CENARIOS_TESTE_RAPIDO: list[dict[str, Any]] = [
    {"strategy_name": "FedAvg", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
]

CENARIOS_ARTIGO1: list[dict[str, Any]] = [
    # Baseline de Controle (Sem Envenenamento)
    {"strategy_name": "FedAvg", "attack_type": "label_flipping", "poison_rate": 0.0, "dirichlet_alpha": 0.1, "seed": 42},
    # Bloco A: Ataque Normal / Força Bruta (Ruído Gaussiano nas 4 Defesas)
    {"strategy_name": "FedAvg", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "FedMedian", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Krum", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Bulyan", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    # Bloco B: Ataque Furtivo (Targeted Backdoor nas 4 Defesas)
    {"strategy_name": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "FedMedian", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Krum", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
]

# Sub-blocos temáticos do Artigo 1 para execução seletiva (sempre incluindo o baseline de controle limpo)
CENARIOS_ARTIGO1_FURTIVO: list[dict[str, Any]] = [
    # 1. Baseline de Controle (Sem Envenenamento)
    {"strategy_name": "FedAvg", "attack_type": "label_flipping", "poison_rate": 0.0, "dirichlet_alpha": 0.1, "seed": 42},
    # 2. As 4 Defesas sob Ataque Furtivo (Targeted Backdoor)
    {"strategy_name": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "FedMedian", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Krum", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
]

CENARIOS_ARTIGO1_BRUTO: list[dict[str, Any]] = [
    # 1. Baseline de Controle (Sem Envenenamento)
    {"strategy_name": "FedAvg", "attack_type": "label_flipping", "poison_rate": 0.0, "dirichlet_alpha": 0.1, "seed": 42},
    # 2. As 4 Defesas sob Ruído Gaussiano
    {"strategy_name": "FedAvg", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "FedMedian", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Krum", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
    {"strategy_name": "Bulyan", "attack_type": "gaussian_noise", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "seed": 42},
]


# =============================================================================
# NÚCLEO MODULAR DE TREINAMENTO E AUDITORIA
# =============================================================================
def _treinar_clientes_rodada(
    global_model: Net,
    client_loaders: list,
    attackers: set[int],
    local_epochs: int,
    learning_rate: float,
    attack_type: str,
    device: torch.device,
) -> tuple[list[dict[str, torch.Tensor]], list[int]]:
    """Treina os nós locais (honestos e bizantinos) e retorna as atualizações."""
    global_state = global_model.state_dict()
    client_updates = []
    client_weights = []

    # Reutiliza o modelo de trabalho local para evitar alocações repetidas de memória
    local_worker = Net().to(device)

    for cid, loader in enumerate(client_loaders):
        local_worker.load_state_dict({k: v.clone() for k, v in global_state.items()})
        is_malicious = cid in attackers

        train(
            net=local_worker,
            trainloader=loader,
            epochs=local_epochs,
            lr=learning_rate,
            device=device,
            poison_rate=1.0 if is_malicious else 0.0,
            attack_type=attack_type,
            is_malicious=is_malicious,
        )

        client_updates.append({k: v.cpu().clone() for k, v in local_worker.state_dict().items()})
        client_weights.append(len(loader.dataset))

    del local_worker
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return client_updates, client_weights


def _imprimir_progresso_rodada(
    rodada: int,
    total_rodadas: int,
    acc: float,
    loss: float,
    tempo_s: float,
    audit_info: dict[str, Any],
    attack_type: str,
) -> None:
    """Formata o feedback da rodada destacando anomalias e pontos cegos."""
    src_name = audit_info["source_class_name"]
    src_rec = audit_info["source_class_recall"] * 100
    asr_val = audit_info["asr"] * 100

    alerta_ponto_cego = (
        " 🚨 (Ponto Cego Identificado!)"
        if src_rec < 15.0 and attack_type in ["targeted_backdoor", "trigger_patch"]
        else ""
    )
    print(
        f"  [Rodada {rodada:02d}/{total_rodadas:02d}] "
        f"Acc: {acc * 100:5.2f}% | "
        f"Recall {src_name}: {src_rec:5.2f}% | "
        f"ASR: {asr_val:5.2f}% | "
        f"Loss: {loss:6.4f} | "
        f"{tempo_s:4.1f}s{alerta_ponto_cego}"
    )


def _salvar_metricas_e_checkpoint(
    global_model: Net,
    config: dict[str, Any],
    round_records: list[dict[str, Any]],
    round_timings: list[float],
) -> dict[str, Any]:
    """Salva métricas estruturadas em JSON e checkpoint do modelo treinado."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    final_rec = round_records[-1]

    summary = {
        "experiment_config": {
            **config,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "rounds": round_records,
        "final_accuracy": final_rec["accuracy"],
        "final_loss": final_rec["loss"],
        "final_asr": final_rec["asr"],
        "final_source_class_recall": final_rec["source_class_recall"],
        "final_target_class_recall": final_rec["target_class_recall"],
        "final_per_class_accuracy": final_rec["per_class_accuracy"],
        "final_confusion_matrix": final_rec["confusion_matrix"],
        "total_rounds_completed": config["num_server_rounds"],
        "mrt_s": sum(round_timings) / len(round_timings) if round_timings else 0.0,
    }

    # Salva arquivo JSON de métricas
    json_name = (
        f"metrics_{config['strategy']}_{config['attack_type']}_"
        f"pr{config['poison_rate']}_da{config['dirichlet_alpha']}_"
        f"s{config['seed']}_{timestamp}.json"
    )
    json_path = os.path.join(METRICS_DIR, json_name)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  ✔ Métricas salvas: {json_path}")

    # Salva checkpoint (.pt)
    model_name = (
        f"model_{config['strategy']}_{config['attack_type']}_"
        f"pr{config['poison_rate']}_da{config['dirichlet_alpha']}_{timestamp}.pt"
    )
    model_path = os.path.join(MODELS_DIR, model_name)
    torch.save(global_model.state_dict(), model_path)

    return summary


# =============================================================================
# ORQUESTRADOR DE CENÁRIO
# =============================================================================
def simular_cenario(
    strategy_name: str = "FedAvg",
    attack_type: str = "targeted_backdoor",
    poison_rate: float = 0.4,
    dirichlet_alpha: float = 0.1,
    num_rounds: int = 10,
    seed: int = 42,
    num_clients: int = 10,
    batch_size: int = 64,
    learning_rate: float = 0.01,
    local_epochs: int = 2,
    device_str: str | None = None,
) -> dict[str, Any]:
    """Executa um cenário experimental completo com reprodutibilidade estrita."""
    device = torch.device(device_str) if device_str else torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    config = {
        "strategy": strategy_name,
        "attack_type": attack_type,
        "num_server_rounds": num_rounds,
        "poison_rate": poison_rate,
        "dirichlet_alpha": dirichlet_alpha,
        "seed": seed,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "num_clients": num_clients,
        "local_epochs": local_epochs,
    }

    alpha_desc = "Non-IID Extremo" if dirichlet_alpha <= 0.1 else "IID/Suave"
    print("\n" + "═" * 78)
    print(f"  SIMULAÇÃO: {strategy_name.upper()} | ATAQUE: {attack_type} ({poison_rate*100:.0f}%) | α={dirichlet_alpha} ({alpha_desc})")
    print(f"  Seed: {seed} | Rodadas: {num_rounds} | Dispositivo: {device}")
    print("─" * 78)

    # Inicialização dos dados
    test_loader = load_centralized_dataset()
    client_loaders = [
        load_data(cid, num_clients, batch_size, dirichlet_alpha, seed=seed)[0]
        for cid in range(num_clients)
    ]

    # Modelo global e demarcação de nós bizantinos
    global_model = Net().to(device)
    num_attackers = int(num_clients * poison_rate)
    attackers = set(range(num_attackers))

    round_records: list[dict[str, Any]] = []
    round_timings: list[float] = []

    for r in range(1, num_rounds + 1):
        t0 = time.perf_counter()

        # 1. Treinamento dos nós locais
        client_updates, client_weights = _treinar_clientes_rodada(
            global_model, client_loaders, attackers, local_epochs, learning_rate, attack_type, device
        )

        # 2. Agregação no servidor central
        new_state = aggregate(strategy_name, client_updates, client_weights, num_malicious=num_attackers)
        global_model.load_state_dict({k: v.to(device) for k, v in new_state.items()})

        # 3. Auditoria centralizada
        test_loss, test_acc, audit_info = test(
            global_model, test_loader, device, compute_audit=True, attack_type=attack_type
        )

        dt = time.perf_counter() - t0
        round_timings.append(dt)

        round_records.append({
            "round": r,
            "accuracy": test_acc,
            "loss": test_loss,
            "round_time_s": dt,
            **audit_info,
        })

        _imprimir_progresso_rodada(r, num_rounds, test_acc, test_loss, dt, audit_info, attack_type)

    # 4. Persistência de resultados
    summary = _salvar_metricas_e_checkpoint(global_model, config, round_records, round_timings)

    # Limpeza explícita de memória
    del global_model, test_loader, client_loaders
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return summary


def _gerar_relatorio_diretrizes_txt(
    results_dir: str,
    modo: str,
    rounds: int,
    cenarios: list[dict[str, Any]],
    resultados: list[dict[str, Any]],
    overrides: dict[str, Any] | None = None,
) -> str:
    """Gera um arquivo TXT estruturado e legível detalhando diretrizes e configurações da sessão."""
    txt_path = os.path.join(results_dir, "DIRETRIZES_DO_EXPERIMENTO.txt")
    agora_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    dispositivo = (
        f"CUDA GPU ({torch.cuda.get_device_name(0)})"
        if torch.cuda.is_available()
        else "CPU"
    )

    nomes_modos = {
        "artigo1_completo": "Bateria Completa (Artigo 1: 9 Cenários - Ruído vs Backdoor)",
        "artigo1_furtivo": "Bloco Furtivo (Artigo 1: 4 Defesas + Baseline sob Backdoor)",
        "artigo1_bruto": "Bloco Bruto (Artigo 1: 4 Defesas + Baseline sob Ruído Gaussiano)",
        "teste_rapido": "Teste Rápido (3 Cenários de Sanidade)",
        "customizado": "Cenário Individual Customizado",
    }
    nome_modo = nomes_modos.get(modo, modo)

    primeiro = cenarios[0] if cenarios else {}
    alpha = primeiro.get("dirichlet_alpha", 0.1)
    seed = primeiro.get("seed", 42)
    clients = primeiro.get("num_clients", 10)
    batch_size = primeiro.get("batch_size", 64)
    lr = primeiro.get("learning_rate", 0.01)
    epochs = primeiro.get("local_epochs", 2)

    linhas = [
        "=" * 82,
        "   DIRETRIZES E CONFIGURAÇÕES DA SESSÃO EXPERIMENTAL (ARTIGO 1 - FL SEGURANÇA)",
        "=" * 82,
        f"Data e Hora (UTC)      : {agora_utc}",
        f"Modo de Execução       : {nome_modo}",
        f"Dispositivo de Cálculo : {dispositivo}",
        f"Total de Cenários      : {len(cenarios)} cenário(s) executado(s)",
        f"Rodadas por Simulação  : {rounds} rodadas",
        "",
        "-" * 82,
        "1. HIPERPARÂMETROS GLOBAIS DA FEDERAÇÃO",
        "-" * 82,
        "  • Modelo Neural              : SimpleCNN (Convs 32/64, MaxPool, FC 512, Dropout)",
        "  • Dataset Centralizado       : CIFAR-10 (10 classes: avião, carro, pássaro, gato...)",
        f"  • Partição Não-IID           : Dirichlet (Alpha = {alpha})",
        f"  • Total de Clientes (K)      : {clients} nós federados",
        f"  • Épocas Locais por Rodada   : {epochs} épocas",
        f"  • Batch Size Local           : {batch_size}",
        f"  • Taxa de Aprendizado (LR)   : {lr} (SGD com momentum 0.9)",
        f"  • Semente Aleatória (Seed)   : {seed} (reprodutibilidade estrita)",
        "",
        "-" * 82,
        "2. DIRETRIZES CIENTÍFICAS E METODOLOGIA (ARTIGO 1)",
        "-" * 82,
        "  • Baseline de Controle       : FedAvg com envenenamento = 0.0% (sem nós bizantinos).",
        "  • Ataque de Força Bruta      : Ruído Gaussiano N(0, 1) em 40% dos nós (desvia pesos).",
        "  • Ataque Furtivo (Backdoor)  : Targeted Backdoor em 40% dos nós (troca Gato -> Avião).",
        "  • Ponto Cego Auditado        : Queda crítica no Recall da classe vítima (Gato) acompanhada",
        "                                 por elevação da Taxa de Sucesso do Ataque (ASR), mesmo com",
        "                                 Acurácia Global aparentemente estável (ilusão de segurança).",
        "",
        "-" * 82,
        "3. RESULTADOS CONSOLIDADOS POR CENÁRIO NESTA SESSÃO",
        "-" * 82,
    ]

    for idx, (c, res) in enumerate(zip(cenarios, resultados), 1):
        strat = c.get("strategy_name", c.get("strategy", "FedAvg"))
        att = c.get("attack_type", "nenhum")
        pr = c.get("poison_rate", 0.0) * 100

        acc = res.get("final_accuracy", 0.0) * 100
        loss = res.get("final_loss", 0.0)
        src_rec = res.get("final_source_class_recall", 0.0) * 100
        asr = res.get("final_asr", 0.0) * 100
        mrt = res.get("mrt_s", 0.0)
        total_r = res.get("total_rounds_completed", rounds)

        alerta = ""
        if att in ["targeted_backdoor", "trigger_patch"] and pr > 0:
            if src_rec < 15.0 and asr > 70.0:
                alerta = "  ⚠️ [PONTO CEGO CONFIRMADO: Recall da vítima colapsou e ASR disparou!]"
            elif asr > 50.0:
                alerta = "  ⚠️ [ATAQUE PARCIALMENTE EFETIVO]"
        elif att == "gaussian_noise" and pr > 0:
            if acc < 25.0:
                alerta = "  🛑 [DEFESA COLAPSADA sob Ruído Gaussiano]"
            else:
                alerta = "  🛡️ [DEFESA RESILIENTE ao Ruído Gaussiano]"

        linhas.extend([
            f"[{idx:02d}/{len(cenarios):02d}] Defesa: {strat:<10} | Ataque: {att:<18} | Bizantinos: {pr:4.1f}% | Rodadas: {total_r}",
            f"       • Acurácia Global Final : {acc:5.2f}%",
            f"       • Perda (Loss) Final     : {loss:.4f}",
            f"       • Recall da Vítima (Gato): {src_rec:5.2f}%",
            f"       • Taxa de Sucesso (ASR)  : {asr:5.2f}%",
            f"       • Tempo Médio por Rodada : {mrt:.2f} s/rodada",
        ])
        if alerta:
            linhas.append(f"     {alerta}")
        linhas.append("")

    linhas.extend([
        "-" * 82,
        "4. ESTRUTURA DOS ARQUIVOS EXPORTADOS NESTE PACOTE",
        "-" * 82,
        "  • DIRETRIZES_DO_EXPERIMENTO.txt  : Este arquivo com a memória técnica da sessão.",
        "  • tabela_resumo_estatistico.csv : Tabela analítica completa para importação no Excel/Pandas.",
        "  • tabela_resumo_estatistico.md  : Tabela formatada em Markdown pronta para artigos/relatórios.",
        "  • graficos/                      : Figuras vetoriais e de alta resolução (300 DPI):",
        "      - figura1_ataque_normal_...  : Curvas de acurácia/loss sob ruído gaussiano.",
        "      - figura2_ataque_furtivo_... : O Ponto Cego sob Backdoor (Acurácia vs Recall da vítima).",
        "      - figura3_resumo_barras_...  : Comparativo de barras das 4 defesas sob os dois ataques.",
        "      - figura4_matrizes_...       : Matrizes de confusão comparativas normalizadas.",
        "      - figura5_raiox_classes_...  : Dissecação do desempenho das 10 classes CIFAR-10.",
        "      - figura_customizada_...     : Dashboard 4-em-1 (gerado quando rodado modo customizado).",
        "  • metrics_json/                  : Logs JSON detalhados rodada a rodada de cada cenário.",
        "  • modelos/                       : Checkpoints de pesos PyTorch (.pt) salvos ao final.",
        "=" * 82,
    ])

    texto_final = "\n".join(linhas) + "\n"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto_final)
    print(f"  ✔ Diretrizes da sessão salvas em: {txt_path}")
    return txt_path


# =============================================================================
# CLI E EXECUÇÃO DE BATERIAS
# =============================================================================
def executar_bateria(
    modo: str = "artigo1_completo",
    rounds: int = 10,
    gerar_graficos: bool = True,
    custom_scenario: dict[str, Any] | None = None,
    override_params: dict[str, Any] | None = None,
) -> None:
    """Executa um lote de cenários ou um cenário customizado, acionando a geração de figuras."""
    if modo == "customizado" and custom_scenario:
        cenarios = [custom_scenario]
    elif modo == "artigo1_furtivo":
        cenarios = [dict(c) for c in CENARIOS_ARTIGO1_FURTIVO]
    elif modo == "artigo1_bruto":
        cenarios = [dict(c) for c in CENARIOS_ARTIGO1_BRUTO]
    elif modo == "teste_rapido":
        cenarios = [dict(c) for c in CENARIOS_TESTE_RAPIDO]
    else:  # artigo1_completo
        cenarios = [dict(c) for c in CENARIOS_ARTIGO1]

    # Aplica overrides aos cenários selecionados
    if override_params:
        for c in cenarios:
            for k, v in override_params.items():
                if v is not None:
                    # Preserva envenenamento 0.0 para o Baseline em lotes do artigo
                    if k == "poison_rate" and c.get("poison_rate") == 0.0 and modo != "customizado":
                        continue
                    c[k] = v

    print("=" * 80)
    print(f"  🚀 EXECUÇÃO DE EXPERIMENTOS ({len(cenarios)} cenário(s) | Modo: {modo})")
    print(f"  Resultados: {RESULTS_DIR}")
    print("=" * 80)

    resultados_sessao = []
    for i, cenario in enumerate(cenarios, 1):
        print(f"\n[{i:02d}/{len(cenarios)}] Iniciando cenário...")
        num_rounds = cenario.get("num_rounds", rounds)
        cenario_limpo = {k: v for k, v in cenario.items() if k != "num_rounds"}
        summary = simular_cenario(**cenario_limpo, num_rounds=num_rounds)
        resultados_sessao.append(summary)

    print("\n" + "═" * 80)
    print("  ✔ TODAS AS SIMULAÇÕES FORAM CONCLUÍDAS COM SUCESSO!")

    # Gera o arquivo TXT de diretrizes e configurações estruturadas
    _gerar_relatorio_diretrizes_txt(
        results_dir=RESULTS_DIR,
        modo=modo,
        rounds=rounds,
        cenarios=cenarios,
        resultados=resultados_sessao,
        overrides=override_params,
    )

    if gerar_graficos:
        print("  Gerando figuras científicas, matrizes de confusão e tabela resumo...")
        print("═" * 80 + "\n")
        import plotar_resultados
        plotar_resultados.main(target_rounds=rounds, modo_executado=modo, custom_scenario=custom_scenario)
    else:
        print("═" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executor Modular e Parametrizável de Baterias de Segurança Federada."
    )
    parser.add_argument(
        "--modo",
        type=str,
        default="artigo1_completo",
        choices=["artigo1_completo", "artigo1_furtivo", "artigo1_bruto", "teste_rapido", "customizado"],
        help="Modo de execução da bateria experimental",
    )
    parser.add_argument("--rounds", type=int, default=10, help="Número de rodadas por simulação")
    parser.add_argument("--defesa", type=str, default=None, choices=["FedAvg", "FedMedian", "Krum", "Bulyan"],
                        help="Defesa para cenário customizado")
    parser.add_argument("--ataque", type=str, default=None,
                        choices=["targeted_backdoor", "gaussian_noise", "label_flipping", "trigger_patch"],
                        help="Ataque para cenário customizado")
    parser.add_argument("--poison_rate", type=float, default=None, help="Fração de nós maliciosos (ex: 0.4)")
    parser.add_argument("--alpha", type=float, default=None, help="Parâmetro Dirichlet de assimetria não-IID (ex: 0.1)")
    parser.add_argument("--seed", type=int, default=None, help="Seed aleatória para reprodutibilidade")
    parser.add_argument("--clients", type=int, default=None, help="Número total de clientes na federação")
    parser.add_argument("--batch_size", type=int, default=None, help="Tamanho do lote de treino local")
    parser.add_argument("--lr", type=float, default=None, help="Taxa de aprendizado local")
    parser.add_argument("--epochs", type=int, default=None, help="Número de épocas locais de treino por rodada")
    parser.add_argument("--sem_graficos", action="store_true", help="Pula a geração automática de gráficos ao final")

    args = parser.parse_args()

    override_params = {}
    if args.alpha is not None:
        override_params["dirichlet_alpha"] = args.alpha
    if args.seed is not None:
        override_params["seed"] = args.seed
    if args.clients is not None:
        override_params["num_clients"] = args.clients
    if args.batch_size is not None:
        override_params["batch_size"] = args.batch_size
    if args.lr is not None:
        override_params["learning_rate"] = args.lr
    if args.epochs is not None:
        override_params["local_epochs"] = args.epochs
    if args.poison_rate is not None:
        override_params["poison_rate"] = args.poison_rate

    # Se modo customizado ou se foi especificada uma defesa ou ataque individual
    custom_scenario = None
    modo = args.modo
    if args.modo == "customizado" or (args.defesa is not None and args.ataque is not None):
        modo = "customizado"
        custom_scenario = {
            "strategy_name": args.defesa or "FedAvg",
            "attack_type": args.ataque or "targeted_backdoor",
            "poison_rate": args.poison_rate if args.poison_rate is not None else 0.4,
            "dirichlet_alpha": args.alpha if args.alpha is not None else 0.1,
            "seed": args.seed if args.seed is not None else 42,
            "num_clients": args.clients if args.clients is not None else 10,
            "batch_size": args.batch_size if args.batch_size is not None else 64,
            "learning_rate": args.lr if args.lr is not None else 0.01,
            "local_epochs": args.epochs if args.epochs is not None else 2,
            "num_rounds": args.rounds,
        }

    executar_bateria(
        modo=modo,
        rounds=args.rounds,
        gerar_graficos=not args.sem_graficos,
        custom_scenario=custom_scenario,
        override_params=override_params,
    )


if __name__ == "__main__":
    main()

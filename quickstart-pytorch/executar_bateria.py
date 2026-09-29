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

# Sub-blocos temáticos do Artigo 1 para execução seletiva
CENARIOS_ARTIGO1_FURTIVO: list[dict[str, Any]] = [
    c for c in CENARIOS_ARTIGO1 if c["attack_type"] == "targeted_backdoor"
]

CENARIOS_ARTIGO1_BRUTO: list[dict[str, Any]] = [
    c for c in CENARIOS_ARTIGO1 if c["attack_type"] == "gaussian_noise"
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


# =============================================================================
# CLI E EXECUÇÃO DE BATERIAS
# =============================================================================
def executar_bateria(
    modo: str = "artigo1_completo",
    rounds: int = 10,
    gerar_graficos: bool = True,
    custom_scenario: dict[str, Any] | None = None,
) -> None:
    """Executa um lote de cenários ou um cenário customizado, acionando a geração de figuras."""
    if modo == "customizado" and custom_scenario:
        cenarios = [custom_scenario]
    elif modo == "artigo1_furtivo":
        cenarios = CENARIOS_ARTIGO1_FURTIVO
    elif modo == "artigo1_bruto":
        cenarios = CENARIOS_ARTIGO1_BRUTO
    elif modo == "teste_rapido":
        cenarios = CENARIOS_TESTE_RAPIDO
    else:  # artigo1_completo
        cenarios = CENARIOS_ARTIGO1

    print("=" * 80)
    print(f"  🚀 EXECUÇÃO DE EXPERIMENTOS ({len(cenarios)} cenário(s) | Modo: {modo})")
    print(f"  Resultados: {RESULTS_DIR}")
    print("=" * 80)

    for i, cenario in enumerate(cenarios, 1):
        print(f"\n[{i:02d}/{len(cenarios)}] Iniciando cenário...")
        # num_rounds do cenario tem precedência se já estiver nele, senão usa rounds
        num_rounds = cenario.get("num_rounds", rounds)
        cenario_limpo = {k: v for k, v in cenario.items() if k != "num_rounds"}
        simular_cenario(**cenario_limpo, num_rounds=num_rounds)

    print("\n" + "═" * 80)
    print("  ✔ TODAS AS SIMULAÇÕES FORAM CONCLUÍDAS COM SUCESSO!")
    if gerar_graficos:
        print("  Gerando figuras científicas, matrizes de confusão e tabela resumo...")
        print("═" * 80 + "\n")
        import plotar_resultados
        plotar_resultados.main()
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
    parser.add_argument("--poison_rate", type=float, default=0.4, help="Fração de nós maliciosos (ex: 0.4)")
    parser.add_argument("--alpha", type=float, default=0.1, help="Parâmetro Dirichlet de assimetria não-IID (ex: 0.1)")
    parser.add_argument("--seed", type=int, default=42, help="Seed aleatória para reprodutibilidade")
    parser.add_argument("--clients", type=int, default=10, help="Número total de clientes na federação")
    parser.add_argument("--batch_size", type=int, default=64, help="Tamanho do lote de treino local")
    parser.add_argument("--lr", type=float, default=0.01, help="Taxa de aprendizado local")
    parser.add_argument("--epochs", type=int, default=2, help="Número de épocas locais de treino por rodada")
    parser.add_argument("--sem_graficos", action="store_true", help="Pula a geração automática de gráficos ao final")

    args = parser.parse_args()

    # Se parâmetros específicos de cenário forem fornecidos, ativa modo customizado
    custom_scenario = None
    modo = args.modo
    if args.defesa is not None or args.ataque is not None or args.modo == "customizado":
        modo = "customizado"
        custom_scenario = {
            "strategy_name": args.defesa or "Bulyan",
            "attack_type": args.ataque or "targeted_backdoor",
            "poison_rate": args.poison_rate,
            "dirichlet_alpha": args.alpha,
            "seed": args.seed,
            "num_clients": args.clients,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "local_epochs": args.epochs,
            "num_rounds": args.rounds,
        }

    executar_bateria(
        modo=modo,
        rounds=args.rounds,
        gerar_graficos=not args.sem_graficos,
        custom_scenario=custom_scenario,
    )


if __name__ == "__main__":
    main()

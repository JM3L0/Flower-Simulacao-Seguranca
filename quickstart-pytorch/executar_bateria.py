"""
executar_bateria.py — Executor Direto e Robusto de Simulações Federadas.

Executa as simulações em GPU/CPU diretamente pelo Python, garantindo:
1. Logs limpos e em tempo real no console rodada a rodada.
2. Salvamento determinístico de métricas JSON na pasta resultados_ataque_furtivo/metrics_json/.
3. Suporte a qualquer combinação de Defesa, Ataque, Heterogeneidade e Seeds.
4. Geração automática das figuras científicas e painel resumo no final.

Uso:
    python executar_bateria.py
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# Garante UTF-8 limpo no terminal Windows e Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


import torch

# Define diretórios absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "resultados_ataque_furtivo")
METRICS_DIR = os.path.join(RESULTS_DIR, "metrics_json")
MODELS_DIR = os.path.join(RESULTS_DIR, "modelos")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Garante que o pacote pytorchexample seja importável
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pytorchexample.task import Net, load_centralized_dataset, load_data, test, train_with_attack



def simular_cenario(
    strategy_name: str = "FedAvg",
    attack_type: str = "targeted_backdoor",
    poison_rate: float = 0.4,
    dirichlet_alpha: float = 0.1,
    num_rounds: int = 10,
    seed: int = 42,
    num_clients: int = 10,
    batch_size: int = 64,
    learning_rate: float = 0.1,
    device_str: str = None
) -> dict:
    """Executa um cenário completo de Aprendizado Federado de forma direta e transparente."""
    if device_str is None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    print("\n" + "═" * 78)
    print(f"  EXECUTANDO SIMULAÇÃO: {strategy_name.upper()}")
    print("═" * 78)
    print(f"  • Defesa:                {strategy_name}")
    print(f"  • Ataque:                {attack_type} (Poison Rate: {poison_rate*100:.0f}%)")
    print(f"  • Heterogeneidade (α):   {dirichlet_alpha} ({'Non-IID Extremo' if dirichlet_alpha <= 0.1 else 'IID/Suave'})")
    print(f"  • Semente (Seed):        {seed}")
    print(f"  • Rodadas Globais:       {num_rounds}")
    print(f"  • Dispositivo (Device):  {device}")
    print("─" * 78)

    # Carrega dados de teste centralizados para auditoria
    test_loader = load_centralized_dataset()

    # Inicializa modelo global
    global_model = Net().to(device)

    # Carrega datasets locais dos clientes
    client_loaders = []
    for cid in range(num_clients):
        train_loader, _ = load_data(
            partition_id=cid,
            num_partitions=num_clients,
            batch_size=batch_size,
            dirichlet_alpha=dirichlet_alpha,
            seed=seed
        )

        client_loaders.append(train_loader)

    # Identifica nós atacantes
    attackers = set()
    num_attackers = int(num_clients * poison_rate)
    for cid in range(num_attackers):
        attackers.add(cid)

    round_records = []
    round_timings = []

    for r in range(1, num_rounds + 1):
        t0 = time.perf_counter()

        # 1. Clientes treinam localmente a partir dos pesos globais
        client_updates = []
        client_weights = []

        global_state = global_model.state_dict()

        for cid in range(num_clients):
            # Cria cópia do modelo para o cliente
            local_model = Net().to(device)
            local_model.load_state_dict({k: v.clone() for k, v in global_state.items()})

            is_malicious = (cid in attackers)
            loader = client_loaders[cid]

            # Treina com ataque se for atacante
            train_loss, num_poisoned = train_with_attack(
                net=local_model,
                trainloader=loader,
                epochs=1,
                lr=learning_rate,
                device=device,
                poison_rate=1.0 if is_malicious else 0.0,
                attack_type=attack_type
            )


            # Extrai os pesos atualizados
            updated_state = {k: v.cpu().clone() for k, v in local_model.state_dict().items()}
            client_updates.append(updated_state)
            client_weights.append(len(loader.dataset))

        # 2. Agregação pelo Servidor com a Defesa Selecionada
        total_samples = sum(client_weights)
        new_state = {}

        if strategy_name == "FedAvg":
            for key in global_state.keys():
                stacked = torch.stack([u[key].float() for u in client_updates])
                weights_tensor = torch.tensor(client_weights, dtype=torch.float32)
                weights_tensor = weights_tensor / weights_tensor.sum()
                # Weighted average
                for _ in range(stacked.dim() - 1):
                    weights_tensor = weights_tensor.unsqueeze(-1)
                new_state[key] = (stacked * weights_tensor).sum(dim=0).to(global_state[key].dtype)

        elif strategy_name == "FedMedian":
            for key in global_state.keys():
                stacked = torch.stack([u[key].float() for u in client_updates])
                median_val, _ = torch.median(stacked, dim=0)
                new_state[key] = median_val.to(global_state[key].dtype)

        elif strategy_name in ["Krum", "Bulyan"]:
            # Flatten dos vetores de parâmetros para cálculo de distâncias euclidianas
            client_vectors = []
            for u in client_updates:
                flat = torch.cat([v.flatten().float() for v in u.values()])
                client_vectors.append(flat)
            stacked_vectors = torch.stack(client_vectors)

            # Matriz de distâncias
            n = len(client_vectors)
            f = num_attackers if num_attackers > 0 else 1
            f = min(f, (n - 3) // 2) if n > 3 else 0
            
            distances = torch.cdist(stacked_vectors, stacked_vectors)
            scores = []
            for i in range(n):
                sorted_dists, _ = torch.sort(distances[i])
                # Soma das n - f - 2 menores distâncias
                k = max(1, n - f - 2)
                score = sorted_dists[1:k+1].sum().item()
                scores.append(score)

            if strategy_name == "Krum":
                best_idx = int(torch.argmin(torch.tensor(scores)))
                new_state = {k: client_updates[best_idx][k].to(device) for k in global_state.keys()}
            else: # Bulyan
                sorted_indices = torch.argsort(torch.tensor(scores))
                # Seleciona os theta melhores candidatos
                theta = max(1, n - 2 * f)
                selected_cands = [client_updates[idx] for idx in sorted_indices[:theta]]
                # Para cada coordenada, remove os extremos e calcula a média
                for key in global_state.keys():
                    cand_stacked = torch.stack([c[key].float() for c in selected_cands])
                    # Média aparada (Trimmed Mean)
                    sorted_vals, _ = torch.sort(cand_stacked, dim=0)
                    beta = max(0, f)
                    if cand_stacked.shape[0] > 2 * beta and beta > 0:
                        trimmed = sorted_vals[beta:-beta]
                    else:
                        trimmed = sorted_vals
                    new_state[key] = trimmed.mean(dim=0).to(global_state[key].dtype)
        else:
            # Fallback FedAvg
            for key in global_state.keys():
                stacked = torch.stack([u[key].float() for u in client_updates])
                new_state[key] = stacked.mean(dim=0).to(global_state[key].dtype)

        # Atualiza modelo global
        global_model.load_state_dict({k: v.to(device) for k, v in new_state.items()})

        # 3. Auditoria Centralizada na Rodada
        test_loss, test_acc, audit_info = test(
            global_model,
            test_loader,
            device,
            compute_audit=True,
            attack_type=attack_type
        )

        t1 = time.perf_counter()
        dt = t1 - t0
        round_timings.append(dt)

        src_name = audit_info["source_class_name"]
        src_rec = audit_info["source_class_recall"] * 100
        asr_val = audit_info["asr"] * 100

        round_data = {
            "round": r,
            "accuracy": test_acc,
            "loss": test_loss,
            "source_class_name": src_name,
            "source_class_recall": audit_info["source_class_recall"],
            "target_class_name": audit_info["target_class_name"],
            "target_class_recall": audit_info["target_class_recall"],
            "asr": audit_info["asr"],
            "per_class_accuracy": audit_info["per_class_accuracy"],
            "confusion_matrix": audit_info["confusion_matrix"],
            "round_time_s": dt,
        }
        round_records.append(round_data)

        # Log em tempo real formatado
        ponto_cego_str = " 🚨 (Ponto Cego!)" if src_rec < 15.0 and attack_type in ["targeted_backdoor", "trigger_patch"] else ""
        print(
            f"  [Rodada {r:02d}/{num_rounds:02d}] "
            f"Acc Global: {test_acc*100:5.2f}% | "
            f"Recall {src_name}: {src_rec:5.2f}% | "
            f"ASR: {asr_val:5.2f}% | "
            f"Loss: {test_loss:6.4f} | "
            f"Tempo: {dt:4.1f}s{ponto_cego_str}"
        )

    # 4. Salva Métricas em JSON estruturado
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = (
        f"metrics_{strategy_name}_{attack_type}_pr{poison_rate}_da{dirichlet_alpha}_s{seed}_{timestamp_str}.json"
    )
    summary_path = os.path.join(METRICS_DIR, summary_filename)

    final_rec = round_records[-1]
    summary = {
        "experiment_config": {
            "strategy": strategy_name,
            "attack_type": attack_type,
            "num_server_rounds": num_rounds,
            "poison_rate": poison_rate,
            "dirichlet_alpha": dirichlet_alpha,
            "seed": seed,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "timestamp": datetime.now().isoformat(),
        },
        "rounds": round_records,
        "final_accuracy": final_rec["accuracy"],
        "final_loss": final_rec["loss"],
        "final_asr": final_rec["asr"],
        "final_source_class_recall": final_rec["source_class_recall"],
        "final_target_class_recall": final_rec["target_class_recall"],
        "final_per_class_accuracy": final_rec["per_class_accuracy"],
        "final_confusion_matrix": final_rec["confusion_matrix"],
        "total_rounds_completed": num_rounds,
        "mrt_s": sum(round_timings) / len(round_timings) if round_timings else 0.0,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"  ✔ Métricas salvas: {summary_path}")

    # Salva checkpoint do modelo treinado
    model_filename = f"model_{strategy_name}_{attack_type}_pr{poison_rate}_da{dirichlet_alpha}_{timestamp_str}.pt"
    model_path = os.path.join(MODELS_DIR, model_filename)
    torch.save(global_model.state_dict(), model_path)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Executor de Baterias Experimentais de Segurança Federada.")
    parser.add_argument("--modo", type=str, default="artigo1_completo", choices=["artigo1_completo", "teste_rapido", "custom"],
                        help="Modo de execução da bateria")
    parser.add_argument("--rounds", type=int, default=10, help="Número de rodadas por simulação")
    args = parser.parse_args()

    print("=" * 80)
    print("  🚀 INICIANDO BATERIA EXPERIMENTAL (MOTOR FEDERADO PYTORCH)")
    print("=" * 80)
    print(f"  Modo Selecionado:       {args.modo}")
    print(f"  Diretório de Resultados:{RESULTS_DIR}")
    print("=" * 80)

    if args.modo == "teste_rapido":
        cenarios = [
            {"defesa": "FedAvg", "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": 3, "seed": 42},
            {"defesa": "Bulyan", "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": 3, "seed": 42},
        ]
    else:
        # Bateria Comparativa Completa do Artigo 1
        cenarios = [
            # 1. Baseline Limpo de Controle (Sem Ataque)
            {"defesa": "FedAvg", "ataque": "label_flipping", "pr": 0.0, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            
            # 2. Ataques Brutos de Controle (Ruído Gaussiano)
            {"defesa": "FedAvg", "ataque": "gaussian_noise",  "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            {"defesa": "Bulyan", "ataque": "gaussian_noise",  "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            
            # 3. Ataques Furtivos: Targeted Backdoor (As 4 Defesas sob alpha=0.1)
            {"defesa": "FedAvg",    "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            {"defesa": "FedMedian", "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            {"defesa": "Krum",      "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            {"defesa": "Bulyan",    "ataque": "targeted_backdoor", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            
            # 4. Ataque Furtivo: Trigger Patch Físico
            {"defesa": "FedAvg", "ataque": "trigger_patch", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
            {"defesa": "Bulyan", "ataque": "trigger_patch", "pr": 0.4, "alpha": 0.1, "rounds": args.rounds, "seed": 42},
        ]

    total = len(cenarios)
    for i, c in enumerate(cenarios, 1):
        print(f"\n[{i:02d}/{total}] Iniciando bateria...")
        simular_cenario(
            strategy_name=c["defesa"],
            attack_type=c["ataque"],
            poison_rate=c["pr"],
            dirichlet_alpha=c["alpha"],
            num_rounds=c["rounds"],
            seed=c["seed"]
        )

    print("\n" + "═" * 80)
    print("  ✔ TODAS AS SIMULAÇÕES FORAM CONCLUÍDAS COM SUCESSO!")
    print("  Gerando figuras científicas, matrizes de confusão e tabela resumo...")
    print("═" * 80 + "\n")

    # Chama o agregador estatístico e gerador de figuras
    import plotar_resultados
    plotar_resultados.main()


if __name__ == "__main__":
    main()

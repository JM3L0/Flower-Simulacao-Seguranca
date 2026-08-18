"""pytorchexample: A Flower / PyTorch app — Security Experimentation Server."""

import json
import os
import time
from datetime import datetime

import torch
from flwr.app import ArrayRecord, ConfigRecord, Context, MetricRecord
from flwr.serverapp import Grid, ServerApp
from flwr.serverapp.strategy import Bulyan, FedAvg, FedMedian, Krum

from pytorchexample.task import Net, load_centralized_dataset, test

# Create ServerApp
app = ServerApp()

# =============================================================================
# DIRETÓRIOS PARA ORGANIZAÇÃO DOS RESULTADOS DE ATAQUES FURTIVOS
# =============================================================================
BASE_RESULTS_DIR = "resultados_ataque_furtivo"
METRICS_DIR = os.path.join(BASE_RESULTS_DIR, "metrics_json")
MODELS_DIR = os.path.join(BASE_RESULTS_DIR, "modelos")

# Estado global temporário para auditoria por rodada
_current_attack_type = "targeted_backdoor"
_audit_records_per_round = {}


@app.main()
def main(grid: Grid, context: Context) -> None:
    """Main entry point for the ServerApp."""
    global _current_attack_type, _audit_records_per_round
    _audit_records_per_round.clear()

    # Read run config
    fraction_evaluate: float = context.run_config["fraction-evaluate"]
    num_rounds: int = context.run_config["num-server-rounds"]
    lr: float = context.run_config["learning-rate"]
    poison_rate: float = context.run_config["poison_rate"]
    dirichlet_alpha: float = context.run_config["dirichlet_alpha"]
    modo_defesa: str = context.run_config["defense_mode"]
    attack_type: str = context.run_config.get("attack_type", "targeted_backdoor")
    seed: int = context.run_config.get("seed", 42)
    _current_attack_type = attack_type

    print("=" * 75)
    print("  ESTUDO EMPÍRICO DE SEGURANÇA FEDERADA (FLOWER + PYTORCH)")
    print("=" * 75)
    print(f"  Estratégia de Defesa:      {modo_defesa}")
    print(f"  Tipo de Ataque:            {attack_type}")
    print(f"  Taxa de Envenenamento:     {poison_rate} ({int(poison_rate*100)}% nós/dados)")
    print(f"  Dirichlet Alpha (Non-IID): {dirichlet_alpha}")
    print(f"  Semente Aleatória (Seed):  {seed}")
    print(f"  Rodadas Globais:           {num_rounds}")
    print(f"  Learning Rate:             {lr}")
    print(f"  Diretório de Saída:        {BASE_RESULTS_DIR}/")
    print("=" * 75)


    # Criação das pastas organizadas
    os.makedirs(METRICS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Load global model
    global_model = Net()
    arrays = ArrayRecord(global_model.state_dict())

    # =========================================================================
    # SELEÇÃO DINÂMICA DA ESTRATÉGIA DE DEFESA CONVENCIONAL
    # =========================================================================
    if modo_defesa == "FedMedian":
        strategy = FedMedian(fraction_evaluate=fraction_evaluate)
        print("[Defesa] Estratégia FedMedian instanciada.")
    elif modo_defesa == "Bulyan":
        strategy = Bulyan(fraction_evaluate=fraction_evaluate)
        print("[Defesa] Estratégia Bulyan instanciada.")
    elif modo_defesa == "FedAvg":
        strategy = FedAvg(fraction_evaluate=fraction_evaluate)
        print("[Defesa] Estratégia FedAvg (baseline) instanciada.")
    elif modo_defesa == "Krum":
        strategy = Krum(fraction_evaluate=fraction_evaluate, num_malicious_nodes=1)
        print("[Defesa] Estratégia Krum instanciada.")
    else:
        print(f"[AVISO] Estratégia '{modo_defesa}' não reconhecida. Usando FedAvg.")
        strategy = FedAvg(fraction_evaluate=fraction_evaluate)
        modo_defesa = "FedAvg"

    # Track round timing (MRT)
    round_timings: dict[int, float] = {}
    prev_round_end = time.perf_counter()

    def evaluate_with_timing(server_round: int, arrays: ArrayRecord) -> MetricRecord:
        nonlocal prev_round_end
        metrics = global_evaluate(server_round, arrays)
        now = time.perf_counter()
        round_timings[server_round] = now - prev_round_end
        prev_round_end = now
        return metrics

    # Start strategy for `num_rounds`
    result = strategy.start(
        grid=grid,
        initial_arrays=arrays,
        train_config=ConfigRecord({"lr": lr}),
        num_rounds=num_rounds,
        evaluate_fn=evaluate_with_timing,
    )

    # =========================================================================
    # EXPORTAÇÃO ESTRUTURADA DE MÉTRICAS E AUDITORIA EM JSON
    # =========================================================================
    experiment_config = {
        "strategy": modo_defesa,
        "attack_type": attack_type,
        "num_server_rounds": num_rounds,
        "poison_rate": poison_rate,
        "dirichlet_alpha": dirichlet_alpha,
        "seed": seed,
        "learning_rate": lr,
        "fraction_evaluate": fraction_evaluate,
        "timestamp": datetime.now().isoformat(),
    }

    all_rounds_data = []
    final_conf_matrix = None
    final_per_class_acc = {}
    final_asr = 0.0
    final_source_recall = 0.0
    final_target_recall = 0.0

    for round_num in sorted(_audit_records_per_round.keys()):
        round_audit = _audit_records_per_round[round_num]
        all_rounds_data.append({
            "round": round_num,
            "accuracy": round_audit.get("accuracy"),
            "loss": round_audit.get("loss"),
            "source_class_recall": round_audit.get("source_class_recall"),
            "target_class_recall": round_audit.get("target_class_recall"),
            "asr": round_audit.get("asr"),
            "per_class_accuracy": round_audit.get("per_class_accuracy"),
            "round_time_s": round_timings.get(round_num),
        })
        final_conf_matrix = round_audit.get("confusion_matrix")
        final_per_class_acc = round_audit.get("per_class_accuracy", {})
        final_asr = round_audit.get("asr", 0.0)
        final_source_recall = round_audit.get("source_class_recall", 0.0)
        final_target_recall = round_audit.get("target_class_recall", 0.0)

    final_round = max(_audit_records_per_round.keys()) if _audit_records_per_round else 0
    final_metrics = _audit_records_per_round.get(final_round, {})

    mrt_s = (
        sum(round_timings.values()) / len(round_timings)
        if round_timings
        else None
    )

    summary = {
        "experiment_config": experiment_config,
        "rounds": all_rounds_data,
        "final_accuracy": final_metrics.get("accuracy"),
        "final_loss": final_metrics.get("loss"),
        "final_asr": final_asr,
        "final_source_class_recall": final_source_recall,
        "final_target_class_recall": final_target_recall,
        "final_per_class_accuracy": final_per_class_acc,
        "final_confusion_matrix": final_conf_matrix,
        "total_rounds_completed": len(all_rounds_data),
        "mrt_s": mrt_s,
    }

    # Salva o arquivo JSON com nome padronizado e descritivo
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = (
        f"metrics_{modo_defesa}_{attack_type}_pr{poison_rate}_da{dirichlet_alpha}_s{seed}_{timestamp_str}.json"
    )

    summary_file = os.path.join(METRICS_DIR, summary_filename)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Exibe o resumo final
    print("\n" + "=" * 75)
    print(f"  RESUMO CONSOLIDADO DO EXPERIMENTO")
    print("=" * 75)
    print(f"  Defesa Avaliada:          {modo_defesa}")
    print(f"  Ataque Furtivo:           {attack_type}")
    print(f"  Acurácia Global Final:    {summary['final_accuracy']*100:.2f}% (Visão Agregada)")
    print(f"  Recall da Classe Vítima:  {final_source_recall*100:.2f}% (Ponto Cego Real)")
    print(f"  Taxa Sucesso Ataque (ASR):{final_asr*100:.2f}%")
    print(f"  Perda Final (Loss):       {summary['final_loss']:.4f}")
    print(f"  MRT (Tempo/Rodada):       {summary['mrt_s']:.2f} s")
    print(f"  Arquivo de Métricas:      {summary_file}")
    print("=" * 75)

    # Salva modelo final
    model_filename = f"model_{modo_defesa}_{attack_type}_pr{poison_rate}_da{dirichlet_alpha}_{timestamp_str}.pt"
    model_path = os.path.join(MODELS_DIR, model_filename)
    state_dict = result.arrays.to_torch_state_dict()
    torch.save(state_dict, model_path)
    torch.save(state_dict, "final_model.pt")
    print(f"Modelo final salvo em: {model_path}\n")


def global_evaluate(server_round: int, arrays: ArrayRecord) -> MetricRecord:
    """Evaluate model on central data with granular class inspection."""
    global _current_attack_type, _audit_records_per_round

    # Load the model and initialize it with the received weights
    model = Net()
    model.load_state_dict(arrays.to_torch_state_dict())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Load entire test set
    test_dataloader = load_centralized_dataset()

    # Evaluate with full audit metrics
    test_loss, test_acc, audit_info = test(
        model,
        test_dataloader,
        device,
        compute_audit=True,
        attack_type=_current_attack_type,
    )

    # Guarda o snapshot de auditoria da rodada
    _audit_records_per_round[server_round] = {
        "round": server_round,
        "accuracy": test_acc,
        "loss": test_loss,
        "source_class_name": audit_info["source_class_name"],
        "source_class_recall": audit_info["source_class_recall"],
        "target_class_name": audit_info["target_class_name"],
        "target_class_recall": audit_info["target_class_recall"],
        "asr": audit_info["asr"],
        "per_class_accuracy": audit_info["per_class_accuracy"],
        "confusion_matrix": audit_info["confusion_matrix"],
    }

    src_name = audit_info["source_class_name"]
    src_rec = audit_info["source_class_recall"] * 100
    asr_val = audit_info["asr"] * 100

    print(
        f"[Diagnóstico Global] Rodada {server_round:02d} | "
        f"Acc Global: {test_acc*100:5.2f}% | "
        f"Recall Vítima ({src_name}): {src_rec:5.2f}% | "
        f"ASR: {asr_val:5.2f}% | "
        f"Loss: {test_loss:.4f}"
    )

    # Return the evaluation metrics to Flower engine
    return MetricRecord({"accuracy": test_acc, "loss": test_loss})

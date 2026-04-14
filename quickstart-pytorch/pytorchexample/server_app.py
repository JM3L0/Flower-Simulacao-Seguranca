"""pytorchexample: A Flower / PyTorch app — Security Experimentation Server."""

import json
import os
from datetime import datetime

import torch
from flwr.app import ArrayRecord, ConfigRecord, Context, MetricRecord
from flwr.serverapp import Grid, ServerApp
from flwr.serverapp.strategy import Bulyan, FedAvg, FedMedian

from pytorchexample.task import Net, load_centralized_dataset, test

# Create ServerApp
app = ServerApp()

# =============================================================================
# DIRETÓRIO PARA EXPORTAÇÃO DE MÉTRICAS JSON
# =============================================================================
METRICS_DIR = "metrics_json"


@app.main()
def main(grid: Grid, context: Context) -> None:
    """Main entry point for the ServerApp."""

    # Read run config
    fraction_evaluate: float = context.run_config["fraction-evaluate"]
    num_rounds: int = context.run_config["num-server-rounds"]
    lr: float = context.run_config["learning-rate"]
    poison_rate: float = context.run_config["poison_rate"]
    dirichlet_alpha: float = context.run_config["dirichlet_alpha"]
    modo_defesa: str = context.run_config["defense_mode"]

    print("=" * 70)
    print("  AMBIENTE DE EXPERIMENTAÇÃO EM SEGURANÇA FEDERADA")
    print("=" * 70)
    print(f"  Estratégia:       {modo_defesa}")
    print(f"  Rodadas:          {num_rounds}")
    print(f"  Taxa de Ataque:   {poison_rate}")
    print(f"  Dirichlet Alpha:  {dirichlet_alpha}")
    print(f"  Learning Rate:    {lr}")
    print("=" * 70)

    # Create metrics output directory
    os.makedirs(METRICS_DIR, exist_ok=True)

    # Load global model
    global_model = Net()
    arrays = ArrayRecord(global_model.state_dict())

    # =========================================================================
    # SELEÇÃO DINÂMICA DA ESTRATÉGIA DE DEFESA
    #
    # Controle via terminal:
    #   flwr run . --run-config "defense_mode=FedMedian"
    #   flwr run . --run-config "defense_mode=Bulyan"
    #   flwr run . --run-config "defense_mode=FedAvg"
    #
    # FedAvg   — Baseline sem defesa robusta (média simples dos pesos)
    # FedMedian — Agregação via mediana coordenada-a-coordenada (robusto)
    # Bulyan   — Defesa bizantina avançada (filtra outliers + média trimmed)
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
    else:
        print(f"[AVISO] Estratégia '{modo_defesa}' não reconhecida. Usando FedAvg.")
        strategy = FedAvg(fraction_evaluate=fraction_evaluate)
        modo_defesa = "FedAvg"

    # Start strategy for `num_rounds`
    result = strategy.start(
        grid=grid,
        initial_arrays=arrays,
        train_config=ConfigRecord({"lr": lr}),
        num_rounds=num_rounds,
        evaluate_fn=global_evaluate,
    )

    # =========================================================================
    # EXPORTAÇÃO DE MÉTRICAS — metrics_summary.json
    # =========================================================================
    experiment_config = {
        "strategy": modo_defesa,
        "num_server_rounds": num_rounds,
        "poison_rate": poison_rate,
        "dirichlet_alpha": dirichlet_alpha,
        "learning_rate": lr,
        "fraction_evaluate": fraction_evaluate,
        "timestamp": datetime.now().isoformat(),
    }

    all_rounds_data = []
    for round_num, metrics in result.evaluate_metrics_serverapp.items():
        all_rounds_data.append({
            "round": round_num,
            "accuracy": metrics.get("accuracy", None),
            "loss": metrics.get("loss", None),
        })

    final_round = max(result.evaluate_metrics_serverapp.keys()) if result.evaluate_metrics_serverapp else 0
    final_metrics = result.evaluate_metrics_serverapp.get(final_round, {})

    summary = {
        "experiment_config": experiment_config,
        "rounds": all_rounds_data,
        "final_accuracy": final_metrics.get("accuracy", None),
        "final_loss": final_metrics.get("loss", None),
        "total_rounds_completed": len(all_rounds_data),
    }

    summary_file = os.path.join(METRICS_DIR, "metrics_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"  RESUMO DO EXPERIMENTO")
    print(f"  Estratégia:      {modo_defesa}")
    print(f"  Acurácia Final:  {summary['final_accuracy']}")
    print(f"  Perda Final:     {summary['final_loss']}")
    print(f"  Métricas salvas: {summary_file}")
    print("=" * 70)

    # Save final model to disk
    print("\nSaving final model to disk...")
    state_dict = result.arrays.to_torch_state_dict()
    torch.save(state_dict, "final_model.pt")


def global_evaluate(server_round: int, arrays: ArrayRecord) -> MetricRecord:
    """Evaluate model on central data."""

    # Load the model and initialize it with the received weights
    model = Net()
    model.load_state_dict(arrays.to_torch_state_dict())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Load entire test set
    test_dataloader = load_centralized_dataset()

    # Evaluate the global model on the test set
    test_loss, test_acc = test(model, test_dataloader, device)

    print(
        f"[Avaliação Global] Rodada {server_round}: "
        f"accuracy={test_acc:.4f}, loss={test_loss:.4f}"
    )

    # Return the evaluation metrics
    return MetricRecord({"accuracy": test_acc, "loss": test_loss})

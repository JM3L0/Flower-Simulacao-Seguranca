"""
plotar_resultados.py — Gerador de Graficos Comparativos para Experimentos de Seguranca Federada.

Le todos os arquivos JSON da pasta metrics_json/ e gera graficos comparativos
de Acuracia e Perda (Loss) por rodada, com uma curva para cada cenario.

Uso:
    python plotar_resultados.py
"""

import json
import os
import glob

import matplotlib.pyplot as plt  # type: ignore


# ============================================================================
# CONFIGURACAO DOS GRAFICOS
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_DIR = os.path.join(SCRIPT_DIR, "metrics_json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "graficos")

# Estilo academico
plt.rcParams.update({
    "figure.figsize": (12, 5),
    "font.family": "serif",
    "font.size": 12,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 2,
    "lines.markersize": 6,
})

MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "<"]
COLORS = [
    "#2196F3",  # azul
    "#F44336",  # vermelho
    "#4CAF50",  # verde
    "#FF9800",  # laranja
    "#9C27B0",  # roxo
    "#00BCD4",  # ciano
    "#795548",  # marrom
    "#607D8B",  # cinza
]


def carregar_experimentos(diretorio: str) -> list[dict]:
    """Carrega todos os JSONs de metricas do diretorio."""
    arquivos = glob.glob(os.path.join(diretorio, "metrics_*.json"))
    experimentos = []

    for arquivo in sorted(arquivos):
        with open(arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Gera um label descritivo para a legenda
        config = data.get("experiment_config", {})
        label = (
            f"{config.get('strategy', '?')} | "
            f"PR={config.get('poison_rate', '?')} | "
            f"DA={config.get('dirichlet_alpha', '?')}"
        )

        experimentos.append({
            "label": label,
            "config": config,
            "rounds": data.get("rounds", []),
            "arquivo": os.path.basename(arquivo),
        })

    return experimentos


def plotar_comparativo(experimentos: list[dict], output_dir: str):
    """Gera graficos comparativos de Acuracia e Loss."""
    if not experimentos:
        print("Nenhum experimento encontrado em metrics_json/")
        return

    os.makedirs(output_dir, exist_ok=True)

    fig, (ax_acc, ax_loss) = plt.subplots(1, 2, figsize=(14, 6))

    for i, exp in enumerate(experimentos):
        rounds = [r["round"] for r in exp["rounds"]]
        accuracies = [r["accuracy"] for r in exp["rounds"]]
        losses = [r["loss"] for r in exp["rounds"]]

        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]

        ax_acc.plot(
            rounds, accuracies,
            color=color, marker=marker, label=exp["label"],
        )
        ax_loss.plot(
            rounds, losses,
            color=color, marker=marker, label=exp["label"],
        )

    # Acuracia
    ax_acc.set_xlabel("Rodada")
    ax_acc.set_ylabel("Acuracia Global")
    ax_acc.set_title("Acuracia por Rodada")
    ax_acc.legend(fontsize=9, loc="best")
    ax_acc.set_ylim(bottom=0)

    # Loss
    ax_loss.set_xlabel("Rodada")
    ax_loss.set_ylabel("Perda (Loss)")
    ax_loss.set_title("Perda por Rodada")
    ax_loss.legend(fontsize=9, loc="best")

    plt.tight_layout()

    output_file = os.path.join(output_dir, "comparativo_cenarios.png")
    fig.savefig(output_file, dpi=200, bbox_inches="tight")
    print(f"Grafico salvo em: {output_file}")
    plt.show()


def main():
    print("=" * 60)
    print("  GERADOR DE GRAFICOS — Seguranca Federada")
    print("=" * 60)

    experimentos = carregar_experimentos(METRICS_DIR)
    print(f"\nExperimentos encontrados: {len(experimentos)}")
    for exp in experimentos:
        print(f"  - {exp['label']}  ({exp['arquivo']})")

    plotar_comparativo(experimentos, OUTPUT_DIR)


if __name__ == "__main__":
    main()

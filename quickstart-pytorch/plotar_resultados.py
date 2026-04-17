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
            f"ATK={config.get('attack_type', '?')} | "
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

    # === GRAFICO DE ACURACIA ===
    fig_acc, ax_acc = plt.subplots(figsize=(10, 6))

    for i, exp in enumerate(experimentos):
        rounds = [r["round"] for r in exp["rounds"]]
        accuracies = [r["accuracy"] for r in exp["rounds"]]

        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]

        ax_acc.plot(
            rounds, accuracies,
            color=color, marker=marker, label=exp["label"],
        )

    ax_acc.set_xlabel("Rodada")
    ax_acc.set_ylabel("Acuracia Global")
    ax_acc.set_title("Comparacao de Acuracia")
    ax_acc.legend(fontsize=9, loc="best")
    ax_acc.set_ylim(bottom=0)

    fig_acc.tight_layout()
    out_acc = os.path.join(output_dir, "comparativo_acuracia.png")
    fig_acc.savefig(out_acc, dpi=200, bbox_inches="tight")
    print(f"Grafico de Acuracia salvo em: {out_acc}")

    # === GRAFICO DE LOSS ===
    fig_loss, ax_loss = plt.subplots(figsize=(10, 6))

    for i, exp in enumerate(experimentos):
        rounds = [r["round"] for r in exp["rounds"]]
        losses = [r["loss"] for r in exp["rounds"]]

        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]

        ax_loss.plot(
            rounds, losses,
            color=color, marker=marker, label=exp["label"],
        )

    ax_loss.set_xlabel("Rodada")
    ax_loss.set_ylabel("Perda (Loss)")
    ax_loss.set_title("Comparacao de Perda (Loss)")
    ax_loss.legend(fontsize=9, loc="best")

    fig_loss.tight_layout()
    out_loss = os.path.join(output_dir, "comparativo_loss.png")
    fig_loss.savefig(out_loss, dpi=200, bbox_inches="tight")
    print(f"Grafico de Loss salvo em:     {out_loss}")

    # === GRAFICO DE TEMPO POR RODADA (MRT) ===
    has_time = any(
        "round_time_s" in r for exp in experimentos for r in exp["rounds"]
    )
    if has_time:
        fig_time, ax_time = plt.subplots(figsize=(10, 6))

        for i, exp in enumerate(experimentos):
            rounds = [r["round"] for r in exp["rounds"]]
            times = [r.get("round_time_s") for r in exp["rounds"]]

            if all(t is None for t in times):
                continue

            color = COLORS[i % len(COLORS)]
            marker = MARKERS[i % len(MARKERS)]

            ax_time.plot(
                rounds, times,
                color=color, marker=marker, label=exp["label"],
            )

        ax_time.set_xlabel("Rodada")
        ax_time.set_ylabel("Tempo por rodada (s)")
        ax_time.set_title("Comparacao de MRT por Rodada")
        ax_time.legend(fontsize=9, loc="best")

        fig_time.tight_layout()
        out_time = os.path.join(output_dir, "comparativo_mrt.png")
        fig_time.savefig(out_time, dpi=200, bbox_inches="tight")
        print(f"Grafico de MRT salvo em:      {out_time}")

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

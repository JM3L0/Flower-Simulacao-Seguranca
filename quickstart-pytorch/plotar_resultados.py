"""
plotar_resultados.py — Gerador de Figuras Científicas e Agregação Estatística (Multi-Trial).

Suporta a execução de N repetições (seeds) por cenário e realiza automaticamente:
1. Agrupamento de experimentos idênticos (multi-trial / multi-seed).
2. Cálculo da Média (μ) e Desvio Padrão (σ) rodada a rodada.
3. Plotagem das curvas médias com Faixas Sombreadas de Desvio Padrão (Shaded Error Bands).
4. Cálculo do Impacto Acumulativo do Ataque (CAI - Cumulative Attack Impact).
5. Geração de Tabela Resumo Estatístico em Markdown e CSV para o Artigo.

Uso:
    python plotar_resultados.py
"""

import glob
import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore

# ============================================================================
# DIRETÓRIOS E CONFIGURAÇÃO
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_RESULTS_DIR = os.path.join(SCRIPT_DIR, "resultados_ataque_furtivo")
METRICS_DIR = os.path.join(BASE_RESULTS_DIR, "metrics_json")
OUTPUT_DIR = os.path.join(BASE_RESULTS_DIR, "graficos")
CM_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "matrizes_confusao")

# Fallback se a pasta nova ainda não tiver JSONs
if not os.path.exists(METRICS_DIR) or len(glob.glob(os.path.join(METRICS_DIR, "*.json"))) == 0:
    FALLBACK_DIR = os.path.join(SCRIPT_DIR, "metrics_json")
    if os.path.exists(FALLBACK_DIR) and len(glob.glob(os.path.join(FALLBACK_DIR, "*.json"))) > 0:
        METRICS_DIR = FALLBACK_DIR

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "lines.linewidth": 2.2,
    "lines.markersize": 5,
})

MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "<"]
COLORS = [
    "#1976D2",  # Azul Royal (FedAvg)
    "#E53935",  # Vermelho Vivo (FedMedian)
    "#43A047",  # Verde Esmeralda (Krum)
    "#8E24AA",  # Roxo Nobre (Bulyan)
    "#FB8C00",  # Laranja
    "#00ACC1",  # Ciano
    "#6D4C41",  # Marrom
    "#546E7A",  # Cinza Ardósia
]

CIFAR10_CLASSES = [
    "Airplane", "Automobile", "Bird", "Cat", "Deer",
    "Dog", "Frog", "Horse", "Ship", "Truck"
]


def carregar_e_agrupar_experimentos(diretorio: str) -> dict:
    """
    Carrega todos os JSONs e agrupa por cenário idêntico:
    (strategy, attack_type, poison_rate, dirichlet_alpha, num_server_rounds).
    """
    arquivos = glob.glob(os.path.join(diretorio, "metrics_*.json"))
    grupos = defaultdict(list)

    for arquivo in sorted(arquivos):
        with open(arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = data.get("experiment_config", {})
        chave_cenario = (
            config.get("strategy", "FedAvg"),
            config.get("attack_type", "targeted_backdoor"),
            float(config.get("poison_rate", 0.0)),
            float(config.get("dirichlet_alpha", 1.0)),
            int(config.get("num_server_rounds", 10)),
        )

        data["_nome_arquivo"] = os.path.basename(arquivo)
        grupos[chave_cenario].append(data)

    return grupos


def consolidar_estatisticas(grupos: dict) -> list[dict]:
    """Calcula Média e Desvio Padrão para cada rodada de cada cenário agrupado."""
    cenarios_consolidados = []

    for chave, trials in grupos.items():
        strategy, attack_type, poison_rate, dirichlet_alpha, num_rounds = chave
        num_trials = len(trials)

        # Encontra o total de rodadas reportadas
        all_rounds = sorted(list({r["round"] for t in trials for r in t.get("rounds", [])}))

        rounds_stats = []
        for r_num in all_rounds:
            accs = [
                r.get("accuracy", 0.0)
                for t in trials
                for r in t.get("rounds", [])
                if r.get("round") == r_num and r.get("accuracy") is not None
            ]
            losses = [
                r.get("loss", 0.0)
                for t in trials
                for r in t.get("rounds", [])
                if r.get("round") == r_num and r.get("loss") is not None
            ]
            src_recs = [
                r.get("source_class_recall", 0.0)
                for t in trials
                for r in t.get("rounds", [])
                if r.get("round") == r_num and r.get("source_class_recall") is not None
            ]
            asrs = [
                r.get("asr", 0.0)
                for t in trials
                for r in t.get("rounds", [])
                if r.get("round") == r_num and r.get("asr") is not None
            ]
            times = [
                r.get("round_time_s", 0.0)
                for t in trials
                for r in t.get("rounds", [])
                if r.get("round") == r_num and r.get("round_time_s") is not None
            ]

            rounds_stats.append({
                "round": r_num,
                "acc_mean": float(np.mean(accs)) if accs else 0.0,
                "acc_std": float(np.std(accs)) if len(accs) > 1 else 0.0,
                "loss_mean": float(np.mean(losses)) if losses else 0.0,
                "loss_std": float(np.std(losses)) if len(losses) > 1 else 0.0,
                "src_recall_mean": float(np.mean(src_recs)) if src_recs else 0.0,
                "src_recall_std": float(np.std(src_recs)) if len(src_recs) > 1 else 0.0,
                "asr_mean": float(np.mean(asrs)) if asrs else 0.0,
                "asr_std": float(np.std(asrs)) if len(asrs) > 1 else 0.0,
                "time_mean": float(np.mean(times)) if times else 0.0,
            })

        # Média da Matriz de Confusão Final
        cms = [t.get("final_confusion_matrix") for t in trials if t.get("final_confusion_matrix")]
        if cms:
            cm_mean = np.mean(np.array(cms), axis=0).tolist()
        else:
            cm_mean = None

        # Finais
        final_accs = [t.get("final_accuracy", 0.0) for t in trials if t.get("final_accuracy") is not None]
        final_asrs = [t.get("final_asr", 0.0) for t in trials if t.get("final_asr") is not None]
        final_recs = [t.get("final_source_class_recall", 0.0) for t in trials if t.get("final_source_class_recall") is not None]
        mrts = [t.get("mrt_s", 0.0) for t in trials if t.get("mrt_s") is not None]

        # Cumulative Attack Impact (CAI) - Área de perda em relação a 1.0 (ou baseline ideal)
        # CAI = soma da perda de recall ao longo das rodadas
        cai_values = []
        for t in trials:
            cai_t = sum(1.0 - (r.get("source_class_recall", 0.0) or 0.0) for r in t.get("rounds", []))
            cai_values.append(cai_t)

        label = f"{strategy} | Atk={attack_type} | α={dirichlet_alpha} | PR={poison_rate}"
        if num_trials > 1:
            label_legenda = f"{label} (N={num_trials} trials)"
        else:
            label_legenda = label

        cenarios_consolidados.append({
            "chave": chave,
            "label": label,
            "label_legenda": label_legenda,
            "strategy": strategy,
            "attack_type": attack_type,
            "poison_rate": poison_rate,
            "dirichlet_alpha": dirichlet_alpha,
            "num_server_rounds": num_rounds,
            "num_trials": num_trials,
            "rounds_stats": rounds_stats,
            "final_acc_mean": float(np.mean(final_accs)) if final_accs else 0.0,
            "final_acc_std": float(np.std(final_accs)) if len(final_accs) > 1 else 0.0,
            "final_asr_mean": float(np.mean(final_asrs)) if final_asrs else 0.0,
            "final_asr_std": float(np.std(final_asrs)) if len(final_asrs) > 1 else 0.0,
            "final_rec_mean": float(np.mean(final_recs)) if final_recs else 0.0,
            "final_rec_std": float(np.std(final_recs)) if len(final_recs) > 1 else 0.0,
            "mrt_mean": float(np.mean(mrts)) if mrts else 0.0,
            "cai_mean": float(np.mean(cai_values)) if cai_values else 0.0,
            "cai_std": float(np.std(cai_values)) if len(cai_values) > 1 else 0.0,
            "cm_mean": cm_mean,
        })

    return cenarios_consolidados


def plotar_figura1_divergencia(cenarios: list[dict], output_dir: str):
    """FIGURA 1: Ponto Cego com Bandas Sombreadas de Desvio Padrão."""
    fig, ax = plt.subplots(figsize=(13, 7))

    for i, cenario in enumerate(cenarios):
        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]

        rounds = [r["round"] for r in cenario["rounds_stats"]]
        acc_means = np.array([r["acc_mean"] * 100 for r in cenario["rounds_stats"]])
        acc_stds = np.array([r["acc_std"] * 100 for r in cenario["rounds_stats"]])
        rec_means = np.array([r["src_recall_mean"] * 100 for r in cenario["rounds_stats"]])
        rec_stds = np.array([r["src_recall_std"] * 100 for r in cenario["rounds_stats"]])

        # 1. Linha da Acurácia Global
        ax.plot(
            rounds, acc_means,
            color=color, marker=marker, linestyle="-",
            label=f"{cenario['strategy']} (Acurácia Global)",
        )
        if cenario["num_trials"] > 1:
            ax.fill_between(
                rounds, np.clip(acc_means - acc_stds, 0, 100), np.clip(acc_means + acc_stds, 0, 100),
                color=color, alpha=0.18
            )

        # 2. Linha do Recall da Classe Vítima
        ax.plot(
            rounds, rec_means,
            color=color, marker=marker, linestyle="--", alpha=0.85,
            label=f"{cenario['strategy']} (Recall Classe Vítima)",
        )
        if cenario["num_trials"] > 1:
            ax.fill_between(
                rounds, np.clip(rec_means - rec_stds, 0, 100), np.clip(rec_means + rec_stds, 0, 100),
                color=color, alpha=0.12
            )

    ax.set_xlabel("Rodada de Treinamento Federado", fontsize=12, fontweight="bold")
    ax.set_ylabel("Desempenho Médio ± Desvio Padrão (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Figura 1: Ponto Cego sob Ataques Furtivos em Aprendizado Federado\n"
        "(Acurácia Global Aparentada vs. Destruição do Recall da Classe Vítima)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.set_ylim(-5, 105)
    ax.set_xlim(left=1)
    ax.legend(fontsize=9, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=True)

    fig.tight_layout()
    out_path = os.path.join(output_dir, "figura1_divergencia_ponto_cego.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 1 salva: {out_path}")


def plotar_figura2_heatmaps(cenarios: list[dict], output_dir: str):
    """FIGURA 2: Heatmaps das Matrizes de Confusão (Médias dos Trials)."""
    os.makedirs(output_dir, exist_ok=True)

    for cenario in cenarios:
        cm = cenario.get("cm_mean")
        if cm is None:
            continue

        cm_array = np.array(cm)
        row_sums = cm_array.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        cm_norm = (cm_array / row_sums) * 100

        fig, ax = plt.subplots(figsize=(9, 7.5))
        cax = ax.matshow(cm_norm, cmap="Blues", vmin=0, vmax=100)
        cbar = fig.colorbar(cax, fraction=0.046, pad=0.04)
        cbar.set_label("Percentual de Predições (%)", rotation=270, labelpad=15)

        ax.set_xticks(range(len(CIFAR10_CLASSES)))
        ax.set_yticks(range(len(CIFAR10_CLASSES)))
        ax.set_xticklabels(CIFAR10_CLASSES, rotation=45, ha="left", fontsize=9)
        ax.set_yticklabels(CIFAR10_CLASSES, fontsize=9)

        for i in range(len(CIFAR10_CLASSES)):
            for j in range(len(CIFAR10_CLASSES)):
                val = cm_norm[i, j]
                color = "white" if val > 50 else "black"
                ax.text(j, i, f"{val:.0f}%", ha="center", va="center", color=color, fontsize=8)

        st = cenario["strategy"]
        atk = cenario["attack_type"]
        da = cenario["dirichlet_alpha"]
        n = cenario["num_trials"]

        ax.set_xlabel("Classe Predita", fontsize=11, fontweight="bold", labelpad=10)
        ax.set_ylabel("Classe Real (Gabarito)", fontsize=11, fontweight="bold")
        ax.set_title(
            f"Matriz de Confusão Média: {st} sob {atk} (α={da}, N={n} trials)",
            fontsize=12, fontweight="bold", pad=20
        )

        fig.tight_layout()
        nome_arquivo = f"matriz_confusao_{st}_{atk}_pr{cenario['poison_rate']}_da{da}.png"
        out_path = os.path.join(output_dir, nome_arquivo)
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  [✓] Matriz de Confusão salva: {out_path}")


def plotar_figura3_asr_barras(cenarios: list[dict], output_dir: str):
    """FIGURA 3: Barras de ASR com Barras de Erro de Desvio Padrão."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    labels = [c["label_legenda"] for c in cenarios]
    asrs_mean = [c["final_asr_mean"] * 100 for c in cenarios]
    asrs_std = [c["final_asr_std"] * 100 for c in cenarios]
    cores = [COLORS[i % len(COLORS)] for i in range(len(cenarios))]

    y_pos = np.arange(len(labels))
    bars = ax.barh(
        y_pos, asrs_mean,
        xerr=asrs_std if any(s > 0 for s in asrs_std) else None,
        color=cores, height=0.55, edgecolor="black", alpha=0.85, capsize=4
    )

    for bar, mean_val, std_val in zip(bars, asrs_mean, asrs_std):
        width = bar.get_width()
        texto = f"{mean_val:.1f}%" if std_val == 0 else f"{mean_val:.1f} ± {std_val:.1f}%"
        ax.text(
            width + 2.0, bar.get_y() + bar.get_height() / 2,
            texto, ha="left", va="center", fontsize=9, fontweight="bold"
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Attack Success Rate - ASR (%) [Média ± Desvio Padrão]", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 115)
    ax.set_title(
        "Figura 3: Comparativo de Resiliência a Backdoor (ASR por Estratégia)\n"
        "(Menor ASR = Maior Resiliência da Defesa)",
        fontsize=12, fontweight="bold", pad=12
    )

    fig.tight_layout()
    out_path = os.path.join(output_dir, "figura3_comparativo_asr.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 3 (ASR) salva: {out_path}")


def plotar_curvas_gerais(cenarios: list[dict], output_dir: str):
    """Gera curvas de Acurácia Global, Loss e MRT com bandas sombreadas."""
    # 1. Acurácia Global
    fig_acc, ax_acc = plt.subplots(figsize=(11, 5.5))
    for i, c in enumerate(cenarios):
        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]
        rounds = [r["round"] for r in c["rounds_stats"]]
        acc_means = np.array([r["acc_mean"] * 100 for r in c["rounds_stats"]])
        acc_stds = np.array([r["acc_std"] * 100 for r in c["rounds_stats"]])
        ax_acc.plot(rounds, acc_means, color=color, marker=marker, label=c["label_legenda"])
        if c["num_trials"] > 1:
            ax_acc.fill_between(rounds, np.clip(acc_means - acc_stds, 0, 100), np.clip(acc_means + acc_stds, 0, 100), color=color, alpha=0.18)
    ax_acc.set_xlabel("Rodada", fontsize=11)
    ax_acc.set_ylabel("Acurácia Global (%) [Média ± σ]", fontsize=11)
    ax_acc.set_title("Evolução da Acurácia Global por Rodada", fontsize=12, fontweight="bold")
    ax_acc.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig_acc.tight_layout()
    fig_acc.savefig(os.path.join(output_dir, "comparativo_acuracia_global.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_acc)

    # 2. Loss
    fig_loss, ax_loss = plt.subplots(figsize=(11, 5.5))
    for i, c in enumerate(cenarios):
        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]
        rounds = [r["round"] for r in c["rounds_stats"]]
        loss_means = np.array([r["loss_mean"] for r in c["rounds_stats"]])
        loss_stds = np.array([r["loss_std"] for r in c["rounds_stats"]])
        ax_loss.plot(rounds, loss_means, color=color, marker=marker, label=c["label_legenda"])
        if c["num_trials"] > 1:
            ax_loss.fill_between(rounds, np.maximum(loss_means - loss_stds, 0), loss_means + loss_stds, color=color, alpha=0.18)
    ax_loss.set_xlabel("Rodada", fontsize=11)
    ax_loss.set_ylabel("Perda (Loss) [Média ± σ]", fontsize=11)
    ax_loss.set_title("Evolução da Perda (Loss) Global por Rodada", fontsize=12, fontweight="bold")
    ax_loss.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig_loss.tight_layout()
    fig_loss.savefig(os.path.join(output_dir, "comparativo_loss.png"), dpi=300, bbox_inches="tight")
    plt.close(fig_loss)


def gerar_tabela_resumo_estatistico(cenarios: list[dict], output_base: str):
    """Gera arquivo Markdown e CSV com a tabela resumo estatística pronta para o artigo."""
    linhas_md = [
        "# 📊 Tabela Resumo Estatístico dos Experimentos",
        "",
        "| Defesa | Ataque | Dirichlet (α) | Taxa (PR) | Trials (N) | Acurácia Global Final (%) | Recall Classe Vítima (%) | ASR Final (%) | CAI (Impacto Acumulado) | MRT (s/rodada) |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    linhas_csv = [
        "Defesa,Ataque,Dirichlet_Alpha,Poison_Rate,Num_Trials,Acc_Global_Mean,Acc_Global_Std,Recall_Vitima_Mean,Recall_Vitima_Std,ASR_Mean,ASR_Std,CAI_Mean,CAI_Std,MRT_s"
    ]

    for c in cenarios:
        n = c["num_trials"]
        acc_str = f"{c['final_acc_mean']*100:.2f} ± {c['final_acc_std']*100:.2f}" if n > 1 else f"{c['final_acc_mean']*100:.2f}"
        rec_str = f"{c['final_rec_mean']*100:.2f} ± {c['final_rec_std']*100:.2f}" if n > 1 else f"{c['final_rec_mean']*100:.2f}"
        asr_str = f"{c['final_asr_mean']*100:.2f} ± {c['final_asr_std']*100:.2f}" if n > 1 else f"{c['final_asr_mean']*100:.2f}"
        cai_str = f"{c['cai_mean']:.2f} ± {c['cai_std']:.2f}" if n > 1 else f"{c['cai_mean']:.2f}"
        mrt_str = f"{c['mrt_mean']:.2f}"

        linhas_md.append(
            f"| **{c['strategy']}** | `{c['attack_type']}` | {c['dirichlet_alpha']} | {c['poison_rate']} | {n} | {acc_str}% | {rec_str}% | {asr_str}% | {cai_str} | {mrt_str} s |"
        )

        linhas_csv.append(
            f"{c['strategy']},{c['attack_type']},{c['dirichlet_alpha']},{c['poison_rate']},{n},{c['final_acc_mean']*100:.4f},{c['final_acc_std']*100:.4f},{c['final_rec_mean']*100:.4f},{c['final_rec_std']*100:.4f},{c['final_asr_mean']*100:.4f},{c['final_asr_std']*100:.4f},{c['cai_mean']:.4f},{c['cai_std']:.4f},{c['mrt_mean']:.4f}"
        )

    md_path = os.path.join(output_base, "tabela_resumo_estatistico.md")
    csv_path = os.path.join(output_base, "tabela_resumo_estatistico.csv")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_csv))

    print(f"  [✓] Tabela Estatística Markdown salva: {md_path}")
    print(f"  [✓] Tabela Estatística CSV salva:      {csv_path}")


def main():
    print("=" * 75)
    print("  AGREGADOR ESTATÍSTICO & PLOTTER CIENTÍFICO (MULTI-TRIAL)")
    print("=" * 75)
    print(f"  Diretório de Métricas: {METRICS_DIR}")
    print(f"  Diretório de Gráficos: {OUTPUT_DIR}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CM_OUTPUT_DIR, exist_ok=True)

    grupos = carregar_e_agrupar_experimentos(METRICS_DIR)
    if not grupos:
        print("  [!] Nenhum arquivo de métricas JSON encontrado.")
        print("      Execute uma ou mais simulações via 'flwr run .' para gerar dados.")
        return

    cenarios = consolidar_estatisticas(grupos)
    print(f"  Cenários únicos consolidados: {len(cenarios)}")
    for c in cenarios:
        print(f"  - {c['label_legenda']}")

    print("\n  Gerando figuras científicas e tabelas estatísticas...")
    plotar_figura1_divergencia(cenarios, OUTPUT_DIR)
    plotar_figura2_heatmaps(cenarios, CM_OUTPUT_DIR)
    plotar_figura3_asr_barras(cenarios, OUTPUT_DIR)
    plotar_curvas_gerais(cenarios, OUTPUT_DIR)
    gerar_tabela_resumo_estatistico(cenarios, BASE_RESULTS_DIR)

    print("\n" + "=" * 75)
    print(f"  [✓] Concluído com sucesso! Resultados em: {BASE_RESULTS_DIR}")
    print("=" * 75)


if __name__ == "__main__":
    main()

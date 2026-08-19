"""
plotar_resultados.py — Suíte de Visualização Científica e Agregação Estatística.

Gera 4 Figuras Científicas Claras, Focadas e de Padrão de Publicação:
1. FIGURA 1: Avaliação sob Ataque Normal / Bruto (Ruído Gaussiano) — Acurácia Global e Perda (Loss)
2. FIGURA 2: O Ponto Cego sob Ataque Furtivo (Targeted Backdoor) — Acurácia Global Aparentada vs. Colapso do Recall Vítima
3. FIGURA 3: Comparativo de Resiliência (Ataque Normal vs. Ataque Furtivo) em Gráfico de Barras
4. FIGURA 4: Grid 2x2 de Matrizes de Confusão sob Ataque Furtivo (FedAvg, FedMedian, Krum, Bulyan)
5. TABELAS: Resumo estatístico consolidado em Markdown (.md) e CSV (.csv)

Uso:
    python plotar_resultados.py
"""

import glob
import json
import os
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore


# ============================================================================
# DIRETÓRIOS E CONFIGURAÇÃO VISUAL CIENTÍFICA
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_RESULTS_DIR = os.path.join(SCRIPT_DIR, "resultados_ataque_furtivo")
METRICS_DIR = os.path.join(BASE_RESULTS_DIR, "metrics_json")
OUTPUT_DIR = os.path.join(BASE_RESULTS_DIR, "graficos")
CM_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "matrizes_confusao")

plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "lines.linewidth": 2.4,
    "lines.markersize": 6,
    "legend.fontsize": 10,
})

DEFENSE_COLORS = {
    "Baseline (Sem Ataque)": "#37474F", # Cinza Chumbo
    "FedAvg":    "#1976D2",             # Azul Royal
    "FedMedian": "#E53935",             # Vermelho
    "Krum":      "#2E7D32",             # Verde Floresta
    "Bulyan":    "#7B1FA2",             # Roxo Nobre
}

DEFENSE_MARKERS = {
    "Baseline (Sem Ataque)": "o",
    "FedAvg":    "s",
    "FedMedian": "^",
    "Krum":      "D",
    "Bulyan":    "P",
}

CIFAR10_CLASSES = [
    "Airplane", "Automobile", "Bird", "Cat", "Deer",
    "Dog", "Frog", "Horse", "Ship", "Truck"
]


# ============================================================================
# CARREGAMENTO E CONSOLIDAÇÃO ESTATÍSTICA
# ============================================================================

def carregar_e_agrupar_experimentos(diretorio: str) -> dict:
    """Carrega todos os JSONs de métricas e agrupa por cenário único."""
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
            float(config.get("dirichlet_alpha", 0.1)),
            int(config.get("num_server_rounds", 10)),
        )
        grupos[chave_cenario].append(data)

    return grupos


def consolidar_estatisticas(grupos: dict) -> list[dict]:
    """Calcula média e desvio padrão para cada rodada dos cenários agrupados."""
    cenarios_consolidados = []

    for chave, trials in grupos.items():
        strategy, attack_type, poison_rate, dirichlet_alpha, num_rounds = chave
        num_trials = len(trials)

        all_rounds = sorted(list({r["round"] for t in trials for r in t.get("rounds", [])}))
        rounds_stats = []

        for r_num in all_rounds:
            accs = [r.get("accuracy", 0.0) for t in trials for r in t.get("rounds", []) if r.get("round") == r_num]
            losses = [r.get("loss", 0.0) for t in trials for r in t.get("rounds", []) if r.get("round") == r_num]
            src_recs = [r.get("source_class_recall", 0.0) for t in trials for r in t.get("rounds", []) if r.get("round") == r_num]
            asrs = [r.get("asr", 0.0) for t in trials for r in t.get("rounds", []) if r.get("round") == r_num]
            times = [r.get("round_time_s", 0.0) for t in trials for r in t.get("rounds", []) if r.get("round") == r_num]

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

        cms = [t.get("final_confusion_matrix") for t in trials if t.get("final_confusion_matrix")]
        cm_mean = np.mean(np.array(cms), axis=0).tolist() if cms else None

        final_accs = [t.get("final_accuracy", 0.0) for t in trials if t.get("final_accuracy") is not None]
        final_asrs = [t.get("final_asr", 0.0) for t in trials if t.get("final_asr") is not None]
        final_recs = [t.get("final_source_class_recall", 0.0) for t in trials if t.get("final_source_class_recall") is not None]
        mrts = [t.get("mrt_s", 0.0) for t in trials if t.get("mrt_s") is not None]

        cai_values = [sum(1.0 - (r.get("source_class_recall", 0.0) or 0.0) for r in t.get("rounds", [])) for t in trials]

        label = f"{strategy} | {attack_type} (PR={poison_rate*100:.0f}%)"
        if poison_rate == 0.0:
            categoria = "Controle Limpo"
            nome_legenda = "Baseline (Sem Ataque)"
        elif attack_type == "gaussian_noise":
            categoria = "Ataque Normal"
            nome_legenda = strategy
        else:
            categoria = "Ataque Furtivo"
            nome_legenda = strategy

        cenarios_consolidados.append({
            "chave": chave,
            "label": label,
            "nome_legenda": nome_legenda,
            "categoria": categoria,
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


# ============================================================================
# GERADOR DE FIGURAS CIENTÍFICAS
# ============================================================================

def plotar_figura1_ataque_normal(cenarios: list[dict], output_dir: str):
    """
    FIGURA 1: Avaliação sob Ataque Normal (Ruído Gaussiano, PR=40%).
    Subplot 1: Acurácia Global por Rodada (4 defesas + baseline).
    Subplot 2: Perda (Loss) por Rodada.
    """
    # Filtra cenários relevantes
    normais = [c for c in cenarios if c["attack_type"] == "gaussian_noise" or c["poison_rate"] == 0.0]
    if not normais:
        return

    fig, (ax_acc, ax_loss) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Ordem fixa de plotagem
    ordem_defesas = ["Baseline (Sem Ataque)", "FedAvg", "FedMedian", "Krum", "Bulyan"]

    for def_nome in ordem_defesas:
        c_list = [c for c in normais if c["nome_legenda"] == def_nome or (def_nome == "Baseline (Sem Ataque)" and c["poison_rate"] == 0.0)]
        if not c_list:
            continue
        c = c_list[0]

        color = DEFENSE_COLORS.get(def_nome, "#555555")
        marker = DEFENSE_MARKERS.get(def_nome, "o")
        linestyle = "--" if def_nome == "Baseline (Sem Ataque)" else "-"

        rounds = [r["round"] for r in c["rounds_stats"]]
        acc_means = [r["acc_mean"] * 100 for r in c["rounds_stats"]]
        acc_stds = [r["acc_std"] * 100 for r in c["rounds_stats"]]
        loss_means = [r["loss_mean"] for r in c["rounds_stats"]]
        loss_stds = [r["loss_std"] for r in c["rounds_stats"]]

        # 1. Acurácia Global
        ax_acc.plot(rounds, acc_means, color=color, marker=marker, linestyle=linestyle, label=def_nome)
        if c["num_trials"] > 1:
            ax_acc.fill_between(rounds, np.clip(np.array(acc_means) - np.array(acc_stds), 0, 100),
                                np.clip(np.array(acc_means) + np.array(acc_stds), 0, 100), color=color, alpha=0.15)

        # 2. Perda (Loss)
        ax_loss.plot(rounds, loss_means, color=color, marker=marker, linestyle=linestyle, label=def_nome)
        if c["num_trials"] > 1:
            ax_loss.fill_between(rounds, np.maximum(np.array(loss_means) - np.array(loss_stds), 0),
                                 np.array(loss_means) + np.array(loss_stds), color=color, alpha=0.15)

    ax_acc.set_title("(A) Acurácia Global sob Ataque Normal (Ruído)")
    ax_acc.set_xlabel("Rodada de Treinamento")
    ax_acc.set_ylabel("Acurácia Global (%)")
    ax_acc.set_ylim(0, 100)
    ax_acc.legend(loc="best", frameon=True)

    ax_loss.set_title("(B) Evolução da Perda (Loss) Global")
    ax_loss.set_xlabel("Rodada de Treinamento")
    ax_loss.set_ylabel("Cross-Entropy Loss")
    ax_loss.legend(loc="best", frameon=True)

    fig.suptitle("Figura 1: Resiliência das Defesas Convencionais contra Ataque Normal (Ruído Gaussiano, 40%)", fontsize=14, fontweight="bold", y=0.98)
    fig.tight_layout()

    out_path = os.path.join(output_dir, "figura1_ataque_normal_acuracia_e_loss.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 1 salva: {out_path}")


def plotar_figura2_ataque_furtivo(cenarios: list[dict], output_dir: str):
    """
    FIGURA 2: O Ponto Cego sob Ataque Furtivo (Targeted Backdoor, PR=40%).
    Subplot 1: Acurácia Global Aparentada (4 defesas parecem saudáveis).
    Subplot 2: Recall da Classe Vítima (Mostra o colapso oculto para 0%).
    """
    furtivos = [c for c in cenarios if c["attack_type"] == "targeted_backdoor"]
    baseline = [c for c in cenarios if c["poison_rate"] == 0.0]
    if not furtivos:
        return

    fig, (ax_acc, ax_rec) = plt.subplots(1, 2, figsize=(14, 5.5))

    ordem_defesas = ["Baseline (Sem Ataque)", "FedAvg", "FedMedian", "Krum", "Bulyan"]

    for def_nome in ordem_defesas:
        if def_nome == "Baseline (Sem Ataque)":
            if not baseline:
                continue
            c = baseline[0]
            linestyle = "--"
        else:
            c_list = [c for c in furtivos if c["strategy"] == def_nome]
            if not c_list:
                continue
            c = c_list[0]
            linestyle = "-"

        color = DEFENSE_COLORS.get(def_nome, "#555555")
        marker = DEFENSE_MARKERS.get(def_nome, "s")

        rounds = [r["round"] for r in c["rounds_stats"]]
        acc_means = [r["acc_mean"] * 100 for r in c["rounds_stats"]]
        acc_stds = [r["acc_std"] * 100 for r in c["rounds_stats"]]
        rec_means = [r["src_recall_mean"] * 100 for r in c["rounds_stats"]]
        rec_stds = [r["src_recall_std"] * 100 for r in c["rounds_stats"]]

        # 1. Acurácia Global Aparentada
        ax_acc.plot(rounds, acc_means, color=color, marker=marker, linestyle=linestyle, label=def_nome)
        if c["num_trials"] > 1:
            ax_acc.fill_between(rounds, np.clip(np.array(acc_means) - np.array(acc_stds), 0, 100),
                                np.clip(np.array(acc_means) + np.array(acc_stds), 0, 100), color=color, alpha=0.15)

        # 2. Recall da Classe Vítima (Colapso Oculto)
        ax_rec.plot(rounds, rec_means, color=color, marker=marker, linestyle=linestyle, label=def_nome)
        if c["num_trials"] > 1:
            ax_rec.fill_between(rounds, np.clip(np.array(rec_means) - np.array(rec_stds), 0, 100),
                                np.clip(np.array(rec_means) + np.array(rec_stds), 0, 100), color=color, alpha=0.15)

    ax_acc.set_title("(A) Acurácia Global Aparentada (Ilusão de Segurança)")
    ax_acc.set_xlabel("Rodada de Treinamento")
    ax_acc.set_ylabel("Acurácia Global (%)")
    ax_acc.set_ylim(0, 100)
    ax_acc.legend(loc="best", frameon=True)

    ax_rec.set_title("(B) Recall da Classe Vítima (Colapso Silencioso)")
    ax_rec.set_xlabel("Rodada de Treinamento")
    ax_rec.set_ylabel("Recall da Classe Vítima (%) [Gato]")
    ax_rec.set_ylim(-5, 100)
    ax_rec.axhline(0, color="black", linestyle=":", alpha=0.4)
    ax_rec.legend(loc="best", frameon=True)

    fig.suptitle("Figura 2: O Ponto Cego sob Ataque Furtivo (Targeted Backdoor, 40%)", fontsize=14, fontweight="bold", y=0.98)
    fig.tight_layout()

    out_path = os.path.join(output_dir, "figura2_ataque_furtivo_ponto_cego.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 2 salva: {out_path}")


def plotar_figura3_resumo_barras(cenarios: list[dict], output_dir: str):
    """
    FIGURA 3: Comparativo de Resiliência em Barras (Normal vs. Furtivo).
    Subplot 1: Acurácia Global Final por Defesa.
    Subplot 2: Attack Success Rate (ASR) sob Backdoor.
    """
    defesas = ["FedAvg", "FedMedian", "Krum", "Bulyan"]
    
    acc_normal = []
    acc_furtivo = []
    asr_furtivo = []

    for d in defesas:
        cn = [c for c in cenarios if c["strategy"] == d and c["attack_type"] == "gaussian_noise"]
        cf = [c for c in cenarios if c["strategy"] == d and c["attack_type"] == "targeted_backdoor"]
        
        acc_normal.append(cn[0]["final_acc_mean"] * 100 if cn else 0.0)
        acc_furtivo.append(cf[0]["final_acc_mean"] * 100 if cf else 0.0)
        asr_furtivo.append(cf[0]["final_asr_mean"] * 100 if cf else 0.0)

    x = np.arange(len(defesas))
    width = 0.35

    fig, (ax_bar1, ax_bar2) = plt.subplots(1, 2, figsize=(14, 5.2))

    # 1. Barras de Acurácia Global Final
    rects1 = ax_bar1.bar(x - width/2, acc_normal, width, label="Ataque Normal (Ruído)", color="#78909C", edgecolor="black")
    rects2 = ax_bar1.bar(x + width/2, acc_furtivo, width, label="Ataque Furtivo (Backdoor)", color="#EF5350", edgecolor="black")

    ax_bar1.set_ylabel("Acurácia Global Final (%)")
    ax_bar1.set_title("(A) Comparativo de Acurácia Global Final")
    ax_bar1.set_xticks(x)
    ax_bar1.set_xticklabels(defesas, fontweight="bold")
    ax_bar1.set_ylim(0, 100)
    ax_bar1.legend(loc="upper left")

    # Adiciona rótulos numéricos sobre as barras
    for rect in rects1 + rects2:
        h = rect.get_height()
        if h > 0:
            ax_bar1.annotate(f"{h:.1f}%",
                             xy=(rect.get_x() + rect.get_width() / 2, h),
                             xytext=(0, 3), textcoords="offset points",
                             ha="center", va="bottom", fontsize=9, fontweight="bold")

    # 2. Barras de ASR (Taxa de Sucesso do Ataque Furtivo)
    cores_asr = [DEFENSE_COLORS[d] for d in defesas]
    bars_asr = ax_bar2.bar(defesas, asr_furtivo, width=0.5, color=cores_asr, edgecolor="black")
    ax_bar2.set_ylabel("Attack Success Rate - ASR (%)")
    ax_bar2.set_title("(B) Taxa de Infiltração do Backdoor (ASR)")
    ax_bar2.set_ylim(0, 115)

    for bar in bars_asr:
        h = bar.get_height()
        ax_bar2.annotate(f"{h:.1f}%",
                         xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points",
                         ha="center", va="bottom", fontsize=10, fontweight="bold")

    fig.suptitle("Figura 3: Resumo Comparativo de Desempenho e Infiltração por Defesa", fontsize=14, fontweight="bold", y=0.98)
    fig.tight_layout()

    out_path = os.path.join(output_dir, "figura3_resumo_barras_comparativo.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 3 salva: {out_path}")


def plotar_figura4_matrizes_confusao(cenarios: list[dict], output_dir: str):
    """
    FIGURA 4: Grid 2x2 elegante das Matrizes de Confusão sob Targeted Backdoor.
    (FedAvg, FedMedian, Krum, Bulyan).
    """
    furtivos = [c for c in cenarios if c["attack_type"] == "targeted_backdoor"]
    if not furtivos:
        return

    defesas = ["FedAvg", "FedMedian", "Krum", "Bulyan"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    axes_flat = axes.flatten()

    for idx, d in enumerate(defesas):
        ax = axes_flat[idx]
        c_list = [c for c in furtivos if c["strategy"] == d]
        if not c_list or c_list[0].get("cm_mean") is None:
            ax.text(0.5, 0.5, f"Dados não disponíveis\npara {d}", ha="center", va="center")
            continue

        c = c_list[0]
        cm = np.array(c["cm_mean"])
        
        # Normaliza por linha (recall por classe)
        row_sums = cm.sum(axis=1, keepdims=True)
        cm_norm = np.divide(cm, row_sums, out=np.zeros_like(cm, dtype=float), where=row_sums != 0) * 100

        im = ax.imshow(cm_norm, interpolation="nearest", cmap="Blues", vmin=0, vmax=100)

        # Destaca a célula do ataque (Classe 3 = Cat -> Classe 5 = Dog)
        ax.add_patch(plt.Rectangle((4.5, 2.5), 1, 1, fill=False, edgecolor="red", lw=2.5, linestyle="--"))

        ax.set_title(f"Defesa: {d} (ASR: {c['final_asr_mean']*100:.1f}%)", fontweight="bold", fontsize=11)
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels([c[:3] for c in CIFAR10_CLASSES], fontsize=8)
        ax.set_yticklabels([c[:3] for c in CIFAR10_CLASSES], fontsize=8)
        ax.set_xlabel("Classe Prevista", fontsize=9)
        ax.set_ylabel("Classe Real", fontsize=9)

    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.7, label="Taxa de Predição (%)")
    fig.suptitle("Figura 4: Matrizes de Confusão 10x10 sob Ataque Furtivo (Targeted Backdoor)\n[Destaque Vermelho: Classe Vítima Cat -> Dog]", fontsize=13, fontweight="bold", y=0.98)

    out_path = os.path.join(output_dir, "figura4_matrizes_confusao_comparativas.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] Figura 4 salva: {out_path}")


# ============================================================================
# GERADOR DE TABELAS FORMATADAS
# ============================================================================

def gerar_tabela_resumo_estatistico(cenarios: list[dict], output_base: str):
    """Gera arquivos Markdown e CSV limpos e organizados por família de teste."""
    linhas_md = [
        "# 📊 Tabela Resumo Estatístico dos Experimentos (Artigo 1)",
        "",
        "| Categoria | Defesa | Ataque | PR (%) | Acurácia Global Final (%) | Recall Vítima (%) | ASR Final (%) | MRT (s/rod) |",
        "|---|---|---|:---:|:---:|:---:|:---:|:---:|",
    ]

    linhas_csv = [
        "Categoria,Defesa,Ataque,Dirichlet_Alpha,Poison_Rate,Num_Trials,Acc_Global_Final,Recall_Vitima_Final,ASR_Final,MRT_s"
    ]

    # Ordena por Categoria e Defesa
    ordem_cat = {"Controle Limpo": 0, "Ataque Normal": 1, "Ataque Furtivo": 2}
    cenarios_ordenados = sorted(cenarios, key=lambda c: (ordem_cat.get(c["categoria"], 9), c["strategy"]))

    for c in cenarios_ordenados:
        n = c["num_trials"]
        acc_str = f"{c['final_acc_mean']*100:.2f} ± {c['final_acc_std']*100:.2f}" if n > 1 else f"{c['final_acc_mean']*100:.2f}"
        rec_str = f"{c['final_rec_mean']*100:.2f} ± {c['final_rec_std']*100:.2f}" if n > 1 else f"{c['final_rec_mean']*100:.2f}"
        asr_str = f"{c['final_asr_mean']*100:.2f} ± {c['final_asr_std']*100:.2f}" if n > 1 else f"{c['final_asr_mean']*100:.2f}"
        mrt_str = f"{c['mrt_mean']:.2f}"

        linhas_md.append(
            f"| {c['categoria']} | **{c['strategy']}** | `{c['attack_type']}` | {c['poison_rate']*100:.0f}% | {acc_str}% | {rec_str}% | {asr_str}% | {mrt_str} s |"
        )

        linhas_csv.append(
            f"{c['categoria']},{c['strategy']},{c['attack_type']},{c['dirichlet_alpha']},{c['poison_rate']},{n},{c['final_acc_mean']*100:.4f},{c['final_rec_mean']*100:.4f},{c['final_asr_mean']*100:.4f},{c['mrt_mean']:.4f}"
        )

    md_path = os.path.join(output_base, "tabela_resumo_estatistico.md")
    csv_path = os.path.join(output_base, "tabela_resumo_estatistico.csv")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_csv))

    print("\n" + "═" * 90)
    print("  📋 PAINEL RESUMO ESTATÍSTICO DOS EXPERIMENTOS")
    print("═" * 90)
    print(f"{'CATEGORIA':<16} | {'DEFESA':<11} | {'ATAQUE':<18} | {'ACC GLOBAL':<12} | {'RECALL VÍT.':<12} | {'ASR':<10}")
    print("─" * 90)
    for c in cenarios_ordenados:
        acc_str = f"{c['final_acc_mean']*100:5.2f}%"
        rec_str = f"{c['final_rec_mean']*100:5.2f}%"
        asr_str = f"{c['final_asr_mean']*100:5.2f}%"
        ponto_cego = " 🚨 (Ponto Cego!)" if c['final_rec_mean'] < 0.15 and c['attack_type'] == 'targeted_backdoor' else ""
        print(f"{c['categoria']:<16} | {c['strategy']:<11} | {c['attack_type']:<18} | {acc_str:<12} | {rec_str:<12} | {asr_str:<10}{ponto_cego}")
    print("═" * 90)
    print(f"  [✓] Tabela Markdown salva: {md_path}")
    print(f"  [✓] Tabela CSV salva:      {csv_path}")


# ============================================================================
# PONTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    print("=" * 78)
    print("  🚀 GERADOR DE FIGURAS CIENTÍFICAS E TABELAS ESTATÍSTICAS (ARTIGO 1)")
    print("=" * 78)
    print(f"  Métricas: {METRICS_DIR}")
    print(f"  Gráficos: {OUTPUT_DIR}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CM_OUTPUT_DIR, exist_ok=True)

    grupos = carregar_e_agrupar_experimentos(METRICS_DIR)
    if not grupos:
        print("  [!] Nenhum arquivo de métricas JSON encontrado.")
        return

    cenarios = consolidar_estatisticas(grupos)
    print(f"  Total de cenários consolidados: {len(cenarios)}")

    print("\n  Gerando as 4 Figuras Científicas do Artigo...")
    plotar_figura1_ataque_normal(cenarios, OUTPUT_DIR)
    plotar_figura2_ataque_furtivo(cenarios, OUTPUT_DIR)
    plotar_figura3_resumo_barras(cenarios, OUTPUT_DIR)
    plotar_figura4_matrizes_confusao(cenarios, OUTPUT_DIR)
    gerar_tabela_resumo_estatistico(cenarios, BASE_RESULTS_DIR)

    print("\n" + "=" * 78)
    print(f"  [✓] Todas as figuras e tabelas geradas com sucesso em: {OUTPUT_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    main()

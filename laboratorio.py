"""
laboratorio.py — Interface Interativa para o Laboratório de Segurança Federada.

Execute na RAIZ do projeto:
    python laboratorio.py

O script gerencia automaticamente:
  - Configuração de UTF-8 no terminal Windows
  - Execução dos lotes de simulação com Flower no subdiretório quickstart-pytorch/
  - Suporte a repetições estatísticas (Multi-Trial com Seeds variadas para curvas suaves)
  - Limpeza de processos Ray e pausas seguras entre rodadas
  - Geração automática das figuras científicas do Artigo 1 e tabelas de resumo (CAI, ASR, etc.)
  - Arquivamento organizado dos experimentos em experimentos/
"""

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ─── Caminhos do projeto ──────────────────────────────────────────────────────
RAIZ             = Path(__file__).parent
SRC              = RAIZ / "quickstart-pytorch"
BASE_RESULTS_DIR = SRC / "resultados_ataque_furtivo"
METRICS_DIR      = BASE_RESULTS_DIR / "metrics_json"
GRAFICOS_DIR     = BASE_RESULTS_DIR / "graficos"
EXPERIMENTOS     = RAIZ / "experimentos"

# ─── Paleta de cores ANSI ─────────────────────────────────────────────────────
class Cor:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    GRAY   = "\033[90m"

def c(texto, cor): return f"{cor}{texto}{Cor.RESET}"

# ─── Lotes Pré-Definidos para o Artigo 1 & Benchmarks ────────────────────────
LOTES = {
    "1": {
        "nome": "Artigo 1: Ponto Cego sob Targeted Backdoor (4 Defesas em Non-IID)",
        "descricao": "FedAvg, FedMedian, Krum e Bulyan sob targeted_backdoor (pr=0.4, α=0.1, 10 rodadas)",
        "runs": [
            {"defense_mode": "FedAvg",    "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "FedMedian", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Krum",      "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Bulyan",    "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
        ],
    },
    "2": {
        "nome": "Artigo 1: Efeito da Assimetria (IID vs Non-IID Extremo)",
        "descricao": "Bulyan e FedAvg sob targeted_backdoor em α=100.0 (IID) vs α=0.1 (Non-IID)",
        "runs": [
            {"defense_mode": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 100.0, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 100.0, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1,   "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1,   "num-server-rounds": 10, "seed": 42},
        ],
    },
    "3": {
        "nome": "Artigo 1: Ataque Trigger Patch Físico (Padrão Visual)",
        "descricao": "FedAvg vs Bulyan sob trigger_patch com marca no canto da imagem (pr=0.4, α=0.1)",
        "runs": [
            {"defense_mode": "FedAvg", "attack_type": "trigger_patch", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Bulyan", "attack_type": "trigger_patch", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
        ],
    },
    "4": {
        "nome": "Multi-Trial Rigoroso (3 Seeds para Curvas Suaves e Bandas de Incerteza)",
        "descricao": "Executa Bulyan e FedAvg 3x com seeds 42, 43, 44 para calcular média e desvio padrão",
        "runs": [
            {"defense_mode": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 43},
            {"defense_mode": "FedAvg", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 44},
            {"defense_mode": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 42},
            {"defense_mode": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 43},
            {"defense_mode": "Bulyan", "attack_type": "targeted_backdoor", "poison_rate": 0.4, "dirichlet_alpha": 0.1, "num-server-rounds": 10, "seed": 44},
        ],
    },
    "5": {
        "nome": "Controle de Ataque Bruto (Morte Súbita — Gradient Ascent)",
        "descricao": "Inversão de gradiente contra FedAvg, FedMedian, Krum e Bulyan",
        "runs": [
            {"defense_mode": d, "attack_type": "gradient_ascent", "poison_rate": 1.0, "num-server-rounds": 5, "seed": 42}
            for d in ["FedAvg", "FedMedian", "Krum", "Bulyan"]
        ],
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def separador(char="═", largura=70):
    print(c(char * largura, Cor.CYAN))

def cabecalho(titulo):
    separador()
    print(c(f"  {titulo}", Cor.BOLD + Cor.CYAN))
    separador()

def proximo_numero_experimento() -> int:
    """Retorna o próximo número de experimento disponível em experimentos/."""
    EXPERIMENTOS.mkdir(exist_ok=True)
    existentes = [
        int(re.match(r"exp_(\d+)", p.name).group(1))
        for p in EXPERIMENTOS.iterdir()
        if p.is_dir() and re.match(r"exp_(\d+)", p.name)
    ]
    return (max(existentes) + 1) if existentes else 1

def construir_run_config(params: dict) -> str:
    """Monta a string --run-config a partir de um dicionário de parâmetros."""
    partes = []
    for chave, valor in params.items():
        if isinstance(valor, str):
            partes.append(f"{chave}='{valor}'")
        else:
            partes.append(f"{chave}={valor}")
    return " ".join(partes)

def executar_run(params: dict, numero: int, total: int) -> bool:
    """Executa um único flwr run . --stream e retorna True se bem-sucedido."""
    run_config = construir_run_config(params)

    print()
    print(c(f"  ▶  Execução {numero}/{total}", Cor.BOLD + Cor.YELLOW))
    print(c(f"     Configuração: {run_config}", Cor.GRAY))
    separador("─", 70)

    cmd = f'flwr run . --stream --run-config "{run_config}"'

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        resultado = subprocess.run(
            cmd,
            shell=True,
            cwd=str(SRC),
            env=env,
        )
        sucesso = resultado.returncode == 0
    except KeyboardInterrupt:
        print(c("\n  [!] Execução interrompida pelo usuário.", Cor.RED))
        return False

    if numero < total:
        print(c("\n  → Pausa e limpeza de processos Ray...", Cor.GRAY))
        subprocess.run("ray stop", shell=True, cwd=str(SRC), capture_output=True, env=env)
        time.sleep(3)

    return sucesso

def gerar_graficos():
    """Executa plotar_resultados.py dentro de quickstart-pytorch/."""
    print()
    print(c("  → Processando métricas e gerando figuras científicas...", Cor.CYAN))
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    resultado = subprocess.run(
        f"{sys.executable} plotar_resultados.py",
        shell=True,
        cwd=str(SRC),
        env=env,
    )
    if resultado.returncode == 0:
        print(c("  ✔  Figuras científicas e tabelas estatísticas geradas.", Cor.GREEN))
    else:
        print(c("  ✘  Erro ao gerar figuras.", Cor.RED))

def arquivar_resultados(nome_descritivo: str):
    """Move JSONs, PNGs e Tabelas para experimentos/expXX_nome/."""
    num = proximo_numero_experimento()
    slug = re.sub(r"[^\w\s]", "", nome_descritivo).strip().replace(" ", "_").lower()
    pasta = EXPERIMENTOS / f"exp_{num:02d}_{slug}"
    dados_dir    = pasta / "dados"
    graficos_dir = pasta / "graficos"
    dados_dir.mkdir(parents=True, exist_ok=True)
    graficos_dir.mkdir(parents=True, exist_ok=True)

    # Mover JSONs
    jsons = list(METRICS_DIR.glob("metrics_*.json"))
    for f in jsons:
        shutil.move(str(f), str(dados_dir / f.name))

    # Mover PNGs (incluindo matrizes de confusão)
    for p in GRAFICOS_DIR.rglob("*.png"):
        rel = p.relative_to(GRAFICOS_DIR)
        dest = graficos_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dest))

    # Copiar tabelas estatísticas geradas
    for tab in BASE_RESULTS_DIR.glob("tabela_resumo_estatistico.*"):
        shutil.copy(str(tab), str(pasta / tab.name))

    print()
    print(c(f"  ✔  Resultados arquivados em: experimentos/{pasta.name}/", Cor.GREEN))
    print(c(f"     {len(jsons)} JSON(s) movidos para dados/", Cor.GRAY))
    print(c(f"     Figuras salvas em graficos/", Cor.GRAY))
    return pasta

def confirmar(mensagem: str) -> bool:
    resp = input(c(f"\n  {mensagem} [s/N]: ", Cor.YELLOW)).strip().lower()
    return resp in ("s", "sim", "y", "yes")

# ─── Fluxo de Execução de um Lote ─────────────────────────────────────────────
def executar_lote(runs: list[dict], nome_lote: str):
    """Executa uma lista de runs e arquiva os resultados."""
    total = len(runs)
    print()
    print(c(f"  Total de execuções no lote: {total}", Cor.CYAN))

    jsons_anteriores = list(METRICS_DIR.glob("metrics_*.json"))
    if jsons_anteriores:
        print(c(f"\n  ℹ  {len(jsons_anteriores)} JSON(s) já existem na pasta — serão somados na análise.", Cor.GRAY))

    if not confirmar("Iniciar execuções agora?"):
        print(c("  Cancelado.", Cor.GRAY))
        return

    print()
    sucessos = 0
    for i, params in enumerate(runs, start=1):
        ok = executar_run(params, i, total)
        if ok:
            sucessos += 1

    separador()
    print(c(f"  Concluído: {sucessos}/{total} execuções bem-sucedidas.", Cor.GREEN if sucessos == total else Cor.YELLOW))

    jsons_gerados = list(METRICS_DIR.glob("metrics_*.json"))
    if jsons_gerados:
        if confirmar("Gerar figuras científicas e tabelas estatísticas?"):
            gerar_graficos()

        if confirmar("Arquivar resultados em experimentos/?"):
            nome = input(c("  Nome descritivo do experimento: ", Cor.CYAN)).strip()
            if not nome:
                nome = nome_lote
            arquivar_resultados(nome)
    else:
        print(c("  [!] Nenhum JSON gerado — nada a arquivar.", Cor.YELLOW))

# ─── Opção: Experimento Customizado ───────────────────────────────────────────
ATAQUES = [
    "targeted_backdoor", "trigger_patch", "label_flipping",
    "gaussian_noise", "gradient_ascent", "model_replacement", "free_rider"
]
DEFESAS = ["FedAvg", "FedMedian", "Krum", "Bulyan"]

def menu_customizado():
    """Interface interativa para configurar experimentos personalizados com múltiplas repetições."""
    cabecalho("Configurar Experimento Personalizado")

    params_base = {}

    # Defesa
    print(c("\n  Estratégia de Defesa:", Cor.CYAN))
    for i, d in enumerate(DEFESAS, 1):
        print(f"    [{i}] {d}")
    while True:
        try:
            idx = int(input(c("  Escolha [1-4]: ", Cor.YELLOW))) - 1
            if 0 <= idx < len(DEFESAS):
                params_base["defense_mode"] = DEFESAS[idx]
                break
        except ValueError:
            pass
        print(c("  Opção inválida.", Cor.RED))

    # Ataque
    print(c("\n  Tipo de Ataque:", Cor.CYAN))
    for i, a in enumerate(ATAQUES, 1):
        print(f"    [{i}] {a}")
    while True:
        try:
            idx = int(input(c(f"  Escolha [1-{len(ATAQUES)}]: ", Cor.YELLOW))) - 1
            if 0 <= idx < len(ATAQUES):
                params_base["attack_type"] = ATAQUES[idx]
                break
        except ValueError:
            pass
        print(c("  Opção inválida.", Cor.RED))

    # poison_rate
    while True:
        try:
            val = float(input(c("  Taxa de envenenamento (poison_rate) [0.0 a 1.0, padrão 0.4]: ", Cor.YELLOW)) or "0.4")
            if 0.0 <= val <= 1.0:
                params_base["poison_rate"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # dirichlet_alpha
    while True:
        try:
            val = float(input(c("  Dirichlet Alpha (Heterogeneidade) [0.1=Non-IID extremo, 100.0=IID, padrão 0.1]: ", Cor.YELLOW)) or "0.1")
            if val > 0:
                params_base["dirichlet_alpha"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # num-server-rounds
    while True:
        try:
            val = int(input(c("  Número de rodadas (num-server-rounds) [padrão 10]: ", Cor.YELLOW)) or "10")
            if val > 0:
                params_base["num-server-rounds"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # Quantidade de repetições (Trials / Seeds)
    while True:
        try:
            trials_count = int(input(c("  Quantas repetições estatísticas (seeds)? [1 para único, 3 ou 5 para média, padrão 1]: ", Cor.YELLOW)) or "1")
            if trials_count >= 1:
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # Monta a lista de execuções com seeds incrementais (42, 43, 44...)
    runs = []
    base_seed = 42
    for i in range(trials_count):
        p = params_base.copy()
        p["seed"] = base_seed + i
        runs.append(p)

    print()
    separador("─", 70)
    print(c(f"  Configuração Pronta ({trials_count} execuções programadas):", Cor.BOLD))
    for k, v in params_base.items():
        print(f"    {c(k, Cor.CYAN)}: {c(str(v), Cor.YELLOW)}")
    if trials_count > 1:
        print(f"    {c('Seeds programadas', Cor.CYAN)}: {c(str([base_seed + i for i in range(trials_count)]), Cor.YELLOW)}")
    separador("─", 70)

    executar_lote(runs, "experimento_customizado")

# ─── Opção: Ver Experimentos Salvos ───────────────────────────────────────────
def ver_experimentos():
    cabecalho("Histórico de Experimentos Salvos")
    pastas = sorted([p for p in EXPERIMENTOS.iterdir() if p.is_dir()])
    if not pastas:
        print(c("  Nenhum experimento arquivado em experimentos/ ainda.", Cor.GRAY))
        return
    for pasta in pastas:
        dados    = list((pasta / "dados").glob("*.json"))    if (pasta / "dados").exists()    else []
        graficos = list((pasta / "graficos").glob("*.png"))  if (pasta / "graficos").exists() else []
        print(f"\n  {c(pasta.name, Cor.BOLD)}")
        print(f"    {c(str(len(dados)), Cor.CYAN)} JSON(s) de métricas  |  {c(str(len(graficos)), Cor.CYAN)} Figuras PNG")

# ─── Menu Principal ───────────────────────────────────────────────────────────
def menu_principal():
    os.system("cls" if os.name == "nt" else "clear")
    separador("═", 70)
    print(c("       LABORATÓRIO DE SEGURANÇA FEDERADA (FLOWER + PYTORCH)", Cor.BOLD + Cor.CYAN))
    print(c("       Estudo Empírico de Ataques Furtivos & Avaliação de Defesas", Cor.GRAY))
    separador("═", 70)

    print(c("\n  🔬 Lotes Pré-Definidos do Artigo 1:", Cor.BOLD))
    for chave, lote in LOTES.items():
        total = len(lote["runs"])
        print(f"    [{c(chave, Cor.YELLOW)}] {lote['nome']}")
        print(c(f"        {lote['descricao']} ({total} execuções)", Cor.GRAY))

    print(c("\n  ⚙️  Opções Avançadas:", Cor.BOLD))
    print(f"    [{c('6', Cor.YELLOW)}] Configurar Experimento Personalizado (com N repetições)")
    print(f"    [{c('7', Cor.YELLOW)}] Ver Histórico de Experimentos Arquivados")
    print(f"    [{c('8', Cor.YELLOW)}] Re-gerar Gráficos e Tabelas dos Resultados Atuais")
    print(f"    [{c('0', Cor.YELLOW)}] Sair")

    separador("─", 70)
    return input(c("  Escolha uma opção: ", Cor.YELLOW)).strip()

# ─── Entry Point ──────────────────────────────────────────────────────────────
def main():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    EXPERIMENTOS.mkdir(exist_ok=True)

    while True:
        escolha = menu_principal()

        if escolha in LOTES:
            lote = LOTES[escolha]
            cabecalho(lote["nome"])
            print(c(f"  {lote['descricao']}", Cor.GRAY))
            executar_lote(lote["runs"], lote["nome"])

        elif escolha == "6":
            menu_customizado()

        elif escolha == "7":
            ver_experimentos()

        elif escolha == "8":
            gerar_graficos()

        elif escolha == "0":
            print(c("\n  Encerrando laboratório. Até logo!\n", Cor.CYAN))
            break

        else:
            print(c("  Opção inválida.", Cor.RED))

        input(c("\n  Pressione Enter para voltar ao menu principal...", Cor.GRAY))

if __name__ == "__main__":
    main()

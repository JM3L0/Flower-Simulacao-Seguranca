"""
laboratorio.py — Interface interativa para o Laboratório de Segurança Federada.

Execute na RAIZ do projeto:
    python laboratorio.py

O script cuida de:
  - Configurar PYTHONIOENCODING=utf-8 automaticamente
  - Executar cada flwr run . --stream dentro de quickstart-pytorch/
  - Fazer ray stop + pausa entre execuções para evitar travamentos
  - Gerar gráficos automaticamente após cada lote
  - Arquivar os resultados em experimentos/ com nome descritivo
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─── Caminhos do projeto ──────────────────────────────────────────────────────
RAIZ        = Path(__file__).parent
SRC         = RAIZ / "quickstart-pytorch"
METRICS_DIR = SRC / "metrics_json"
GRAFICOS_DIR= SRC / "graficos"
EXPERIMENTOS= RAIZ / "experimentos"

# ─── Paleta de cores ANSI ─────────────────────────────────────────────────────
class Cor:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"

def c(texto, cor): return f"{cor}{texto}{Cor.RESET}"

# ─── Lotes pré-definidos ──────────────────────────────────────────────────────
LOTES = {
    "1": {
        "nome": "Comparar estratégias de defesa",
        "descricao": "FedAvg vs FedMedian vs Bulyan — mesmo ataque e poison_rate",
        "runs": [
            {"defense_mode": "FedAvg",    "attack_type": "gaussian_noise", "poison_rate": 0.3},
            {"defense_mode": "FedMedian", "attack_type": "gaussian_noise", "poison_rate": 0.3},
            {"defense_mode": "Bulyan",    "attack_type": "gaussian_noise", "poison_rate": 0.3},
            {"defense_mode": "Krum",      "attack_type": "gaussian_noise", "poison_rate": 0.3},
        ],
    },
    "2": {
        "nome": "Variar poison_rate (curva de colapso)",
        "descricao": "FedAvg com label_flipping, poison_rate de 0.0 a 0.9",
        "runs": [
            {"defense_mode": "FedAvg", "attack_type": "label_flipping", "poison_rate": pr}
            for pr in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]
        ],
    },
    "3": {
        "nome": "Variar heterogeneidade (Dirichlet Alpha)",
        "descricao": "Bulyan com model_replacement, dirichlet_alpha de IID a non-IID extremo",
        "runs": [
            {"defense_mode": "Bulyan", "attack_type": "model_replacement",
             "poison_rate": 1.0, "dirichlet_alpha": da}
            for da in [100.0, 10.0, 1.0, 0.5, 0.1]
        ],
    },
    "4": {
        "nome": "Matriz completa 3×5 (defesas × poison_rates)",
        "descricao": "FedAvg, FedMedian, Bulyan × poison_rate 0.0→0.9 com gaussian_noise",
        "runs": [
            {"defense_mode": d, "attack_type": "gaussian_noise", "poison_rate": pr}
            for d in ["FedAvg", "FedMedian", "Bulyan"]
            for pr in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]
        ],
    },
    "5": {
        "nome": "Morte Súbita — gradient_ascent vs defesas",
        "descricao": "Testa o ataque mais destrutivo contra FedAvg, FedMedian e Bulyan",
        "runs": [
            {"defense_mode": d, "attack_type": "gradient_ascent", "poison_rate": 1.0}
            for d in ["FedAvg", "FedMedian", "Bulyan"]
        ],
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def separador(char="═", largura=62):
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
    print(c(f"     {run_config}", Cor.GRAY))
    separador("─")

    # Monta o comando completo
    cmd = f'flwr run . --stream --run-config "{run_config}"'

    # Configura ambiente com encoding UTF-8
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

    # Limpa Ray entre execuções para evitar travamentos
    if numero < total:
        print(c("\n  → Limpando processos Ray...", Cor.GRAY))
        subprocess.run("ray stop", shell=True, cwd=str(SRC),
                       capture_output=True, env=env)
        import time; time.sleep(4)

    return sucesso

def gerar_graficos():
    """Executa plotar_resultados.py dentro de quickstart-pytorch/."""
    print()
    print(c("  → Gerando gráficos...", Cor.CYAN))
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    resultado = subprocess.run(
        f"{sys.executable} plotar_resultados.py",
        shell=True,
        cwd=str(SRC),
        env=env,
    )
    if resultado.returncode == 0:
        print(c("  ✔  Gráficos gerados.", Cor.GREEN))
    else:
        print(c("  ✘  Erro ao gerar gráficos.", Cor.RED))

def arquivar_resultados(nome_descritivo: str):
    """Move JSONs e PNGs para experimentos/expXX_nome/."""
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

    # Mover PNGs
    pngs = list(GRAFICOS_DIR.glob("*.png"))
    for f in pngs:
        shutil.move(str(f), str(graficos_dir / f.name))

    print()
    print(c(f"  ✔  Arquivado em: experimentos/{pasta.name}/", Cor.GREEN))
    print(c(f"     {len(jsons)} JSON(s) → dados/", Cor.GRAY))
    print(c(f"     {len(pngs)} PNG(s)  → graficos/", Cor.GRAY))
    return pasta

def confirmar(mensagem: str) -> bool:
    resp = input(c(f"\n  {mensagem} [s/N]: ", Cor.YELLOW)).strip().lower()
    return resp in ("s", "sim", "y", "yes")

# ─── Fluxo de execução de um lote ─────────────────────────────────────────────
def executar_lote(runs: list[dict], nome_lote: str):
    """Executa uma lista de runs e arquiva os resultados."""
    total = len(runs)
    print()
    print(c(f"  Total de execuções: {total}", Cor.CYAN))

    # Limpa resultados antigos se existirem
    jsons_anteriores = list(METRICS_DIR.glob("metrics_*.json"))
    if jsons_anteriores:
        print(c(f"\n  [!] Existem {len(jsons_anteriores)} JSON(s) anteriores em metrics_json/.", Cor.YELLOW))
        if confirmar("Limpar antes de começar?"):
            for f in jsons_anteriores:
                f.unlink()
            list(GRAFICOS_DIR.glob("*.png")) and [f.unlink() for f in GRAFICOS_DIR.glob("*.png")]
            print(c("  → Resultados anteriores removidos.", Cor.GRAY))

    if not confirmar("Iniciar execuções agora?"):
        print(c("  Cancelado.", Cor.GRAY))
        return

    print()
    sucessos = 0
    for i, params in enumerate(runs, start=1):
        ok = executar_run(params, i, total)
        if ok:
            sucessos += 1

    # Resumo
    separador()
    print(c(f"  Concluído: {sucessos}/{total} execuções bem-sucedidas.", Cor.GREEN if sucessos == total else Cor.YELLOW))

    # Gerar gráficos
    jsons_gerados = list(METRICS_DIR.glob("metrics_*.json"))
    if jsons_gerados:
        if confirmar("Gerar gráficos comparativos?"):
            gerar_graficos()

        # Arquivar
        if confirmar("Arquivar resultados em experimentos/?"):
            nome = input(c("  Nome descritivo do experimento: ", Cor.CYAN)).strip()
            if not nome:
                nome = nome_lote
            arquivar_resultados(nome)
    else:
        print(c("  [!] Nenhum JSON gerado — nada a arquivar.", Cor.YELLOW))

# ─── Opção: Experimento Customizado ───────────────────────────────────────────
ATAQUES  = ["label_flipping", "gaussian_noise", "targeted_backdoor",
            "trigger_patch", "gradient_ascent", "model_replacement", "free_rider"]
DEFESAS  = ["FedAvg", "FedMedian", "Bulyan", "Krum"]

def menu_customizado():
    """Interface para configurar um experimento com parâmetros manuais."""
    cabecalho("Experimento Customizado")

    params = {}

    # Defesa
    print(c("\n  Estratégia de defesa:", Cor.CYAN))
    for i, d in enumerate(DEFESAS, 1):
        print(f"    [{i}] {d}")
    while True:
        try:
            idx = int(input(c("  Escolha [1-4]: ", Cor.YELLOW))) - 1
            if 0 <= idx < len(DEFESAS):
                params["defense_mode"] = DEFESAS[idx]
                break
        except ValueError:
            pass
        print(c("  Opção inválida.", Cor.RED))

    # Ataque
    print(c("\n  Tipo de ataque:", Cor.CYAN))
    for i, a in enumerate(ATAQUES, 1):
        print(f"    [{i}] {a}")
    while True:
        try:
            idx = int(input(c(f"  Escolha [1-{len(ATAQUES)}]: ", Cor.YELLOW))) - 1
            if 0 <= idx < len(ATAQUES):
                params["attack_type"] = ATAQUES[idx]
                break
        except ValueError:
            pass
        print(c("  Opção inválida.", Cor.RED))

    # poison_rate
    while True:
        try:
            val = float(input(c("  poison_rate [0.0 a 1.0, padrão 0.2]: ", Cor.YELLOW)) or "0.2")
            if 0.0 <= val <= 1.0:
                params["poison_rate"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # dirichlet_alpha
    while True:
        try:
            val = float(input(c("  dirichlet_alpha [ex: 0.1 non-IID / 1.0 moderado / 100.0 IID, padrão 1.0]: ", Cor.YELLOW)) or "1.0")
            if val > 0:
                params["dirichlet_alpha"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # num-server-rounds
    while True:
        try:
            val = int(input(c("  num-server-rounds [padrão 5]: ", Cor.YELLOW)) or "5")
            if val > 0:
                params["num-server-rounds"] = val
                break
        except ValueError:
            pass
        print(c("  Valor inválido.", Cor.RED))

    # Resumo
    print()
    separador("─")
    print(c("  Configuração:", Cor.BOLD))
    for k, v in params.items():
        print(f"    {c(k, Cor.CYAN)}: {c(str(v), Cor.YELLOW)}")
    separador("─")

    executar_lote([params], "experimento_customizado")

# ─── Opção: Ver experimentos salvos ───────────────────────────────────────────
def ver_experimentos():
    cabecalho("Experimentos Salvos")
    pastas = sorted([p for p in EXPERIMENTOS.iterdir() if p.is_dir()])
    if not pastas:
        print(c("  Nenhum experimento arquivado ainda.", Cor.GRAY))
        return
    for pasta in pastas:
        dados    = list((pasta / "dados").glob("*.json"))    if (pasta / "dados").exists()    else []
        graficos = list((pasta / "graficos").glob("*.png"))  if (pasta / "graficos").exists() else []
        print(f"\n  {c(pasta.name, Cor.BOLD)}")
        print(f"    {c(str(len(dados)), Cor.CYAN)} JSON(s)  |  {c(str(len(graficos)), Cor.CYAN)} PNG(s)")

# ─── Menu principal ───────────────────────────────────────────────────────────
def menu_principal():
    os.system("cls" if os.name == "nt" else "clear")
    separador("═")
    print(c("       LABORATÓRIO DE SEGURANÇA FEDERADA", Cor.BOLD + Cor.CYAN))
    print(c("       Flower + PyTorch + CIFAR-10", Cor.GRAY))
    separador("═")

    print(c("\n  Lotes pré-definidos:", Cor.BOLD))
    for chave, lote in LOTES.items():
        total = len(lote["runs"])
        print(f"    [{c(chave, Cor.YELLOW)}] {lote['nome']}")
        print(c(f"        {lote['descricao']} ({total} execuções)", Cor.GRAY))

    print(c("\n  Outras opções:", Cor.BOLD))
    print(f"    [{c('6', Cor.YELLOW)}] Experimento customizado")
    print(f"    [{c('7', Cor.YELLOW)}] Ver experimentos salvos")
    print(f"    [{c('0', Cor.YELLOW)}] Sair")

    separador("─")
    return input(c("  Escolha: ", Cor.YELLOW)).strip()

# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    # Garante que os diretórios necessários existem
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

        elif escolha == "0":
            print(c("\n  Saindo. Até logo!\n", Cor.CYAN))
            break

        else:
            print(c("  Opção inválida.", Cor.RED))

        input(c("\n  Pressione Enter para voltar ao menu...", Cor.GRAY))

if __name__ == "__main__":
    main()

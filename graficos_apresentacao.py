"""Gráficos da apresentação (vídeo). Rode depois de `python analise.py`:

    python graficos_apresentacao.py

Lê dados/limpos/*.csv e resultados/numeros.json e salva figuras/slide_*.png.
Nenhum número aqui é digitado à mão: tudo vem dos arquivos gerados pela análise.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
from statsmodels.stats.power import TTestPower

RAIZ = pathlib.Path(__file__).parent
FIG = RAIZ / "figuras"
N = json.loads((RAIZ / "resultados" / "numeros.json").read_text(encoding="utf-8"))
tarefas = pd.read_csv(RAIZ / "dados" / "limpos" / "tarefas_limpas.csv")
devs = pd.read_csv(RAIZ / "dados" / "limpos" / "medias_por_desenvolvedor.csv")

COR_IA, COR_SEM, CINZA, TINTA = "#2a78d6", "#eb6834", "#6b7280", "#1f2430"
DPI = 150
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.edgecolor": "#9aa0a6",
                     "axes.linewidth": 0.8, "xtick.color": "#3d4451", "ytick.color": "#3d4451",
                     "axes.labelcolor": TINTA, "text.color": TINTA})


def br(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def pct(r):
    v = 100 * (r - 1)
    return ("+" if v >= 0 else "−") + br(abs(v)) + "%"


def limpar(ax):
    ax.spines[["top", "right"]].set_visible(False)


# ---------------------------------------------------------------- 1. distribuição
def distribuicao():
    fig, axes = plt.subplots(2, 1, figsize=(1000 / DPI, 640 / DPI), sharex=True)
    bins = np.logspace(np.log10(2), np.log10(700), 22)
    for ax, (cond, cor) in zip(axes, [("Sem IA", COR_SEM), ("Com IA", COR_IA)]):
        t = tarefas.loc[tarefas.condicao == cond, "initial_implementation_time"]
        ax.hist(t, bins=bins, color=cor, alpha=0.85, edgecolor="white", linewidth=0.8)
        med = t.median()
        ax.axvline(med, color=TINTA, lw=1.5, ls="--")
        ax.text(med * 1.06, ax.get_ylim()[1] * 0.85, f"mediana {br(med, 0)} min", fontsize=12,
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 2, "alpha": 0.9})
        ax.set_ylabel("tarefas")
        ax.set_title(f"{cond} (n = {len(t)})", loc="left", fontsize=13, color=TINTA)
        limpar(ax)
    axes[1].set_xscale("log")
    ticks = [5, 10, 30, 60, 120, 300, 600]
    axes[1].xaxis.set_major_locator(FixedLocator(ticks))
    axes[1].xaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    axes[1].set_xlabel("minutos até abrir o pull request (escala log)")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "slide_distribuicao.png", dpi=DPI)
    plt.close(fig)


# ---------------------------------------------------------------- 2. os 16 devs
def forest():
    d = devs.sort_values("razao").reset_index(drop=True)
    C = N["confirmatoria"]
    fig, ax = plt.subplots(figsize=(1664 / DPI, 720 / DPI))
    ys = np.arange(len(d))[::-1] + 2
    for y, (_, r) in zip(ys, d.iterrows()):
        lento = r["razao"] > 1
        ax.plot([1, r["razao"]], [y, y], color="#d0d4da", lw=1.2, zorder=1)
        ax.scatter(r["razao"], y, s=70, color=TINTA if lento else COR_IA, zorder=3,
                   marker="o" if lento else "s")
        ax.text(7.2, y, f"×{br(r['razao'], 2)}", va="center", fontsize=12, color=CINZA)
    ax.set_yticks(list(ys) + [0])
    ax.set_yticklabels([f"Dev {int(r.dev_id)}  ({int(r.n_sem_ia)} sem / {int(r.n_com_ia)} com)" for _, r in d.iterrows()]
                       + ["Média dos 16 (IC 95%)"], fontsize=11.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    lo, hi = C["ic_razao"]
    ax.plot([lo, hi], [0, 0], color=COR_IA, lw=4, solid_capstyle="butt")
    ax.scatter(C["razao"], 0, s=200, marker="D", color=COR_IA, zorder=4)
    ax.text(7.2, 0, f"×{br(C['razao'], 2)}", va="center", fontsize=12, color=COR_IA, fontweight="bold")
    ax.axvline(1, color=TINTA, lw=1.2)
    ax.axhline(1, color="#e5e7eb", lw=1)
    ax.set_xscale("log")
    ticks = [0.25, 0.5, 1, 2, 4]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter(["0,25", "0,5", "1", "2", "4"]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(0.25, 9)
    ax.set_ylim(-1, len(d) + 2.6)
    ax.set_xlabel("tempo com IA ÷ tempo sem IA (média geométrica de cada dev; escala log)")
    ax.text(0.97, len(d) + 2.0, "← mais rápido com IA", ha="right", fontsize=12, color=COR_IA)
    ax.text(1.03, len(d) + 2.0, "mais lento com IA →", ha="left", fontsize=12, color=TINTA)
    limpar(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "slide_16devs.png", dpi=DPI)
    plt.close(fig)


# ---------------------------------------------------------------- 3. análises comparadas
def comparacao():
    C, E = N["confirmatoria"], N["exploratorias"]
    linhas = [
        ("Previsão dos devs, antes do sorteio", E["previsao"], None, CINZA),
        ("Análise dos autores (tempo total, regressão)", 1 + E["reg_efeito"], (1 + E["reg_ic"][0], 1 + E["reg_ic"][1]), CINZA),
        ("Por tarefa, sem parear (Welch, exploratória)", E["welch_razao"], tuple(E["welch_ic"]), CINZA),
        ("Nossa análise: pareada por dev (confirmatória)", C["razao"], tuple(C["ic_razao"]), COR_IA),
    ]
    fig, ax = plt.subplots(figsize=(1664 / DPI, 560 / DPI))
    ax.axvspan(-60, 0, color="#eef4fc", zorder=0)
    ax.axvline(0, color=TINTA, lw=1.2)
    for i, (rot, r, ic, cor) in enumerate(linhas):
        x = 100 * (r - 1)
        if ic:
            ax.plot([100 * (ic[0] - 1), 100 * (ic[1] - 1)], [i, i], color=cor, lw=4, solid_capstyle="butt")
            txt = f"{pct(r)}   (IC {pct(ic[0])} a {pct(ic[1])})"
            ax.scatter(x, i, s=160, color=cor, zorder=3)
        else:
            txt = f"{pct(r)}   (o que eles esperavam)"
            ax.scatter(x, i, s=160, facecolor="white", edgecolor=cor, linewidth=2.5, zorder=3)
        ax.text(1.5, i + 0.3, txt, ha="left", fontsize=12, color=TINTA if cor == CINZA else cor,
                fontweight="bold" if cor == COR_IA else "normal")
    ax.set_yticks(range(len(linhas)))
    ax.set_yticklabels([l[0] for l in linhas], fontsize=12.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlim(-45, 95)
    ax.set_ylim(-0.6, len(linhas) - 0.2)
    ax.set_xlabel("variação do tempo com IA permitida (%)")
    ax.text(-43, -0.5, "IA mais rápida", fontsize=12, color=COR_IA)
    ax.text(93, -0.5, "IA mais lenta", fontsize=12, color=TINTA, ha="right")
    limpar(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "slide_comparacao.png", dpi=DPI)
    plt.close(fig)


# ---------------------------------------------------------------- 4. poder
def poder():
    P = N["planejamento"]
    ns = np.arange(4, 81)
    pw = [TTestPower().power(effect_size=P["dz_alvo"], nobs=n, alpha=0.05, alternative="larger") for n in ns]
    fig, ax = plt.subplots(figsize=(900 / DPI, 560 / DPI))
    ax.plot(ns, pw, color=COR_IA, lw=2.5)
    ax.axhline(0.8, color=CINZA, lw=1, ls="--")
    for n, cor, rot in ((N["confirmatoria"]["n"], TINTA, "nosso estudo"), (P["n_necessario"], COR_IA, "estudo completo")):
        p_n = TTestPower().power(effect_size=P["dz_alvo"], nobs=n, alpha=0.05, alternative="larger")
        ax.scatter(n, p_n, s=90, color=cor, zorder=3)
        ax.annotate(f"{rot}\n{n} devs → poder {br(p_n, 2)}", (n, p_n), xytext=(10, -46 if n < 30 else -52),
                    textcoords="offset points", fontsize=12, color=cor)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 80)
    ax.set_xlabel("número de desenvolvedores")
    ax.set_ylabel("poder (chance de detectar)")
    ax.set_title("Detectar uma redução de 20% no tempo (α = 0,05)", loc="left", fontsize=13)
    ax.yaxis.set_major_locator(FixedLocator([0, 0.2, 0.4, 0.6, 0.8, 1]))
    ax.yaxis.set_major_formatter(FixedFormatter(["0", "0,2", "0,4", "0,6", "0,8", "1"]))
    limpar(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "slide_poder.png", dpi=DPI)
    plt.close(fig)


# ---------------------------------------------------------------- 5. pergunta 2 (4 grupos)
def kgrupos():
    g4 = pd.read_csv(RAIZ / "dados" / "limpos" / "tarefas_4grupos.csv")
    p2 = N["pergunta2"]
    ordem = [("Curta sem IA", COR_SEM), ("Curta com IA", COR_IA), ("Longa sem IA", COR_SEM), ("Longa com IA", COR_IA)]
    fig, ax = plt.subplots(figsize=(1000 / DPI, 560 / DPI))
    rng = np.random.default_rng(2026)
    for i, (g, cor) in enumerate(ordem):
        r = np.exp(g4.loc[g4.grupo == g, "log_razao"])
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(r)), r, s=10, color=cor, alpha=0.45, linewidths=0)
        mg = np.exp(np.log(r).mean())
        ax.plot([i - 0.28, i + 0.28], [mg, mg], color=TINTA, lw=2.2)
        ax.text(i + 0.31, mg, br(mg, 2), va="center", fontsize=11)
    ax.axhline(1, color=CINZA, lw=0.8, ls=":")
    ax.set_yscale("log")
    ticks = [0.1, 0.25, 0.5, 1, 2, 4, 8]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FixedFormatter([br(t, 2).rstrip("0").rstrip(",") for t in ticks]))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(4), [f"{g}\n(n ={p2['n'][g]})" for g, _ in ordem])
    ax.set_ylabel("tempo real ÷ previsto sem IA (log)")
    ax.set_title(f"ANOVA: F({p2['anova_gl'][0]}, {p2['anova_gl'][1]}) = {br(p2['anova_F'], 2)}, "
                 f"p = {br(p2['anova_p'], 3)}; Kruskal-Wallis p = {br(p2['kruskal_p'], 3)}", loc="left", fontsize=12)
    limpar(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "slide_kgrupos.png", dpi=DPI)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    distribuicao()
    forest()
    comparacao()
    poder()
    kgrupos()
    print("Gráficos salvos em figuras/slide_*.png")

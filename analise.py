"""Análise do Projeto Final MCEQ 12576 – IA × tempo de implementação (base METR).

Vai dos dados brutos aos números e figuras do artigo. Executar depois de
`python baixar_dados.py`:

    python analise.py

Saídas: dados/limpos/*.csv, resultados/resultados.txt, resultados/*.csv,
figuras/figura1.png. Não há sorteio na análise; a semente fica fixada mesmo
assim, por padrão da disciplina.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.power import TTestPower

RAIZ = pathlib.Path(__file__).parent
BRUTO = RAIZ / "dados" / "brutos" / "data_complete.csv"
LIMPOS = RAIZ / "dados" / "limpos"
RES = RAIZ / "resultados"
FIG = RAIZ / "figuras"
ALFA = 0.05
rng = np.random.default_rng(2026)  # semente fixa (não usada: análise determinística)

COR_IA, COR_SEM = "#2a78d6", "#eb6834"  # paleta validada (CVD-safe)
linhas_saida: list[str] = []


def out(texto: str = "") -> None:
    print(texto)
    linhas_saida.append(texto)


# ---------------------------------------------------------------- 1. limpeza
def carregar_e_limpar() -> pd.DataFrame:
    df = pd.read_csv(BRUTO)
    n0 = len(df)
    df["ai_treatment"] = df["ai_treatment"].astype(int)
    df["dev_id"] = df["dev_id"].astype(int)
    df["condicao"] = df["ai_treatment"].map({1: "Com IA", 0: "Sem IA"})
    # Regras de exclusão definidas antes: tempo ausente ou <= 0 (log indefinido).
    validos = df["initial_implementation_time"].notna() & (df["initial_implementation_time"] > 0)
    excluidas = int((~validos).sum())
    df = df[validos].copy()
    df["log_t"] = np.log(df["initial_implementation_time"])
    LIMPOS.mkdir(parents=True, exist_ok=True)
    df.to_csv(LIMPOS / "tarefas_limpas.csv", index=False)
    out(f"Tarefas no arquivo bruto: {n0}; excluídas pela regra prévia: {excluidas}; analisadas: {len(df)}")
    out(f"Desenvolvedores: {df.dev_id.nunique()}")
    return df


# ------------------------------------------------------------ 2. descritiva
def descritiva(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for cond, g in df.groupby("condicao"):
        t = g["initial_implementation_time"]
        q1, q3 = t.quantile([0.25, 0.75])
        linhas.append(
            {
                "condicao": cond,
                "n_tarefas": len(t),
                "media_min": t.mean(),
                "mediana_min": t.median(),
                "dp_min": t.std(ddof=1),
                "q1_min": q1,
                "q3_min": q3,
                "iqr_min": q3 - q1,
                "cv_pct": 100 * t.std(ddof=1) / t.mean(),
                "assimetria_g1": stats.skew(t, bias=True),
                "media_geom_min": float(np.exp(g["log_t"].mean())),
                "outliers_iqr": int(((t < q1 - 1.5 * (q3 - q1)) | (t > q3 + 1.5 * (q3 - q1))).sum()),
            }
        )
    tab = pd.DataFrame(linhas).set_index("condicao")
    tab.round(2).to_csv(RES / "descritiva.csv")
    out("\n== Estatística descritiva (tempo de implementação inicial, min) ==")
    out(tab.round(2).T.to_string())
    return tab


# ------------------------------------------- 3. análise confirmatória (protocolo)
def por_desenvolvedor(df: pd.DataFrame) -> pd.DataFrame:
    m = df.groupby(["dev_id", "ai_treatment"])["log_t"].mean().unstack()
    m.columns = ["log_sem_ia", "log_com_ia"]  # 0 -> sem, 1 -> com
    n = df.groupby(["dev_id", "ai_treatment"]).size().unstack()
    m["n_sem_ia"], m["n_com_ia"] = n[0], n[1]
    m["d"] = m["log_com_ia"] - m["log_sem_ia"]
    m["razao"] = np.exp(m["d"])
    m.to_csv(LIMPOS / "medias_por_desenvolvedor.csv")
    return m


def confirmatoria(m: pd.DataFrame) -> dict:
    d = m["d"].to_numpy()
    n = len(d)
    out("\n== Análise CONFIRMATÓRIA (planejada no protocolo) ==")
    out(f"Blocos (desenvolvedores) n = {n}; tarefas por dev e condição: min {int(m[['n_sem_ia','n_com_ia']].min().min())}, máx {int(m[['n_sem_ia','n_com_ia']].max().max())}")
    sh = stats.shapiro(d)
    out(f"Shapiro-Wilk em d: W = {sh.statistic:.3f}, p = {sh.pvalue:.3f}")
    usa_wilcoxon = sh.pvalue < ALFA
    t_uni = stats.ttest_rel(m["log_com_ia"], m["log_sem_ia"], alternative="less")
    # IC 95% bilateral da média de d (previsto no protocolo)
    ic = stats.ttest_rel(m["log_com_ia"], m["log_sem_ia"]).confidence_interval(0.95)
    dz = d.mean() / d.std(ddof=1)
    w = stats.wilcoxon(m["log_com_ia"], m["log_sem_ia"], alternative="less")
    devs_mais_lentos = int((d > 0).sum())
    res = {
        "n": n,
        "media_d": d.mean(),
        "dp_d": d.std(ddof=1),
        "t": t_uni.statistic,
        "gl": t_uni.df,
        "p_uni": t_uni.pvalue,
        "ic_log": (ic.low, ic.high),
        "razao": np.exp(d.mean()),
        "ic_razao": (np.exp(ic.low), np.exp(ic.high)),
        "dz": dz,
        "shapiro_W": sh.statistic,
        "shapiro_p": sh.pvalue,
        "wilcoxon_W": w.statistic,
        "wilcoxon_p": w.pvalue,
        "devs_mais_lentos": devs_mais_lentos,
        "usa_wilcoxon": usa_wilcoxon,
    }
    out(f"Média de d (log IA − log sem IA) = {d.mean():.3f} (dp = {d.std(ddof=1):.3f})")
    out(f"Teste t pareado unilateral (H1: µ_d < 0): t({t_uni.df:.0f}) = {t_uni.statistic:.3f}, p = {t_uni.pvalue:.3f}")
    out(f"Razão de médias geométricas IA/sem IA = {res['razao']:.3f} "
        f"(IC 95% bilateral: [{res['ic_razao'][0]:.3f}; {res['ic_razao'][1]:.3f}])")
    out(f"  -> variação percentual: {100*(res['razao']-1):+.1f}% "
        f"(IC 95%: [{100*(res['ic_razao'][0]-1):+.1f}%; {100*(res['ic_razao'][1]-1):+.1f}%])")
    out(f"Tamanho de efeito d_z (Cohen, pareado) = {dz:.3f}")
    out(f"Desenvolvedores mais lentos com IA (d > 0): {devs_mais_lentos} de {n}")
    regra = "Wilcoxon (normalidade rejeitada)" if usa_wilcoxon else "teste t pareado (normalidade não rejeitada)"
    out(f"Teste usado na decisão, pela regra do protocolo: {regra}")
    out(f"Wilcoxon unilateral (só seria o principal se Shapiro p < α): W = {w.statistic:.1f}, p = {w.pvalue:.3f}")
    p_dec = w.pvalue if usa_wilcoxon else t_uni.pvalue
    out(f"Decisão com α = {ALFA}: {'rejeita H0' if p_dec <= ALFA else 'NÃO rejeita H0'} (p = {p_dec:.3f})")
    return res


# ------------------------------------------------- 4. análises exploratórias
def exploratorias(df: pd.DataFrame) -> dict:
    out("\n== Análises EXPLORATÓRIAS (não planejadas como confirmatórias) ==")
    ia = df.loc[df.ai_treatment == 1, "log_t"]
    sem = df.loc[df.ai_treatment == 0, "log_t"]
    # E1: Welch no nível da tarefa, ignorando o bloco (comparação didática – Aula 07)
    w = stats.ttest_ind(ia, sem, equal_var=False, alternative="less")
    w_bi = stats.ttest_ind(ia, sem, equal_var=False)
    ic = w_bi.confidence_interval(0.95)
    n1, n2 = len(ia), len(sem)
    sp = np.sqrt(((n1 - 1) * ia.var(ddof=1) + (n2 - 1) * sem.var(ddof=1)) / (n1 + n2 - 2))
    d_cohen = (ia.mean() - sem.mean()) / sp
    out(f"E1 – Welch por tarefa (log): t = {w.statistic:.3f}, gl = {w.df:.1f}, p_uni = {w.pvalue:.3f}; "
        f"razão = {np.exp(ia.mean()-sem.mean()):.3f} [IC95% {np.exp(ic.low):.3f}; {np.exp(ic.high):.3f}]; d de Cohen = {d_cohen:.3f}")
    # E2: tempo total com a imputação e a regressão dos autores (replicação)
    d2 = df.copy()
    medias_rev = d2.groupby("ai_treatment")["post_review_implementation_time"].mean()
    faltantes = int(d2["post_review_implementation_time"].isna().sum())
    d2["post_review_implementation_time"] = d2["post_review_implementation_time"].fillna(
        d2["ai_treatment"].map(medias_rev)
    )
    d2["log_total"] = np.log(d2["initial_implementation_time"] + d2["post_review_implementation_time"])
    d2["log_prev"] = np.log(d2["predicted_time_no_ai"])
    reg = smf.ols("log_total ~ ai_treatment + log_prev", data=d2).fit()
    b, se = reg.params["ai_treatment"], reg.bse["ai_treatment"]
    z = stats.norm.ppf(0.975)
    out(f"E2 – Replicação da regressão dos autores (tempo total; {faltantes} revisões imputadas): "
        f"efeito = {np.exp(b)-1:+.3f} [IC95% {np.exp(b-z*se)-1:+.3f}; {np.exp(b+z*se)-1:+.3f}]")
    # E3: previsão dos desenvolvedores antes do sorteio
    prev = np.exp(np.mean(np.log(df["predicted_time_ai_allowed"]) - np.log(df["predicted_time_no_ai"])))
    out(f"E3 – Previsão prévia dos devs (média geométrica IA/sem IA): {prev:.3f} ({100*(prev-1):+.1f}%)")
    return {"welch_p": w.pvalue, "welch_t": w.statistic, "welch_gl": w.df,
            "welch_razao": float(np.exp(ia.mean() - sem.mean())),
            "welch_ic": (float(np.exp(ic.low)), float(np.exp(ic.high))), "d_cohen": d_cohen,
            "reg_efeito": float(np.exp(b) - 1), "reg_ic": (float(np.exp(b - z * se) - 1), float(np.exp(b + z * se) - 1)),
            "previsao": prev}


# ------------------------------------------------------------------ 5. figura
def figura(df: pd.DataFrame, m: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 7, "font.family": "DejaVu Sans", "axes.edgecolor": "#888",
                         "axes.linewidth": 0.6, "xtick.color": "#444", "ytick.color": "#444"})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(3.4, 2.15), gridspec_kw={"width_ratios": [1, 1.15]})
    ordem = [("Sem IA", COR_SEM), ("Com IA", COR_IA)]
    # (a) boxplot por tarefa, escala log (não é gráfico de barras: eixo não precisa começar em zero)
    dados = [df.loc[df.condicao == c, "initial_implementation_time"] for c, _ in ordem]
    bp = a1.boxplot(dados, widths=0.5, patch_artist=True, showfliers=True,
                    medianprops={"color": "#222", "linewidth": 1.2},
                    whiskerprops={"linewidth": 0.7}, capprops={"linewidth": 0.7},
                    flierprops={"marker": "o", "markersize": 2.5, "markerfacecolor": "#777", "markeredgewidth": 0})
    for caixa, (_, cor) in zip(bp["boxes"], ordem):
        caixa.set_facecolor(cor); caixa.set_alpha(0.75); caixa.set_edgecolor("#333"); caixa.set_linewidth(0.6)
    a1.set_yscale("log")
    a1.set_xticks([1, 2], [f"{c}\n(n={len(x)})" for (c, _), x in zip(ordem, dados)])
    a1.set_ylabel("Tempo até o PR (min, escala log)")
    a1.set_title("(a) Tarefas", fontsize=7)
    # (b) média geométrica por desenvolvedor (bloco), linhas ligando as condições
    gs = np.exp(m[["log_sem_ia", "log_com_ia"]])
    for _, r in gs.iterrows():
        lento = r["log_com_ia"] > r["log_sem_ia"]
        a2.plot([0, 1], [r["log_sem_ia"], r["log_com_ia"]], color="#555" if lento else COR_IA,
                ls="-" if lento else "--", lw=0.8, marker="o", markersize=2.6)
    a2.set_yscale("log")
    a2.set_xticks([0, 1], ["Sem IA", "Com IA"])
    a2.set_xlim(-0.25, 1.25)
    a2.set_title("(b) 16 desenvolvedores", fontsize=7)
    a2.set_ylabel("Média geométrica (min, log)")
    l1, = a2.plot([], [], color="#555", ls="-", lw=0.8, marker="o", markersize=2.6)
    l2, = a2.plot([], [], color=COR_IA, ls="--", lw=0.8, marker="o", markersize=2.6)
    fig.legend([l1, l2], [f"(b) mais lento com IA ({int((m.d > 0).sum())})", f"(b) mais rápido com IA ({int((m.d <= 0).sum())})"], fontsize=5.8,
               frameon=False, loc="lower center", ncol=2, handlelength=2.2, columnspacing=1.2)
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
    for a, ticks in ((a1, [5, 10, 30, 100, 300, 600]), (a2, [30, 50, 100, 200, 300])):
        a.yaxis.set_major_locator(FixedLocator(ticks))
        a.yaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
        a.yaxis.set_minor_formatter(NullFormatter())
    for a in (a1, a2):
        a.spines[["top", "right"]].set_visible(False)
        a.grid(axis="y", which="major", color="#ddd", lw=0.4)
    fig.tight_layout(pad=0.3, w_pad=0.8, rect=(0, 0.07, 1, 1))
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "figura1.png", dpi=600)
    plt.close(fig)
    out("\nFigura salva em figuras/figura1.png")


def planejamento(res: dict) -> dict:
    """Tamanho amostral para um estudo completo (não é teste de hipótese)."""
    efeito = abs(np.log(0.80)) / res["dp_d"]  # detectar redução de 20% com o dp(d) observado
    n = TTestPower().solve_power(effect_size=efeito, alpha=ALFA, power=0.80, alternative="larger")
    poder_atual = TTestPower().power(effect_size=efeito, nobs=res["n"], alpha=ALFA, alternative="larger")
    out(f"\nPlanejamento: para detectar redução de 20% (dp(d) = {res['dp_d']:.3f}; d_z = {efeito:.2f}) "
        f"com poder 80%: n = {int(np.ceil(n))} desenvolvedores; poder com n = {res['n']}: {poder_atual:.2f}")
    return {"n_necessario": int(np.ceil(n)), "poder_atual": float(poder_atual), "dz_alvo": float(efeito)}


def main() -> None:
    RES.mkdir(exist_ok=True)
    df = carregar_e_limpar()
    tab = descritiva(df)
    m = por_desenvolvedor(df)
    res = confirmatoria(m)
    exp = exploratorias(df)
    plan = planejamento(res)
    figura(df, m)
    numeros = {"descritiva": tab.to_dict(orient="index"), "confirmatoria": res, "exploratorias": exp,
               "planejamento": plan, "n_tarefas": int(len(df)),
               "min_tarefas_cond": int(m[["n_sem_ia", "n_com_ia"]].min().min()),
               "max_tarefas_cond": int(m[["n_sem_ia", "n_com_ia"]].max().max()),
               "post_review_ausentes": int(df["post_review_implementation_time"].isna().sum())}
    (RES / "numeros.json").write_text(json.dumps(numeros, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    out("\nTotal de testes de hipótese executados: 1 confirmatório (t pareado) + 1 alternativo "
        "previsto (Wilcoxon) + Shapiro-Wilk + 2 exploratórios (E1 Welch, E2 regressão)")
    (RES / "resultados.txt").write_text("\n".join(linhas_saida), encoding="utf-8")


if __name__ == "__main__":
    main()

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.ticker import ScalarFormatter
from scipy import stats
import itertools
import os

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 16,
    "axes.labelsize": 16,
    "legend.fontsize": 14,
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

config = {
    # "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-fp/output.db",
    "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-program-3493/output.db",

    "methods": ["xomt-hybrid-mathsat5", "optimathsat"],
    # "methods": ["xomt-only_bs-mathsat5", "optimathsat"],
    # "methods": ["xomt-hybrid-mathsat5", "xomt-only_bs-mathsat5"],
    # "methods": ["xomt-hybrid-mathsat5", "xomt-hybrid-bitwuzla"],
    # "methods": ["xomt-only_bs-mathsat5", "xomt-only_bs-bitwuzla"],

    "pairs": [
        ("xomt-hybrid-mathsat5", "optimathsat"),
        ("xomt-only_bs-mathsat5", "optimathsat"),
        ("xomt-hybrid-mathsat5", "xomt-only_bs-mathsat5"),
        ("xomt-hybrid-mathsat5", "xomt-hybrid-bitwuzla"),
        ("xomt-only_bs-mathsat5", "xomt-only_bs-bitwuzla")
    ],

    "rename_map": {
        "optimathsat": "OptiMathSAT",
        "xomt-hybrid-mathsat5": "FOMT-H-MathSAT5",
        "xomt-only_bs-mathsat5": "FOMT-BS-MathSAT5",
        "xomt-hybrid-bitwuzla": "FOMT-H-Bitwuzla",
        "xomt-only_bs-bitwuzla": "FOMT-BS-Bitwuzla"
    },

    "output_dir": "scatter-results",
    # "prefix": "qf-fp",
    "prefix": "program",
    "figsize": (7, 7)  # 1:1 比例
}

def load_data(db_path):
    query = f"""
            SELECT id, sort, file, COALESCE(NULLIF(solving_time, 'None'), 600000) AS solving_time
            FROM solving
            WHERE status like 'SolverStatus.%'
--             WHERE status like 'SolverStatus.SAT' and solving_time >= 1000
        """

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)

    numeric_cols = ["solving_time"]
    # df = df[valid].copy()
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=numeric_cols)


def prepare_comparison(df, method1, method2):
    grouped = df.groupby(["file", "sort"]).agg({
        "solving_time": ["mean", "std", "count"]
    })
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns]
    grouped = grouped.reset_index()

    merged = pd.merge(
        grouped[grouped["sort"] == method1],
        grouped[grouped["sort"] == method2],
        on="file",
        suffixes=("_1", "_2"),
        how="inner"
    )
    return merged


def create_scatter(ax, df, label1, label2, confidence=0.99):
    df = df[(df["solving_time_mean_1"] >= 500) | (df["solving_time_mean_2"] >= 500)]

    x = df["solving_time_mean_1"] / 1000.0
    y = df["solving_time_mean_2"] / 1000.0

    n1 = df["solving_time_count_1"]
    n2 = df["solving_time_count_2"]

    std1 = df["solving_time_std_1"]
    std2 = df["solving_time_std_2"]

    # ===============================
    # 计算置信区间半宽
    # ===============================
    se1 = std1 / np.sqrt(n1)
    se2 = std2 / np.sqrt(n2)

    t1 = stats.t.ppf((1 + confidence) / 2, df=n1 - 1)
    t2 = stats.t.ppf((1 + confidence) / 2, df=n2 - 1)

    ci_x = (se1 * t1) / 1000.0
    ci_y = (se2 * t2) / 1000.0

    # ===============================
    # log scale
    # ===============================
    from matplotlib.ticker import LogLocator

    ax.set_xscale("symlog")
    ax.set_yscale("symlog")

    # X 轴副刻度
    ax.xaxis.set_minor_locator(LogLocator(base=10.0,
                                          subs=np.arange(1.0, 10.0) * 0.1,
                                          numticks=10))
    # Y 轴副刻度
    ax.yaxis.set_minor_locator(LogLocator(base=10.0,
                                          subs=np.arange(1.0, 10.0) * 0.1,
                                          numticks=10))

    # ===============================
    # CI 不重叠判断
    # ===============================
    better_y = y + ci_y < x - ci_x
    better_x = x + ci_x < y - ci_y
    # equal = ~(better_x | better_y)

    # ===============================
    # 绘制 scatter（无误差棒）
    # ===============================
    ax.scatter(x[better_y], y[better_y], color="#4daf4a", s=60, alpha=0.8, marker='s')  # 4daf4a
    ax.scatter(x[better_x], y[better_x], color="#377eb8", s=60, alpha=0.8, marker='^')  # 377eb8
    # ax.scatter(xs[equal], ys[equal], color="#999999", s=60, alpha=0.8)

    # ===============================
    # 胜负统计
    # ===============================
    ax.text(0.7, 0.3, str(np.sum(better_y)), transform=ax.transAxes, fontsize=40)
    ax.text(0.3, 0.7, str(np.sum(better_x)), transform=ax.transAxes, fontsize=40)

    # ===============================
    # 对角线
    # ===============================
    min_val = min(x.min(), y.min())
    max_val = max(x.max(), y.max())

    ax.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", alpha=0.6)

    # # ===============================
    # # 坐标轴
    # # ===============================
    # from matplotlib.font_manager import FontProperties
    # import matplotlib as mpl
    # mpl.rcParams['pdf.fonttype'] = 3
    # mpl.rcParams['ps.fonttype'] = 3
    # # mpl.rcParams['pdf.use14corefonts'] = False
    # font_path = "/home/aaa/SIMSUN.ttf"
    # cn_font = FontProperties(fname=font_path)
    # ax.set_xlabel(f"{label1} 的执行时间", fontproperties=cn_font)
    # ax.set_ylabel(f"{label2} 的执行时间", fontproperties=cn_font)

    ax.set_xlabel(f"{label1} solving time (s)")
    ax.set_ylabel(f"{label2} solving time (s)")

    ax.grid(True, linestyle=":", alpha=0.6)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_major_formatter(ScalarFormatter())
    # ax.legend(loc="upper left", frameon=False)

def generate_scatter(config):
    df = load_data(config["db_path"])
    os.makedirs(config["output_dir"], exist_ok=True)

    for method1, method2 in config["pairs"]:
        label1 = config["rename_map"].get(method1, method1)
        label2 = config["rename_map"].get(method2, method2)

        merged = prepare_comparison(df, method1, method2)
        if merged.empty:
            print(f"No data for pair {label1} vs {label2}, skip")
            continue

        fig, ax = plt.subplots(figsize=config["figsize"])
        create_scatter(ax, merged, label1, label2)

        output_path = f"{config['output_dir']}/{config['prefix']}_{label1}_vs_{label2}_scatter"
        fig.tight_layout()
        fig.savefig(output_path + '.pdf', bbox_inches="tight")
        fig.savefig(output_path + ".png", dpi=600, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved to {output_path}")


if __name__ == "__main__":
    generate_scatter(config)

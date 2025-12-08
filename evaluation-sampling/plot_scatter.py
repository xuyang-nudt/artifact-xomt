import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.ticker import ScalarFormatter

config = {
    # "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-fp/output.db", #on/off
    "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-program/output.db", #on/off

    "methods": ["xomt-hybrid-mathsat5", "optimathsat"], #on/off
    # "methods": ["xomt-hybrid-mathsat5", "xomt-only_bs-mathsat5"], #on/off
    # "methods": ["xomt-hybrid-mathsat5", "xomt-hybrid-bitwuzla"], #on/off
    # "methods": ["xomt-only_bs-mathsat5", "xomt-only_bs-bitwuzla"], #on/off

    "rename_map": {
        "optimathsat": "OptiMathSAT",
        "xomt-hybrid-mathsat5": "Xomt",
        "xomt-only_bs-mathsat5": "Xomt-BS",
        # "xomt-hybrid-mathsat5": "Xomt-MathSAT", #on/off
        # "xomt-only_bs-mathsat5": "Xomt-BS-MathSAT", #on/off
        # "xomt-hybrid-bitwuzla": "Xomt-Bitwuzla", #on/off
        # "xomt-only_bs-bitwuzla": "Xomt-BS-Bitwuzla" #on/off
    },
    "output_dir": "scatter-results",
    "prefix": "qf-fp", #on/off
    # "prefix": "program",   #on/off
    "figsize": (7, 7)  # 1:1 比例
}

def load_data(db_path):
    query = f"""
            SELECT id, sort, file,
                   COALESCE(solving_time, 0) AS solving_time
            FROM solving
            WHERE status like 'SolverStatus.SAT'
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


def create_scatter(ax, df, label1, label2):
    x = df["solving_time_mean_1"] / 1000.0
    y = df["solving_time_mean_2"] /1000.0
    xerr = df["solving_time_std_1"] / np.sqrt(df["solving_time_count_1"]) / 1000.0
    yerr = df["solving_time_std_2"] / np.sqrt(df["solving_time_count_2"]) /1000.0

    ax.set_xscale("log")
    ax.set_yscale("log")

    upper_left = y - x > 0.5
    lower_right = x - y > 0.5
    diagonal = abs(x - y) == 0.5

    for mask, color in [(upper_left, "#4daf4a"), (lower_right, "#377eb8"), (diagonal, "#999999")]:
        ax.errorbar(
            x[mask], y[mask],
            xerr=xerr[mask], yerr=yerr[mask],
            fmt='o', color=color, alpha=0.7, markersize=5,
            ecolor='lightgray', elinewidth=1, capsize=2
        )
        # ax.scatter(
        #     x[mask], y[mask],
        #     color=color, alpha=0.7, s=50,  # s=markersize^2
        #     edgecolors='lightgray', linewidths=0.5
        # )

    stats = [
        (0.3, 0.7, f"{sum(upper_left)}", "#4daf4a"),
        (0.7, 0.3, f"{sum(lower_right)}", "#377eb8")
        # (0.5, 0.5, f"{sum(diagonal)}", "#999999")
    ]

    for x_pos, y_pos, text, color in stats:
        # ax.add_patch(plt.Rectangle(
        #     (x_pos - 0.1, y_pos - 0.04), 0.2, 0.1,
        #     transform=ax.transAxes, color=color, alpha=0.6,
        #     zorder=2, linewidth=0
        # ))
        txt = ax.text(x_pos, y_pos, text, transform=ax.transAxes,
                      ha='center', va='center', fontsize=50, color='black')
        # txt.set_path_effects([
        #     path_effects.Stroke(linewidth=2.5, foreground=color),
        #     path_effects.Normal()
        # ])

    ax.plot([x.min(), x.max()], [x.min(), x.max()], 'r--', alpha=0.6)

    ax.set_xlabel(f"{label1} solving time", fontsize=25)
    ax.set_ylabel(f"{label2} solving time", fontsize=25)
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1)
    # ax.set_title(f"{label1} vs {label2} on {config['prefix'].upper()}", fontsize=18, pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_major_formatter(ScalarFormatter())

def generate_scatter(config):
    df = load_data(config["db_path"])
    method1, method2 = config["methods"]
    label1 = config["rename_map"].get(method1, method1)
    label2 = config["rename_map"].get(method2, method2)

    merged = prepare_comparison(df, method1, method2)


    fig, ax = plt.subplots(figsize=config["figsize"])
    create_scatter(ax, merged, label1, label2)

    output_path = f"{config['output_dir']}/{config['prefix']}_{label1}_vs_{label2}_scatter.pdf"
    fig.tight_layout()
    fig.savefig(output_path, dpi=600, bbox_inches="tight")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    generate_scatter(config)

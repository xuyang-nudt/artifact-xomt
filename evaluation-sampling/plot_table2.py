import sqlite3
import pandas as pd
import os

# ========== 配置 ==========
config = {
    "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-fp/output.db",
    "methods": [
        "optimathsat",
        "xomt-only_bs-bitwuzla",
        "xomt-hybrid-bitwuzla",
        "xomt-only_bs-mathsat5",
        "xomt-hybrid-mathsat5"
    ],
    "table_name": "solving",
    "success_status": ["SolverStatus.SAT"],
    "output_dir": "table-results-multi",
    "prefix": "qf-fp"
}
# ===========================

os.makedirs(config["output_dir"], exist_ok=True)


def load_data(db_path):
    """读取数据库中与 methods 相关的所有数据"""
    query = f"""
        SELECT id, file, sort, status
        FROM {config['table_name']}
        WHERE sort IN ({','.join(['?']*len(config['methods']))})
    """

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=config["methods"])

    df["is_success"] = df["status"].isin(config["success_status"])
    return df


def compute_multi_statistics(df):
    """
    多方法一起处理统计：
    1. success_ratio: 每个 file + solver 的成功率
    2. pivot table: file × solvers
    3. stats summary: 对每个 solver：
         - 总成功数
         - 独立成功数（仅该 solver 成功）
    """
    methods = config["methods"]

    # 1️⃣ 每个文件 + 方法统计成功比例
    summary = (
        df.groupby(["file", "sort"])["is_success"]
        .agg(["sum", "count"])
        .reset_index()
    )
    summary["success_ratio"] = summary["sum"] / summary["count"]

    # 2️⃣ pivot 成 file × solvers
    pivot = summary.pivot(index="file", columns="sort", values="success_ratio")
    pivot = pivot.fillna(0)

    pivot = pivot.reindex(columns=config["methods"])

    # 3️⃣ 定义成功阈值（>= 0.5）
    success_matrix = pivot >= 0.5

    # 4️⃣ 统计每种 solver 成功的实例数
    success_counts = success_matrix.sum().to_dict()

    # 5️⃣ 统计“仅本 solver 成功”的实例数
    only_success_counts = {}
    for solver in methods:
        mask_only_this = (success_matrix[solver]) & (success_matrix.drop(columns=[solver]).sum(axis=1) == 0)
        only_success_counts[solver] = int(mask_only_this.sum())

    return pivot, success_counts, only_success_counts


def save_results(pivot, success_counts, only_success_counts):
    """保存结果"""
    prefix = config["prefix"]
    out_dir = config["output_dir"]

    # 保存 pivot table
    pivot_path = os.path.join(out_dir, f"{prefix}_pivot_success.csv")
    pivot.to_csv(pivot_path)

    # 保存 summary
    summary_path = os.path.join(out_dir, f"{prefix}_multi_success_summary.txt")

    with open(summary_path, "w") as f:
        f.write("=== 各方法成功解决实例数 ===\n")
        for solver, num in success_counts.items():
            f.write(f"{solver:30s}: {num}\n")

        f.write("\n=== 仅该方法成功（其他都失败） ===\n")
        for solver, num in only_success_counts.items():
            f.write(f"{solver:30s}: {num}\n")

    print(f"Saved results to:\n  - {pivot_path}\n  - {summary_path}")


def main():
    print("加载数据中...")
    df = load_data(config["db_path"])

    print("计算多方法统计...")
    pivot, success_counts, only_success_counts = compute_multi_statistics(df)

    print("\n=== 各方法成功实例数 ===")
    for k, v in success_counts.items():
        print(f"{k:30s}: {v}")

    print("\n=== 仅该方法成功（其他都失败） ===")
    for k, v in only_success_counts.items():
        print(f"{k:30s}: {v}")

    save_results(pivot, success_counts, only_success_counts)


if __name__ == "__main__":
    main()

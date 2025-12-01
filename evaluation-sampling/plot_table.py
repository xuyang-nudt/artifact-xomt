import sqlite3
import pandas as pd
import os

# ========== 配置 ==========
config = {
    # "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-fp/output.db",
    "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-program-400/output.db",

    # "methods": ["xomt-hybrid-mathsat5", "optimathsat"],
    # "methods": ["xomt-only_bs-mathsat5", "optimathsat"],
    "methods": ["xomt-hybrid-mathsat5", "xomt-only_bs-mathsat5"],
    # "methods": ["optimathsat", "xomt-hybrid-bitwuzla"],
    # "methods": ["optimathsat", "xomt-hybrid-bitwuzla"],
    # "methods": ["xomt-hybrid-mathsat5", "xomt-hybrid-bitwuzla"],
    # "methods": ["xomt-hybrid-bitwuzla", "xomt-only_bs-bitwuzla"],
    # "methods": ["xomt-only_bs-mathsat5", "xomt-only_bs-bitwuzla"],

    # "target_method": "optimathsat",      # 主要方法
    "target_method": "xomt-bybrid-mathsat5",
    "other_method": "xomt-bybrid-mathsat5",
    "table_name": "solving",             # 表名
    "success_status": ["SolverStatus.SAT"],  # 成功状态定义
    "output_dir": "table-results",
    "prefix": "qf-fp"
}
# ===========================

os.makedirs(config["output_dir"], exist_ok=True)


def load_data(db_path):
    """从数据库加载数据"""
    query = f"""
        SELECT id, file, sort, status
        FROM {config['table_name']}
--         WHERE file not like '%wintersteiger%' and sort IN (?, ?)
        WHERE sort IN (?, ?)
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=config["methods"])

    df["is_success"] = df["status"].isin(config["success_status"])
    return df

def compute_statistics(df, target, other):
    """计算每个文件在多次运行中成功次数>=失败次数视为成功"""
    results = []

    # 1️⃣ 对每个 file + solver 统计成功次数和总次数
    summary = (
        df.groupby(["file", "sort"])["is_success"]
        .agg(["sum", "count"])
        .reset_index()
    )
    summary["success_ratio"] = summary["sum"] / summary["count"]

    # 2️⃣ 透视为 file × solver 的表格
    pivot = summary.pivot(index="file", columns="sort", values="success_ratio").fillna(0)

    # 3️⃣ 只保留两个方法的列
    if target in pivot.columns and other in pivot.columns:
        pivot = pivot[[target, other]]
    else:
        print(f"⚠️ 警告: 数据中缺少 {target} 或 {other} 列，将使用可用列。")

    # 4️⃣ 判断是否“成功次数 ≥ 失败次数”
    for file, row in pivot.iterrows():
        target_success = row.get(target, 0) >= 0.5
        other_success = row.get(other, 0) >= 0.5

        if target_success and not other_success:
            category = "only_target_success"
        elif not target_success and other_success:
            category = "only_other_success"
        elif target_success and other_success:
            category = "both_success"
        else:
            category = "both_fail"

        results.append({
            "file": file,
            f"{target}_success_ratio": round(row.get(target, 0), 3),
            f"{other}_success_ratio": round(row.get(other, 0), 3),
            f"{target}_success": int(target_success),
            f"{other}_success": int(other_success),
            "category": category
        })

    return pd.DataFrame(results)

def summarize_results(df_stats, df_raw, target, other):
    """汇总最终结果"""
    summary = {}

    summary["target_method"] = target
    summary["other_method"] = other
    summary["target_success_total"] = int(df_stats[f"{target}_success"].sum())
    summary["other_success_total"] = int(df_stats[f"{other}_success"].sum())
    summary["only_target_success"] = int((df_stats["category"] == "only_target_success").sum())
    summary["only_other_success"] = int((df_stats["category"] == "only_other_success").sum())
    summary["both_success"] = int((df_stats["category"] == "both_success").sum())
    summary["both_fail"] = int((df_stats["category"] == "both_fail").sum())
    summary["total_cases"] = len(df_stats)

    return summary


def save_results(summary):
    """保存结果为文本和CSV"""
    prefix = config["prefix"]
    out_dir = config["output_dir"]
    csv_path = os.path.join(out_dir, f"{prefix}_success_summary.csv")
    txt_path = os.path.join(out_dir, f"{prefix}_success_summary.txt")

    pd.DataFrame([summary]).to_csv(csv_path, index=False)

    with open(txt_path, "w") as f:
        for k, v in summary.items():
            f.write(f"{k:25s}: {v}\n")

    print(f"Saved summary to:\n  - {csv_path}\n  - {txt_path}")

def save_case_lists(df_stats):
    """保存 only_target、only_other、both_fail 的 smt2 文件名"""
    out_dir = config["output_dir"]
    target, other = config["methods"]

    lists = {
        "only_target_success.txt": df_stats[df_stats["category"] == "only_target_success"]["file"].tolist(),
        "only_other_success.txt": df_stats[df_stats["category"] == "only_other_success"]["file"].tolist(),
        "both_fail.txt": df_stats[df_stats["category"] == "both_fail"]["file"].tolist(),
    }

    for filename, files in lists.items():
        path = os.path.join(out_dir, filename)
        with open(path, "w") as f:
            for smt2 in files:
                f.write(smt2 + "\n")
        print(f"Saved {len(files)} items to {path}")

def main():
    print("加载数据中...")
    df = load_data(config["db_path"])
    method1, method2 = config["methods"]
    print(f"比较方法: {method1} vs {method2}")

    print("计算分类统计...")
    df_stats = compute_statistics(df, method1, method2)

    print("生成汇总结果...")
    summary = summarize_results(df_stats, df, method1, method2)

    print("\n=== 成功统计结果 ===")
    for k, v in summary.items():
        print(f"{k:25s}: {v}")

    # 保存独立成功/全部失败 的 .txt 列表
    print("\n保存文件列表...")
    save_case_lists(df_stats)

    save_results(summary)

if __name__ == "__main__":
    main()

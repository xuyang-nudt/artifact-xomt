import sqlite3
import pandas as pd
from scipy.stats import mannwhitneyu

# ========== 配置 ==========
config = {
    "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-full-fp/output.db",
    # "db_path": "/home/aaa/artifact-omt/evaluation-sampling/results-program-400/output.db",

    # "method_A": "xomt-hybrid-mathsat5",
    # "method_B": "optimathsat",
    "method_A": "xomt-hybrid-mathsat5",
    "method_B": "xomt-only_bs-mathsat5",
    # "method_A": "xomt-only_bs-mathsat5",
    # "method_B": "optimathsat",
    "success_status": ["SolverStatus.SAT"],
    "table_name": "solving",
}
# ==========================


# ----- A12 计算 -----
def compute_A12(listA, listB):
    """
    Vargha–Delaney A12 effect size
    """
    more = sum(a > b for a in listA for b in listB)
    equal = sum(a == b for a in listA for b in listB)
    return (more + 0.5 * equal) / (len(listA) * len(listB))


# ----- 读取数据 -----
def load_data():
    query = f"""
        SELECT id, file, sort, status
        FROM {config["table_name"]}
        WHERE sort in (?, ?)
    """
    with sqlite3.connect(config["db_path"]) as conn:
        df = pd.read_sql_query(query, conn, params=[config["method_A"], config["method_B"]])
    df["is_success"] = df["status"].isin(config["success_status"])
    return df


# ----- 计算每次运行成功数量 -----
def compute_run_success_counts(df, method):
    """
    返回某方法在每次运行 id 中成功的 file 数量列表
    """
    success_df = df[(df["sort"] == method) & (df["is_success"] == True)]
    grouped = success_df.groupby("id")["file"].nunique()
    return grouped.tolist()


# ----- 主流程 -----
def main():
    print("加载数据中...")
    df = load_data()

    A = config["method_A"]
    B = config["method_B"]

    print(f"对比方法: {A} vs {B}")

    A_counts = compute_run_success_counts(df, A)
    B_counts = compute_run_success_counts(df, B)

    print(f"{A} 成功实例数: {A_counts}")
    print(f"{B} 成功实例数: {B_counts}")

    # A12 效应量
    A12_value = compute_A12(A_counts, B_counts)

    # p-value (Mann–Whitney U test)
    stat, p_value = mannwhitneyu(A_counts, B_counts, alternative="two-sided")

    print("\n===== 对比结果（Success Count Level）=====")
    print(f"A12 ({A} vs {B}):  {A12_value:.4f}")
    print(f"p-value:           {p_value:.6f}")

    # 解释 A12
    if A12_value > 0.56:
        interpretation = f"{A} 显著优于 {B}"
    elif A12_value < 0.44:
        interpretation = f"{B} 显著优于 {A}"
    else:
        interpretation = "两者差别不大"

    print(f"解释: {interpretation}")


if __name__ == "__main__":
    main()

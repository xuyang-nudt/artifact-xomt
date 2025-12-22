#!/usr/bin/env python

import argparse
import sys
import time
import commands
import subprocess
import database
import seed
import os

def process_optimathsat(file_path, rep, max_time, rng_seed, coverage, db_path, database_lock, tag, max_samples, opt_time, z3_max_memory_mb, max_cov_samples, coverage_limit_pct, kill_time):
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    optimathsat_command = commands.SMTSamplerCommand(smt2_file=file_path, coverage=coverage, max_samples=max_samples,
                                                 opt_time_seconds=opt_time, seed=rng_seed,
                                                 max_time_seconds=max_time, max_memory_size=z3_max_memory_mb,
                                                 max_cov_samples=max_cov_samples, coverage_limit_pct=coverage_limit_pct,
                                                 kill_time=kill_time)

    start_time = time.time()*1000
    try:
        optimathsat_command.run()
    except TimeoutError as timeoutError:
        pass
    end_time = time.time()*1000

    if not db_path is None:
        database.save_command(db_path, optimathsat_command, tag, rep, file_path, "optimathsat", database_lock)

    if optimathsat_command.get_return_code() == 0:
        solving_time = end_time - start_time
        solving_status = str(optimathsat_command.get_solving_status())
        print("[add by yx] solving_status:", solving_status)
        obj_v = optimathsat_command.get_objective()
        # if solving_status == 'SolverStatus.SAT':  # SolverStatus.UNK is 2
        #     obj_v = optimathsat_command.get_objective()

        if not db_path is None:
            database.save_solving(db_path, tag, rep, file_path, "optimathsat", solving_status, "None", obj_v, solving_time, database_lock)
    else:
        if not db_path is None:
            database.save_solving(db_path, tag, rep, file_path, "optimathsat", "error", None, None, None, database_lock)


def process_xomt(file_path, rep, max_time, rng_seed, coverage, db_path, database_lock, tag, max_samples,
                 opt_time, z3_max_memory_mb, max_cov_samples, coverage_limit_pct, kill_time,
                 opt_alg, smt_solver, search_type):
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    xomt_command = commands.QSamplerCommand(smt2_file=file_path, coverage=coverage, max_samples=max_samples,
                                                 opt_time_seconds=opt_time, seed=rng_seed,
                                                 max_time_seconds=max_time, max_memory_size=z3_max_memory_mb,
                                                 max_cov_samples=max_cov_samples, coverage_limit_pct=coverage_limit_pct,
                                                 kill_time=kill_time, alg=opt_alg, smt_solver=smt_solver, search_type=search_type)

    start_time = time.time()*1000
    try:
        xomt_command.run()
    except TimeoutError as timeoutError:
        pass
    end_time = time.time()*1000

    if not db_path is None:
        database.save_command(db_path, xomt_command, tag, rep, file_path, "xomt-"+search_type+"-"+smt_solver, database_lock)

    if xomt_command.get_return_code() == 0:
        solving_time = end_time - start_time
        solving_status = str(xomt_command.get_solving_status())
        print("[add by yx] solving_status:", solving_status)
        obj_sign = None
        obj_v=xomt_command.get_objective()
        # if solving_status == 'SolverStatus.SAT':  # SolverStatus.UNK is 2
        #     obj_v = sampler_command.get_objective()

        if not db_path is None:
            database.save_solving(db_path, tag, rep, file_path, "xomt-"+search_type+"-"+smt_solver, solving_status, None, obj_v, solving_time, database_lock)

    else:
        if not db_path is None:
            database.save_solving(db_path, tag, rep, file_path, "xomt-"+search_type+"-"+smt_solver, "error", None, None, None, database_lock)

    try:
        xomt_command.cleanup()
    except:
        print("Error doing cleanup")

def process_smt2_files(file_paths, max_time, rep_id, rng_seed, coverage, database,
                       database_lock, tag, tool, opt_time, max_samples, max_memory_mb, max_cov_samples,
                       coverage_limit_pct, kill_time, opt_alg, smt_solver, search_type):
    for file_path in file_paths:
        file_path = file_path.strip()
        seed_generator = seed.Seed(rng_seed, file_path)
        assert rep_id < 1000
        seeds_file = seed_generator.seeds_for_file(1000)
        if tool == "xomt":
            print("[add by yx] tool:", tool)
            process_xomt(file_path, rep_id, max_time,  seeds_file[rep_id], coverage, database, database_lock, tag,
                         max_samples, opt_time, max_memory_mb, max_cov_samples, coverage_limit_pct, kill_time,
                         opt_alg, smt_solver, search_type)
        elif tool == "optimathsat":
            print("[add by yx] tool:", tool)
            process_optimathsat(file_path, rep_id, max_time,  seeds_file[rep_id], coverage, database, database_lock, tag,
                                max_samples, opt_time, max_memory_mb, max_cov_samples, coverage_limit_pct, kill_time)
        else:
            assert False

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('true', '1'):
        return True
    elif v.lower() in ('false','0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def check_db_file(db_path):
    """检查数据库文件状态"""
    db_file = Path(db_path)

    # 检查文件是否存在
    if not db_file.exists():
        print(f"❌ 错误：数据库文件不存在 {db_path}")
        print(f"当前工作目录：{os.getcwd()}")
        print(f"绝对路径：{db_file.absolute()}")
        return False

    # 检查文件是否可读
    if not os.access(db_path, os.R_OK):
        print(f"❌ 错误：数据库文件不可读 {db_path}")
        print(f"文件权限：{oct(db_file.stat().st_mode & 0o777)}")
        return False

    # 检查文件是否可写（如果需要修改）
    if not os.access(db_path, os.W_OK):
        print(f"⚠️ 警告：数据库文件不可写 {db_path}")
        print(f"文件权限：{oct(db_file.stat().st_mode & 0o777)}")

    return True

def main():
    parser = argparse.ArgumentParser(description='Solve SMT2 files using the JFS solver.')
    parser.add_argument('-max-time', required=True, type=int, help='OMT solver time limit (seconds)')
    parser.add_argument('-rep-id', type=int, default=None, help='Execution id', required=True)
    parser.add_argument('-seed', type=int, default=0x96e1ecec)
    parser.add_argument('-coverage', action='store_true')
    parser.add_argument('-jfs-diversify-free-variables', action='store_true')
    parser.add_argument('-jfs-diversify-expr-variables', action='store_true')
    parser.add_argument('-jfs-diversify-prob', type=float, default=1)
    parser.add_argument('-tag', type=str, help='Experiment tag')
    parser.add_argument('-database', type=str, default=None)
    parser.add_argument('-database-lock', type=str, default=None)
    parser.add_argument('-smt2-file', type=str, default=None)
    parser.add_argument('-tool', type=str, required=True)
    parser.add_argument('-opt-time', type=int, default=10, help="Optimization search time (seconds)")
    parser.add_argument('-max-samples', type=int, default=50000)
    parser.add_argument('-max-memory-mb', type=int, default=6*1024)
    parser.add_argument('-max-cov-samples', type=int, default=0)
    parser.add_argument('-coverage-limit-pct', type=int, default=100)
    parser.add_argument('-passes', type=str, default=None)
    parser.add_argument('-smtsampler-reg-times', type=int, default=0)
    parser.add_argument('-smtsampler-threshold', type=int, default=3)
    parser.add_argument('-smtsampler-use-current-testcase', type=str2bool, default=False)
    parser.add_argument('-save-at-exit', action='store_true', default=False)
    parser.add_argument('-kill-time', type=int, required=True)
    parser.add_argument('-opt-alg', type=str, choices=['mocea', 'moceads2', 'optimathsat'], default='mocea')
    parser.add_argument('-smt-solver', type=str, choices=['z3', 'mathsat5', 'bitwuzla'], default='bitwuzla')
    parser.add_argument('-search-type', type=str, choices=['hybrid', 'only_bs', 'only_opt'], default='hybrid')

    # print("[add by yx] reach args")
    args = parser.parse_args()
    print("[add by yx] args", args)
    assert args.tool == "optimathsat" or args.tool == "xomt"
    # assert args.passes != None

    if args.smt2_file is None:
        file_paths = sys.stdin.readlines()
    else:
        file_paths = [args.smt2_file]

    if not args.database is None:
        database.create_tables(args.database, args.database_lock)
        assert not args.tag is None

    # print("[add by yx] reach process!")
    process_smt2_files(file_paths, args.max_time, args.rep_id, args.seed, args.coverage, args.database,
                       args.database_lock, args.tag, args.tool, args.opt_time, args.max_samples,
                       args.max_memory_mb, args.smtsampler_use_current_testcase, args.coverage_limit_pct,
                       args.kill_time, args.opt_alg, args.smt_solver, args.search_type)

if __name__ == "__main__":
    main()
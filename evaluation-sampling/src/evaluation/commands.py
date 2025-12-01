import tempfile
import subprocess
import time
import os
import csv
import io
from enum import Enum
import shutil
import re
import struct
import re
import math
from decimal import Decimal
from collections import defaultdict

class CommandException(Exception):
    pass

class SolverStatus(Enum):
    SAT = 0
    UNSAT = 1
    UNK = 2

def parse_csv_file(file_path):
    with open(file_path, newline='') as csvfile:
        return parse_csv(csvfile)

def parse_csv(csvfile):
    result_dict = {}

    csv_reader = csv.reader(csvfile)
    
    for row in csv_reader:
        key = row[0]
        values = tuple(map(str, row[1:]))
        result_dict[key] = values
    
    return result_dict

class Command:
    def run_command(self, string_list, start_new_session=False, shell=True):
        string_list = [e for e in string_list if e != None]
        string_list = [e.strip() for e in string_list]
        string_list = [e for e in string_list if e != ""]
        self.command = " ".join(string_list)
        start_time = time.time()
        self.command_result = subprocess.run(self.command if shell else string_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, start_new_session=start_new_session)
        self.time = (time.time() - start_time)*1000
        # self.time = round(self.time, 2)
        print("[add by yx] command:", self.command)
        print("[add by yx] command_result:", self.command_result)
        print("[add by yx] time (ms):", self.time)

    def get_time(self):
        return self.time

    def get_stdout(self):
        return self.command_result.stdout.decode('utf-8', errors='replace')

    def get_stderr(self):
        return self.command_result.stderr.decode('utf-8', errors='replace')
     
    def get_return_code(self):
        return self.command_result.returncode
    
    def get_command(self):
        return self.command
    
class SMTCoverageCommand(Command):
    def __init__(self, smt2_file, models_dir, timeout_seconds, rng_seed=0, max_cov_samples=0):
        self.smt2_file = smt2_file
        self.models_dir = models_dir
        self.max_cov_samples = max_cov_samples
        self.rng_seed = rng_seed
        self.timeout_seconds=timeout_seconds
        self.command = None

    def run(self):
        # Run the command and capture the output and error
        cmd_list = ["smt-coverage", "-r", str(self.rng_seed), "-m", str(self.max_cov_samples), self.models_dir, self.smt2_file]

        timeout_list = ["timeout", "-s", "9", str(self.timeout_seconds)] 
        self.run_command(timeout_list + cmd_list)

        self.result_dict = None

        if self.get_return_code() == 0:
            file = io.StringIO(self.get_stdout())
            self.result_dict = parse_csv(file)

    def get_total_bv_coverage(self):
        if self.result_dict is None:
            return None
        return tuple(map(int, self.result_dict['bv-coverage']))
    
    def get_total_bool_coverage(self):
        if self.result_dict is None:
            return None
        return tuple(map(int, self.result_dict['bool-coverage']))

def remove_directory(path):
    if path != "/" and path != "" and os.path.isdir(path):
        try:
            rescode = subprocess.run(f'echo "123" | sudo -S rm -rf {path}',
                           shell=True, check=True)
            print('[add by yx] rescode: ',rescode)
        except subprocess.CalledProcessError as e:
            print("Error occurred while removing directory: " + str(e))

class JFSCommand(Command):
    def __init__(self, smt2_file, timeout_seconds=0, seed=1, output_dir=None, keep_output_dir=False, sampling=False, export_model=False, diversify_free_variables=False, diversify_expr_variables=False, max_samples=0, max_cov_samples=0, passes="none", max_memory_mb=5120, smtsampler_reg_times=0, smtsampler_threshold=3, save_at_exit=False, smtsampler_use_current_testcase=False, coverage_limit_pct=100, coverage=False, kill_time=300, jfs_diversify_prob=1):
        self.smt2_file = smt2_file
        self.timeout_seconds = timeout_seconds
        self.seed = seed
        self.output_dir = output_dir
        if not os.path.exists("/tmp/fast"):
            os.makedirs("/tmp/fast")
        if self.output_dir is None:
            if keep_output_dir:
                self.output_dir_obj = None
                self.output_dir = tempfile.mkdtemp(prefix="jfs-out-dir", dir="/tmp/fast")
            else:
                self.output_dir_obj = tempfile.TemporaryDirectory(prefix="jfs-out-dir", dir="/tmp/fast")
                self.output_dir = self.output_dir_obj.name
            
        self.stats_file = os.path.join(tempfile.mkdtemp(prefix="jfs-out-dir-stats"), "stats.yaml")
        self.sampling = sampling
        self.export_model = export_model
        self.diversify_free_variables = diversify_free_variables
        self.diversify_expr_variables = diversify_expr_variables
        self.keep_output_dir = keep_output_dir
        self.max_samples = max_samples
        self.command = None
        self.keep_out_dir = keep_output_dir
        self.max_cov_samples = max_cov_samples
        self.passes = passes
        self.max_memory_mb = max_memory_mb
        self.smtsampler_reg_times = smtsampler_reg_times
        self.smtsampler_threshold = smtsampler_threshold
        self.save_at_exit = save_at_exit
        self.smtsampler_use_current_testcase = smtsampler_use_current_testcase
        self.coverage_limit_pct = coverage_limit_pct
        self.coverage = coverage
        self.kill_time = kill_time
        self.jfs_diversify_prob = jfs_diversify_prob
        # print("[add by yx] output-dir-jfs: ", self.output_dir)

    def cleanup(self):
        if self.output_dir_obj != None:
            self.output_dir_obj.cleanup()
        remove_directory(self.output_dir)
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)

    def run(self):
        # Run the command and capture the output and error
        sampling_opt = "-libfuzzer-sampling" if self.sampling else ""
        export_model_opt = "-export-model" if self.export_model else ""
        diversify_free_variables_opt = "-diversify-free-variables" if self.diversify_free_variables else ""
        diversify_expr_variables_opt = "-diversify-expr-variables" if self.diversify_expr_variables else ""
        keep_out_dir_opt = "-keep-output-dir" if self.keep_output_dir else ""
        save_at_exit = "-libfuzzer-save-artifacts-at-exit=1" if self.save_at_exit else ""
        smtsampler_use_testcase = "-libfuzzer-smtsampler-use-current-testcase" if self.smtsampler_use_current_testcase else ""
        if self.passes == "none":
            passes_opt = "-disable-standard-passes"
        elif self.passes == "short":
            passes_opt = "-short-standard-passes"
        else:
            assert self.passes == "standard"
            passes_opt = ""

        # Options taken from JFS's original paper/artifact (winner strategy  JFS_LF_SS).
        fixed_options = ["-O0", "-sm-all-ones-seed", "-sm-all-zeros-seed", "-sm-special-constant-seeds=true", "-sm-max-num-seed=100", "-libfuzzer-pure-random=false", "-branch-encoding=fail-fast"] # "-stats-file", self.stats_file
        fixed_options = fixed_options + (["-export-model-smt-coverage"] if self.coverage else [])
        fixed_options = fixed_options + (["-libfuzzer-single-crash-file"] if self.save_at_exit else [])
        max_memory_opt = "-libfuzzer-rss-limit-mb="+str(self.max_memory_mb)

        cmd_list = ["/home/user/jfs/build/bin/jfs"] + fixed_options + [ "-diversify-prob", str(self.jfs_diversify_prob), "-export-model-as-smt2=false", "-export-model-pct", str(self.coverage_limit_pct), max_memory_opt, "-redirect-libfuzzer-output=0", passes_opt, save_at_exit, "-export-model-n", str(self.max_cov_samples), "-libfuzzer-max-samples", str(self.max_samples), "-max-time", str(self.timeout_seconds), "-seed", str(self.seed), "-output-dir", self.output_dir, keep_out_dir_opt, sampling_opt, diversify_free_variables_opt, diversify_expr_variables_opt, export_model_opt, "-libfuzzer-smtsampler-threshold", str(self.smtsampler_threshold), "-libfuzzer-smtsampler-register-times", str(self.smtsampler_reg_times), str(smtsampler_use_testcase), self.smt2_file]
        # cmd_list = ["/home/aaa/artifact/jfs/cmake-build-debug/bin/jfs"] + fixed_options + ["-diversify-prob", str(self.jfs_diversify_prob),
        #                                                                "-export-model-as-smt2=false",
        #                                                                "-export-model-pct",
        #                                                                str(self.coverage_limit_pct), max_memory_opt,
        #                                                                "-redirect-libfuzzer-output=0", passes_opt,
        #                                                                save_at_exit, "-export-model-n",
        #                                                                str(self.max_cov_samples),
        #                                                                "-libfuzzer-max-samples", str(self.max_samples),
        #                                                                "-max-time", str(self.timeout_seconds), "-seed",
        #                                                                str(self.seed), "-output-dir", self.output_dir,
        #                                                                keep_out_dir_opt, sampling_opt,
        #                                                                diversify_free_variables_opt,
        #                                                                diversify_expr_variables_opt, export_model_opt,
        #                                                                "-libfuzzer-smtsampler-threshold",
        #                                                                str(self.smtsampler_threshold),
        #                                                                "-libfuzzer-smtsampler-register-times",
        #                                                                str(self.smtsampler_reg_times),
        #                                                                str(smtsampler_use_testcase), self.smt2_file]

        timeout_list = ["timeout", "-s", "9", str(self.kill_time)]
        cmd = timeout_list + cmd_list

        #with tempfile.NamedTemporaryFile(delete=False, dir="logs/") as temp_file:
        #    temp_file_name = temp_file.name
        #cmd += ["2>&1", "|", "tee", temp_file_name]

        #cmd = ["("] + cmd + [")"]
        self.run_command(cmd, start_new_session=True, shell=True)
        
        self.solving_status = None
        if self.get_return_code() == 0:
            stdout_str = self.get_stdout()
            if "sat" in stdout_str:
                self.solving_status = SolverStatus.SAT
            elif "unsat" in stdout_str:
                self.solving_status = SolverStatus.UNSAT
            else:
                self.solving_status = SolverStatus.UNK

    def get_coverage_time(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage-time.csv")
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number

    def get_total_bv_coverage(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage.csv")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return tuple(map(int, result_dict['bv-coverage']))
        return None
    
    def get_total_bool_coverage(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage.csv")
        # print("JFS [add by yx] file_path: ", file_path)
        if os.path.exists(file_path):
            # print("JFS [add by yx] file_path exists: ", file_path)
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return tuple(map(int, result_dict['bool-coverage']))
        return None

    def get_samples_vec(self):
        file_path = os.path.join(self.output_dir, "export-samples-coverage.csv")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return list(result_dict['samples_vec'])
        return None

    def get_coverage_vec(self):
        file_path = os.path.join(self.output_dir, "export-samples-coverage.csv")
        # print("JFS [add by yx] file_path: ", file_path)
        if os.path.exists(file_path):
            # print("JFS [add by yx] file_path exists: ", file_path)
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return list(result_dict['coverage_vec'])
        return None

    def get_solving_status(self):
        return self.solving_status
    
    def get_total_samples(self):
        file_path = os.path.join(self.output_dir, "models-count.csv")
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number

    def get_sampling_time(self):
        # file_path = os.path.join(self.output_dir, "fuzzing-time.csv")
        file_path = os.path.join(self.output_dir, "export-solver-time.csv")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number
    
    def get_pm_convert_time(self):
        file_path = os.path.join(self.output_dir, "export-pm-model-convert-time.csv")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number
    
    #def parse_sampling_time(file_path):
    #    shell_command = "awk '/name: jfs_fuzzing/{getline;getline;getline; print $2; exit}' " + file_path
    #    try:
    #        result = subprocess.check_output(shell_command, shell=True, stderr=subprocess.STDOUT)
    #        parsed_float = float(result)
    #        return parsed_float
    #    except subprocess.CalledProcessError as e:
    #        return None
    #    except ValueError as e:
    #        return None
    #
    #    return None

    def get_exported_models_dir(self):
        if not self.export_model:
            print("Export model option was not enabled")
            return None
        
        result = os.path.join(self.output_dir, "exported-models")
        if not os.path.exists(result):
            print("Exported models directory does not exist: " + result)
            return None
        
        return result

    def get_total_exported_models(self):
        dir = self.get_exported_models_dir()
        if dir == None:
            return 0
        return JFSCommand.count_smt2_files(dir)

    def count_smt2_files(directory):
        # Ensure the provided path is a directory
        if not os.path.isdir(directory):
            raise ValueError("The provided path is not a directory.")
    
        # Initialize a counter for smt2 files
        smt2_file_count = 0
    
        # Iterate through all files in the directory
        for filename in os.listdir(directory):
            # Check if the file ends with ".smt2"
            if filename.endswith(".smt2"):
                smt2_file_count += 1
    
        return smt2_file_count


class SMTSamplerCommand(Command):
    def __init__(self, smt2_file, output_dir=None, coverage=False, max_samples=1000000, opt_time_seconds=10, seed=0, max_memory_size=5120, max_time_seconds=600, max_cov_samples=0, coverage_limit_pct=100, kill_time=300):
        if not os.path.exists(smt2_file):
            raise Exception("The given SMT2 file does not exist", str(smt2_file))
        
        self.output_dir = output_dir
        if self.output_dir is None:
            self.output_dir_obj = tempfile.TemporaryDirectory(prefix="SMTSampler", dir="/tmp/fast")
            self.output_dir = self.output_dir_obj.name
        
        self.coverage = coverage
        self.max_samples = max_samples
        self.opt_time_second = opt_time_seconds
        self.seed = seed
        self.max_memory_size = max_memory_size
        self.max_time_seconds = max_time_seconds
        self.smt2_file = smt2_file
        self.max_cov_samples = max_cov_samples
        self.coverage_limit_pct = coverage_limit_pct
        self.command = None
        self.kill_time = kill_time

    def run(self):
        # cmd = ["/usr/bin/s", "-no-slow-stop", "-n", str(self.max_samples), "-solver-timeout", str(self.timeout_miliseconds), "-max-memory-size", str(self.max_memory_size), "-rng-seed", str(self.seed), "-t", str(self.max_time_seconds), "-coverage" if self.coverage else "", "-max-cov-samples", str(self.max_cov_samples), "-max-cov-samples-pct", str(self.coverage_limit_pct), self.smt2_file, self.output_dir]
        cmd = ["/home/aaa/optimathsat/bin/optimathsat", "-model_generation=true", self.smt2_file]

        timeout_list = ["timeout", "-s", "SIGKILL", str(self.max_time_seconds)]
        cmd = timeout_list + cmd
        cmd = ["("] + cmd + [")"]
        self.run_command(cmd)
        
        self.result_dict = None
        self.solving_status = None

        if self.get_return_code() == 0:
            stats_file = os.path.join(self.output_dir, "stats")
            if os.path.exists(stats_file):
                self.result_dict = parse_csv_file(stats_file)
            else:
                self.result_dict = None

        self.solving_status = None
        if self.get_return_code() == 0:
            self.stdout_str = self.get_stdout()
            if "sat" in self.stdout_str:
                self.solving_status = SolverStatus.SAT
            elif "unsat" in self.stdout_str:
                self.solving_status = SolverStatus.UNSAT
            else:
                self.solving_status = SolverStatus.UNK
            # print("[add by yx] stdout: ", self.stdout_str)

    def get_solving_status(self):
        return self.solving_status
    
    def get_total_samples(self):
        return int(self.result_dict['samples'][0]) if not self.result_dict is None else None

    def get_total_bv_coverage(self):
        return tuple(map(int, self.result_dict['bv-coverage'])) if not self.result_dict is None else None
    
    def get_total_bool_coverage(self):
        return tuple(map(int, self.result_dict['bool-coverage'])) if not self.result_dict is None else None

    def get_sampling_time(self):
        return float(self.result_dict['sampling-time'][0]) if not self.result_dict is None else None

    def get_coverage_time(self):
        sampling_time = self.get_sampling_time()
        if sampling_time is None:
            return None

        return self.get_time() - sampling_time

    def get_samples_vec(self):
        print("[add by yx] samples_vec, ", self.result_dict['samples_vec'])
        return list(self.result_dict['samples_vec']) if not self.result_dict is None else None

    def get_coverage_vec(self):
        print("[add by yx] coverage_vec, ", self.result_dict['coverage_vec'])
        return list(self.result_dict['coverage_vec']) if not self.result_dict is None else None

    def extract_objectives_block(self, text: str) -> str:
        """提取完整的 (objectives ...) 块"""
        start = text.find("(objectives")
        if start == -1:
            return ""
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return ""

    def parse_objectives_values(self, text: str):
        block = self.extract_objectives_block(text)
        if not block:
            return []

        values = []

        # 去掉外层 (objectives ... )
        inner = block[len("(objectives"): -1].strip()

        # 按括号计数提取每一条 (name ...)
        i = 0
        n = len(inner)
        while i < n:
            # 找到起始 '('
            if inner[i] != "(":
                i += 1
                continue
            depth = 0
            start = i
            while i < n:
                if inner[i] == "(":
                    depth += 1
                elif inner[i] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            entry = inner[start:i + 1].strip()
            i += 1

            # 分离变量名和内容
            m = re.match(r'\(\s*([\w~#\-\.\|]+)\s+(.+)\)', entry, re.S)
            if not m:
                continue
            name, val = m.group(1), m.group(2).strip()

            # ((_ to_fp 8 24) RNE <number>)
            m2 = re.match(r'\(\(_ to_fp \d+ \d+\)\s+\w+\s+(.+)\)', val)
            if m2:
                num_str = m2.group(1).strip()
                try:
                    values.append(float(num_str))
                except ValueError:
                    values.append(num_str)
                continue

            # (_ +oo 8 24) / (_ -oo 8 24) / (_ NaN 8 24)
            m3 = re.match(r'\(_\s+([^\s]+)\s+\d+\s+\d+\)', val)
            if m3:
                tag = m3.group(1)
                if tag == "+oo":
                    values.append(math.inf)
                elif tag == "-oo":
                    values.append(-math.inf)
                elif tag.lower() == "nan":
                    values.append(math.nan)
                else:
                    values.append(tag)
                continue

            # 其他直接保留
            values.append(val)

        return values

    def get_objective(self):
        print("[add by yx] stdout: ", self.get_stdout())
        # obj = self.parse_objectives_values(self.get_stdout())
        # # for v in obj:
        # #     print(v)
        # obj_str = str(obj)
        # print("[add by yx] obj: ", obj_str)
        return self.get_stdout()

"""
  sampler_command = commands.QSamplerCommand(smt2_file=file_path, output_dir=output_path, coverage=coverage, max_samples=max_samples,
                                                 timeout_seconds=solver_timeout, seed=rng_seed,
                                                 max_time_seconds=max_time, max_memory_size=z3_max_memory_mb,
                                                 max_cov_samples=max_cov_samples, coverage_limit_pct=coverage_limit_pct,
                                                 kill_time=kill_time)
                                                 """

class QSamplerCommand(Command):
    def __init__(self, smt2_file, output_dir=None, coverage=False, max_samples=1000000, opt_time_seconds=10,
                 seed=0, max_memory_size=5120, max_time_seconds=600, max_cov_samples=0, coverage_limit_pct=100,
                 kill_time=300, alg="mocea", smt_solver="mathsat5", search_type="hybrid"):
        if not os.path.exists(smt2_file):
            raise Exception("The given SMT2 file does not exist", str(smt2_file))

        # self.output_dir = output_dir
        # if self.output_dir is None:
        #     self.output_dir_obj = tempfile.TemporaryDirectory(prefix="QSampler", dir="/home/aaa/qsampler/output")
        #     self.output_dir = self.output_dir_obj.name

        self.output_dir = output_dir
        if not os.path.exists("/tmp/fast"):
            os.makedirs("/tmp/fast")
        if self.output_dir is None:
            self.output_dir_obj = None
            self.output_dir = tempfile.mkdtemp(prefix="qsampler-out-dir", dir="/tmp/fast")

        # self.export_model = export_model
        self.coverage = coverage
        self.max_samples = max_samples
        self.opt_time_seconds = opt_time_seconds
        self.seed = seed
        self.max_memory_size = max_memory_size
        self.max_time_seconds = max_time_seconds
        self.smt2_file = smt2_file
        self.max_cov_samples = max_cov_samples
        self.coverage_limit_pct = coverage_limit_pct
        self.command = None
        self.kill_time = kill_time
        self.alg = alg
        self.smt_solver = smt_solver
        self.search_type = search_type
        # print("[add by yx] output-dir-qsampler: ", self.output_dir)

    def cleanup(self):
        if self.output_dir_obj != None:
            self.output_dir_obj.cleanup()
        remove_directory(self.output_dir)

    def run(self):
        cmd = ["/home/aaa/xomt/build/bin/xomt", "-opt-time", str(self.opt_time_seconds), "-alg", self.alg,
                          "-pop-size", "100", "-smt-solver", str(self.smt_solver), "-search-type", str(self.search_type), "-c",
                          "-f", self.smt2_file]

        timeout_list = ["timeout", "-s", "SIGKILL", str(self.max_time_seconds)]
        cmd = timeout_list + cmd
        # cmd = ["("] + cmd + [")"]

        # print("[add by yx] qsampler cmd:", cmd)

        self.run_command(cmd, start_new_session=True, shell=True)

        self.solving_status = None
        if self.get_return_code() == 0:
            self.stdout_str = self.get_stdout()
            if "sat" in self.stdout_str:
                self.solving_status = SolverStatus.SAT
            elif "unsat" in self.stdout_str:
                self.solving_status = SolverStatus.UNSAT
            else:
                self.solving_status = SolverStatus.UNK
            print("[add by yx] stdout: ", self.stdout_str)

        # if self.get_return_code() == 0:
        #     file = io.StringIO(self.get_stdout())
        #     self.result_dict = parse_csv(file)
        #     print("[add by yx] result_dict: ", self.result_dict)

    def get_coverage_time(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage-time.csv")
        if not os.path.exists(file_path):
            return 0
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number

    def get_total_bv_coverage(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage.csv")
        if not os.path.exists(file_path):
            return 0,0
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return tuple(map(int, result_dict['bv-coverage']))
        return None

    def get_total_bool_coverage(self):
        file_path = os.path.join(self.output_dir, "export-smt-coverage.csv")
        if not os.path.exists(file_path):
            return 0,0
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return tuple(map(int, result_dict['bool-coverage']))
        return None

    def get_coverage_vec(self):
        file_path = os.path.join(self.output_dir, "export-samples-coverage.csv")
        if not os.path.exists(file_path):
            return list()
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return list(result_dict['coverage_vec'])
        return None

    def get_samples_vec(self):
        file_path = os.path.join(self.output_dir, "export-samples-coverage.csv")
        if not os.path.exists(file_path):
            return list()
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                result_dict = parse_csv(file)
                if result_dict is None:
                    return None
                return list(result_dict['samples_vec'])
        return None

    def get_solving_status(self):
        return self.solving_status

    def get_total_samples(self):
        file_path = os.path.join(self.output_dir, "models-count.csv")
        # print("[add by yx] file_path: ",file_path)
        if not os.path.exists(file_path):
            return 0
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number

    def get_objective(self):
        # # file_path = os.path.join(self.output_dir, "objective.csv")
        # # # print("[add by yx] file_path: ",file_path)
        # # if not os.path.exists(file_path):
        # #     return 0
        # # with open(file_path, 'r') as file:
        # #     content = file.read()
        # # number = int(content)
        # # return number
        # parts = self.stdout_str.split('\n')
        # obj_sign = int(parts[5].split('=')[1])
        # obj2_str = parts[2].split('=')[1]
        # # print("[add by yx] obj2_str: ",obj2_str)
        # # if obj2_str == '-nan' or obj2_str == 'nan' or obj2_str == '-inf' or obj2_str == 'inf':
        # #     return obj_sign, obj2_str
        # obj2_v = str(Decimal(obj2_str))
        # print("[add by yx] obj_sign obj2_v: ", obj_sign, obj2_v)
        # return obj_sign, obj2_v
        return self.get_stdout()

    def get_sampling_time(self):
        file_path = os.path.join(self.output_dir, "solving-time.csv")
        if not os.path.exists(file_path):
            return 0
        with open(file_path, 'r') as file:
            content = file.read()
        number = int(content)
        return number

    # def get_pm_convert_time(self):
    #     file_path = os.path.join(self.output_dir, "export-pm-model-convert-time.csv")
    #     if not os.path.exists(file_path):
    #         return None
    #     with open(file_path, 'r') as file:
    #         content = file.read()
    #     number = int(content)
    #     return number
    #
    # def parse_sampling_time(file_path):
    #    shell_command = "awk '/name: jfs_fuzzing/{getline;getline;getline; print $2; exit}' " + file_path
    #    try:
    #        result = subprocess.check_output(shell_command, shell=True, stderr=subprocess.STDOUT)
    #        parsed_float = float(result)
    #        return parsed_float
    #    except subprocess.CalledProcessError as e:
    #        return None
    #    except ValueError as e:
    #        return None
    #
    #    return None

    # def get_exported_models_dir(self):
    #     if not self.export_model:
    #         print("Export model option was not enabled")
    #         return None
    #
    #     result = os.path.join(self.output_dir, "exported-models")
    #     if not os.path.exists(result):
    #         print("Exported models directory does not exist: " + result)
    #         return None
    #
    #     return result
    #
    # def get_total_exported_models(self):
    #     dir = self.get_exported_models_dir()
    #     if dir == None:
    #         return 0
    #     return JFSCommand.count_smt2_files(dir)

    # def count_smt2_files(directory):
    #     # Ensure the provided path is a directory
    #     if not os.path.isdir(directory):
    #         raise ValueError("The provided path is not a directory.")
    #
    #     # Initialize a counter for smt2 files
    #     smt2_file_count = 0
    #
    #     # Iterate through all files in the directory
    #     for filename in os.listdir(directory):
    #         # Check if the file ends with ".smt2"
    #         if filename.endswith(".smt2"):
    #             smt2_file_count += 1
    #
    #     return smt2_file_count
#!/bin/bash

set -x
set -e

CURRENT_DIR=$(dirname "$(readlink -f "$0")")
SAMPLE_PY="/tmp/evaluation-sampling/src/evaluation/sample.py"
RAND_BENCH_PY="/tmp/evaluation-sampling/src/evaluation/rand-benchmarks.py"
JOIN_DB_SH="/tmp/evaluation-sampling/src/sqlite/join-dbs.sh"

sample_jfs(){
    local database_dir=$1
    local smt2_file=$2
    local rep_id=$3

    # Check if the variable is set
    if [ -z "${PASSES}" ]; then
      echo "Error: PASSES is not set."
      exit 1
    fi

    local current_db=$(mktemp --suffix=.db --tmpdir=$database_dir) 

    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE $EVAL_DIVERSIFY_PROB_JFS $EVAL_DIVERSIFY_FREE_VARIABLES_JFS $EVAL_DIVERSIFY_EXPR_VARIABLES_JFS -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT $PASSES -smtsampler-reg-times $EVAL_SMTSAMPLER_REG_TIMES_JFS -smtsampler-threshold $EVAL_SMTSAMPLER_THRESHOLD_JFS $EVAL_SAVE_AT_EXIT -smtsampler-use-current-testcase $EVAL_SMTSAMPLER_USE_CURRENT_TESTCASE_JFS -coverage-limit-pct $coverage_limit_pct -tool jfs -kill-time $kill_secs"
}

sample_qsampler(){
    local database_dir=$1
    local smt2_file=$2
    local rep_id=$3

    local current_db=$(mktemp --suffix=.db --tmpdir=$database_dir)

#    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE $EVAL_DIVERSIFY_PROB_JFS $EVAL_DIVERSIFY_FREE_VARIABLES_JFS $EVAL_DIVERSIFY_EXPR_VARIABLES_JFS -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT $PASSES -smtsampler-reg-times $EVAL_SMTSAMPLER_REG_TIMES_JFS -smtsampler-threshold $EVAL_SMTSAMPLER_THRESHOLD_JFS $EVAL_SAVE_AT_EXIT -smtsampler-use-current-testcase $EVAL_SMTSAMPLER_USE_CURRENT_TESTCASE_JFS -coverage-limit-pct $coverage_limit_pct -tool qsampler -kill-time $kill_secs"
    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT -coverage-limit-pct $coverage_limit_pct -tool qsampler -kill-time $kill_secs -opt-solver $OPT_SOLVER"

}

omt_optimathsat(){
    local database_dir=$1
    local smt2_file=$2
    local rep_id=$3

    local current_db=$(mktemp --suffix=.db --tmpdir=$database_dir)

#    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE $EVAL_DIVERSIFY_PROB_JFS $EVAL_DIVERSIFY_FREE_VARIABLES_JFS $EVAL_DIVERSIFY_EXPR_VARIABLES_JFS -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT $PASSES -smtsampler-reg-times $EVAL_SMTSAMPLER_REG_TIMES_JFS -smtsampler-threshold $EVAL_SMTSAMPLER_THRESHOLD_JFS $EVAL_SAVE_AT_EXIT -smtsampler-use-current-testcase $EVAL_SMTSAMPLER_USE_CURRENT_TESTCASE_JFS -coverage-limit-pct $coverage_limit_pct -tool qsampler -kill-time $kill_secs"
    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT -coverage-limit-pct $coverage_limit_pct -tool optimathsat -kill-time $kill_secs"

}

omt_xomt(){
    local database_dir=$1
    local smt2_file=$2
    local rep_id=$3

    local current_db=$(mktemp --suffix=.db --tmpdir=$database_dir)

#    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE $EVAL_DIVERSIFY_PROB_JFS $EVAL_DIVERSIFY_FREE_VARIABLES_JFS $EVAL_DIVERSIFY_EXPR_VARIABLES_JFS -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT $PASSES -smtsampler-reg-times $EVAL_SMTSAMPLER_REG_TIMES_JFS -smtsampler-threshold $EVAL_SMTSAMPLER_THRESHOLD_JFS $EVAL_SAVE_AT_EXIT -smtsampler-use-current-testcase $EVAL_SMTSAMPLER_USE_CURRENT_TESTCASE_JFS -coverage-limit-pct $coverage_limit_pct -tool qsampler -kill-time $kill_secs"
    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $current_db -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT -coverage-limit-pct $coverage_limit_pct -tool xomt -kill-time $kill_secs -opt-time $EVAL_SOLVER_TIMEOUT -opt-alg $OPT_SOLVER -smt-solver $SMT_SOLVER -search-type $SEARCH_TYPE"

}

sample_smtsampler(){
    local database_dir=$1
    local smt2_file=$2
    local rep_id=$3

    local database=$(mktemp --suffix=.db --tmpdir=$database_dir) 
    echo "$SAMPLE_PY -rep-id $rep_id -smt2-file $smt2_file -tag $eval_tag -database $database -max-time $EVAL_MAX_TIME -max-samples $EVAL_MAX_SAMPLES $EVAL_COVERAGE -solver-timeout $EVAL_SOLVER_TIMEOUT -max-cov-samples $EVAL_RANDOM_COVERAGE_LIMIT -coverage-limit-pct $coverage_limit_pct -tool smtsampler -kill-time $kill_secs"
}

generate_commands(){
    local dbs_dir=$1

    if [ "$tool" == "jfs" ]; then
        $RAND_BENCH_PY "$benchmark_dir" "$benchmark_n" "$skipped_files" | while read -r smt2_file; do
          for ((i=0; i<EVAL_REPETITIONS; i++))
          do
              smt2_file_abs=$(realpath $smt2_file)
              sample_jfs "$dbs_dir" "$smt2_file_abs" "$i"
          done
        done > commands.txt
    elif [ "$tool" == "smtsampler" ]; then
        $RAND_BENCH_PY "$benchmark_dir" "$benchmark_n" "$skipped_files" | while read -r smt2_file; do
          for ((i=0; i<EVAL_REPETITIONS; i++))
          do
              smt2_file_abs=$(realpath $smt2_file)
              sample_smtsampler "$dbs_dir" "$smt2_file_abs" "$i"
          done
        done > commands.txt
    elif [ "$tool" == "qsampler" ]; then
        $RAND_BENCH_PY "$benchmark_dir" "$benchmark_n" "$skipped_files" | while read -r smt2_file; do
          for ((i=0; i<EVAL_REPETITIONS; i++))
          do
              smt2_file_abs=$(realpath $smt2_file)
              sample_qsampler "$dbs_dir" "$smt2_file_abs" "$i"
          done
        done > commands.txt
    elif [ "$tool" == "xomt" ]; then
        $RAND_BENCH_PY "$benchmark_dir" "$benchmark_n" "$skipped_files" | while read -r smt2_file; do
          for ((i=0; i<EVAL_REPETITIONS; i++))
          do
              smt2_file_abs=$(realpath $smt2_file)
              omt_xomt "$dbs_dir" "$smt2_file_abs" "$i"
          done
        done > commands.txt
    elif [ "$tool" == "optimathsat" ]; then
        $RAND_BENCH_PY "$benchmark_dir" "$benchmark_n" "$skipped_files" | while read -r smt2_file; do
          for ((i=0; i<EVAL_REPETITIONS; i++))
          do
              smt2_file_abs=$(realpath $smt2_file)
              omt_optimathsat "$dbs_dir" "$smt2_file_abs" "$i"
          done
        done > commands.txt
    else
        echo "Error: $tool does not match expected values (jfs or smtsampler)."
        exit 1 
    fi
}

output_dir(){
    echo $CURRENT_DIR/../../results/$folder_name
}

usage() {
  echo "Usage: $0 --max-job-time <MAX_TIME> --config-tag <CONFIG_TAG> --eval-tag <EVAL_TAG> --tool <jfs/smtsampler> --benchmark-dir <DIR> --benchmark-n <N> --threads <N> --sampling-secs <N> --reps <N> --max-samples <N> --folder-name <FOLDER_NAME> --coverage-limit-pct <COVERAGE_PCT> --coverage-limit-n <MAX_N>"
  exit 1
}

join_dbs(){
  local dbs_folder=$1
  local output_db=$2

  # Delete empty database files created when commands were generated.
  # This is useful for single executions, otherwise joining fails.
  find $dbs_folder -type f -name "*.db" -empty -delete

  # Enable nullglob option to handle no matches
  shopt -s nullglob

  # Get the list of databases in the folder
  db_files=("$dbs_folder"/*.db)

  # Disable nullglob option after getting the list of files
  shopt -u nullglob

  echo "db_files: ${db_files[@]}"

  # Check if there are no databases in the folder
  if [ ${#db_files[@]} -eq 0 ]; then
      echo "No databases found in the folder."
      return 1
  fi

  # Check if there is only one database in the folder
  if [ ${#db_files[@]} -eq 1 ]; then
      echo "Only one database found. Copying it to the output."
      cp "${db_files[0]}" "$output_db"
      return 0
  fi

  # Initialize the output database with the first database
  cp "${db_files[0]}" "$output_db"

  # Iterate through the rest of the databases and join them
  for ((i = 1; i < ${#db_files[@]}; i++)); do
      db_b="${db_files[$i]}"
      # Run the join utility
      $JOIN_DB_SH --source-a "$output_db" --source-b "$db_b" --output "$output_db"
  done

  echo "All databases have been joined into $output_db"
}

coverage_limit_pct=100
EVAL_RANDOM_COVERAGE_LIMIT=0
# Parse command line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config-tag)
      shift
      config_tag="$1"
      ;;
    --eval-tag)
      shift
      eval_tag="$1"
      ;;
    --tool)
      shift
      tool="$1"
      ;;
    --benchmark-dir)
      shift
      benchmark_dir="$1"
      ;;
    --benchmark-n)
      shift
      benchmark_n="$1"
      ;;
    --threads)
      shift
      threads="$1"
      ;;
    --sampling-secs)
      shift
      sampling_secs="$1"
      ;;
    --reps)
      shift
      reps="$1"
      ;;
    --max-samples)
      shift
      max_samples="$1"
      ;;
    --max-job-time)
      shift
      max_job_time="$1"
      ;;
    --file-id)
      shift
      file_id="$1"
      ;;
    --rep-id)
      shift
      rep_id="$1"
      ;;
    --folder-name)
      shift
      folder_name="$1"
      ;;
    --coverage-limit-pct)
      shift
      coverage_limit_pct="$1"
      ;;
    --coverage-limit-n)
      shift
      EVAL_RANDOM_COVERAGE_LIMIT="$1"
      ;;
    --kill-secs)
      shift
      kill_secs="$1"
      ;;
    --skipped-files)
      shift
      skipped_files="$1"
      ;;
    *)
      usage
      ;;
  esac
  shift
done

# Check if both options are provided
if [[ -z "$max_job_time" || -z "$config_tag" || -z "$eval_tag" || -z "$benchmark_dir" || -z "$benchmark_n" || -z "$threads" || -z "$max_samples" || -z "$sampling_secs" || -z "$reps" || -z "$folder_name" || -z "$kill_secs" || -z "$skipped_files" ]]; then
  usage
fi

# Check if the tool is valid
if [[ "$tool" != "jfs" && "$tool" != "smtsampler" && "$tool" != "qsampler" && "$tool" != "xomt" && "$tool" != "optimathsat" ]]; then
  echo "Invalid tool. Please use either 'jfs' or 'smtsampler' or 'qsampler' or 'xomt' or 'optimathsat' for --tool."
  usage
fi

if [ ! -e "$skipped_files" ]; then
    echo "The skipped_files path '$skipped_files' does not exist."
fi

benchmark_dir=$(realpath "$benchmark_dir")

# Display the provided options
echo "CONFIG_TAG: $config_tag"
echo "EVAL_TAG: $eval_tag"
echo "TOOL: $tool"
echo "BENCHMARK_DIR: $benchmark_dir"
echo "BENCHMARK_N: $benchmark_n"
echo "THREADS: $threads"
echo "FOLDER NAME: $folder_name"
echo "KILL SECONDS: $kill_secs"
echo "SKIPPED FILES: $skipped_files"

if [ ! -d "$benchmark_dir" ]; then
    echo "Exiting: The directory $benchmark_dir does not exist."
    exit 1
fi

CONFIG_FILE=$(realpath $CURRENT_DIR/../../configs/$config_tag/$tool.sh)
source $CONFIG_FILE

export EVAL_MAX_TIME="$sampling_secs"
export EVAL_REPETITIONS="$reps"
export EVAL_MAX_SAMPLES="$max_samples"
echo "SAMPLING SECONDS: $sampling_secs"
echo "REPS: $reps"
echo "MAX_SAMPLES: $max_samples"
echo "COVERAGE LIMIT PCT: $coverage_limit_pct"
echo "EVAL_DIVERSIFY_PROB: $EVAL_DIVERSIFY_PROB"

output_file=$(output_dir)/sampling-$tool.zip
if [ -e "$output_file" ]; then
  echo "Exiting: output file already exists: $output_file"
  exit 1
fi

mkdir -p $(dirname $output_file)

working_dir=$(mktemp -d --tmpdir=/tmp/fast)
pushd $working_dir

start_time=$(date +%s)

# Genreate commands to execute by GNU parallel 
dbs_dir=$(pwd)/single-dbs
mkdir $dbs_dir
generate_commands $dbs_dir # commands written to commands.txt
cp commands.txt commands-full.txt

# To execute a single case, we extract the corresponding line from commands.txt
if [[ -n "${rep_id}" && -n "${file_id}" ]]; then
  if [ "$file_id" -ge "$benchmark_n" ]; then
      echo "file_id ($file_id) is not less than benchmark_n ($benchmark_n)."
      exit 1
  fi

  if [ "$rep_id" -ge "$EVAL_REPETITIONS" ]; then
      echo "rep_id ($file_id) is not less than eval repetitions ($EVAL_REPETITIONS)."
      exit 1
  fi

  line_number=$((file_id * EVAL_REPETITIONS + rep_id))
  sed -n "$((line_number + 1))p" "commands-full.txt" > commands.txt
fi

df -H > space.txt

mkdir logs/
set +e
# Run commands in parallel
parallel --termseq KILL --timeout $max_job_time --arg-file commands.txt --joblog parallel.log --jobs $threads 
set -e

db_file=$(pwd)/output.db
touch $db_file
join_dbs $dbs_dir $db_file

df -H >> space.txt

end_time=$(date +%s)

echo "CONFIG_TAG: $config_tag" >> parameters.txt
echo "EVAL_TAG: $eval_tag" >> parameters.txt
echo "TOOL: $tool" >> parameters.txt
echo "BENCHMARK_DIR: $benchmark_dir" >> parameters.txt
echo "BENCHMARK_N: $benchmark_n" >> parameters.txt
echo "THREADS: $threads" >> parameters.txt
echo "SAMPLING SECONDS: $sampling_secs" >> parameters.txt
echo "REPS: $reps" >> parameters.txt
echo "MAX_SAMPLES: $max_samples" >> parameters.txt

elapsed_time_seconds=$(( end_time - start_time ))
elapsed_time_minutes=$(( elapsed_time_seconds / 60 ))
echo "$elapsed_time_minutes" > time.txt

zip -r results.zip $(basename $db_file) commands.txt parallel.log parameters.txt $CONFIG_FILE time.txt space.txt logs/ commands-full.txt
mv results.zip $output_file

popd

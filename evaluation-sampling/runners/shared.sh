#JFS_EVALUATION_DIRECTORY="${JFS_EVALUATION_DIRECTORY:-$HOME/just-fuzz-it/jfs-evaluation}"
JFS_EVALUATION_DIRECTORY="${JFS_EVALUATION_DIRECTORY:-$HOME/just-fuzz-it/evaluation-sampling}" # add by yx
PARSE_JOB_ID="python3 $JFS_EVALUATION_DIRECTORY/runners/parse-job-id.py"
SAMPLING_JOB_SH="$JFS_EVALUATION_DIRECTORY/runners/sampling-job.sh"

set -e
file $SAMPLING_JOB_SH > /dev/null
set +e

function parse_job_id() {
  local job_id=$1
  local benchmarks=$2
  local eval_repetitions=$3
  local job_values_length=$4

  set -e
  FILE_ID=$($PARSE_JOB_ID "$job_id" "$benchmarks" "$eval_repetitions" "$job_values_length" "file")
  REP_ID=$($PARSE_JOB_ID "$job_id" "$benchmarks" "$eval_repetitions" "$job_values_length" "rep")
  VALUE_INDEX=$($PARSE_JOB_ID "$job_id" "$benchmarks" "$eval_repetitions" "$job_values_length" "value")
  set +e
}

function sample(){
    local TECHNIQUE=$1
    local LOGIC=$2
    local CONFIG_TAG=$3
    local EVAL_TAG=$4
    local THREADS=$5
    local MAX_TIME=$6
    local REPETITIONS=$7
    local MAX_SAMPLES=$8
    local MAX_JOB_TIME=$9

    (EVAL_CATEGORY="QF_$LOGIC" $JFS_EVALUATION_DIRECTORY/containers/eval-sampling-$TECHNIQUE.sh --max-job-time $MAX_JOB_TIME --config-tag $CONFIG_TAG --eval-tag $EVAL_TAG --benchmark-n $BENCHMARKS --threads $THREADS --sampling-secs $MAX_TIME --reps $REPETITIONS --max-samples $MAX_SAMPLES --folder-name $EVAL_TAG)
}

function sample_single(){
    local TECHNIQUE=$1
    local LOGIC=$2
    local CONFIG_TAG=$3
    local EVAL_TAG=$4
    local FOLDER_NAME=$5
    local MAX_TIME=$6
    local REPETITIONS=$7
    local MAX_SAMPLES=$8
    local MAX_JOB_TIME=$9
    local FILE_ID=${10}
    local REP_ID=${11}
    local COVERAGE_LIMIT_PCT=${12}
    local KILL_TIME=${13}
    local SKIPPED_FILES=${14}
    local BENCHMARKS=${15}
    local THREADS=1

    if [ -z "$FILE_ID" ] || [ -z "$REP_ID" ]; then
        echo "File id and rep id must not be empty"
        exit 1
    fi

    if [ "$EVAL_NO_NEW_CONTAINER" = "1" ]; then
#        local BENCHMARK_DIR="/tmp/jfs-fse-2019-artifact/data/benchmarks/3-stratified-random-sampling/benchmarks/QF_$LOGIC"
        local BENCHMARK_DIR="/tmp/benchmarks/QF_$LOGIC" # add by yx
#        /tmp/jfs-evaluation/src/evaluation/eval-sampling.sh --tool $TECHNIQUE --benchmark-dir $BENCHMARK_DIR --max-job-time $MAX_JOB_TIME --config-tag $CONFIG_TAG --eval-tag $EVAL_TAG --benchmark-n $BENCHMARKS --threads $THREADS --sampling-secs $MAX_TIME --reps $REPETITIONS --max-samples $MAX_SAMPLES --file-id $FILE_ID --rep-id $REP_ID --folder-name $FOLDER_NAME --coverage-limit-pct $COVERAGE_LIMIT_PCT --coverage-limit-n 0 --kill-secs $KILL_TIME --skipped-files $SKIPPED_FILES
        /tmp/evaluation-sampling/src/evaluation/eval-sampling.sh --tool $TECHNIQUE --benchmark-dir $BENCHMARK_DIR --max-job-time $MAX_JOB_TIME --config-tag $CONFIG_TAG --eval-tag $EVAL_TAG --benchmark-n $BENCHMARKS --threads $THREADS --sampling-secs $MAX_TIME --reps $REPETITIONS --max-samples $MAX_SAMPLES --file-id $FILE_ID --rep-id $REP_ID --folder-name $FOLDER_NAME --coverage-limit-pct $COVERAGE_LIMIT_PCT --coverage-limit-n 0 --kill-secs $KILL_TIME --skipped-files $SKIPPED_FILES
        # add by yx
    else
        (EVAL_CATEGORY="QF_$LOGIC" $JFS_EVALUATION_DIRECTORY/containers/eval-sampling-$TECHNIQUE.sh --max-job-time $MAX_JOB_TIME --config-tag $CONFIG_TAG --eval-tag $EVAL_TAG --benchmark-n $BENCHMARKS --threads $THREADS --sampling-secs $MAX_TIME --reps $REPETITIONS --max-samples $MAX_SAMPLES --file-id $FILE_ID --rep-id $REP_ID --folder-name $FOLDER_NAME --coverage-limit-pct $COVERAGE_LIMIT_PCT --coverage-limit-n 0 --kill-secs $KILL_TIME --skipped-files $SKIPPED_FILES)
    fi
}

function local_run(){
    local JOB_ID=$1
    (
        export SINGULARITY_EVAL=0
        export PBS_ARRAY_INDEX="$JOB_ID"
        export JOB_VALUES_LENGTH=${#JOB_VALUES[@]}
        export JOB_VALUES_STR="${JOB_VALUES[*]}"
        #export TOTAL_JOBS=$((JOB_VALUES_LENGTH * BENCHMARKS * EVAL_REPETITIONS))

        export TOOL="$TOOL"
        export EVAL_MAX_TIME="$EVAL_MAX_TIME"
        export EVAL_INTERNAL_KILL_TIME="$EVAL_INTERNAL_KILL_TIME"
        export EVAL_MAX_JOB_TIME="$EVAL_MAX_JOB_TIME"
        export TAG="$TAG"
        export EVAL_MAX_SAMPLES="$EVAL_MAX_SAMPLES"
        export EVAL_RANDOM_COVERAGE_LIMIT_PCT="$EVAL_RANDOM_COVERAGE_LIMIT_PCT"
        export BENCHMARKS="$BENCHMARKS"
        export EVAL_REPETITIONS="$EVAL_REPETITIONS"
        export FEATURE_TAG="$FEATURE_TAG"
        export LOGIC="$LOGIC"
        export JOB_VALUES_STR="$JOB_VALUES_STR"
        export SKIPPED_FILES="$SKIPPED_FILES"
        export BATCH_TAG="$BATCH_TAG"
        $SAMPLING_JOB_SH
    )
}

function write_job_script() {
    local dir="$1"
    local id="$2"
    local script_file="$dir/$i.sh"

    cat << EOF > $script_file
#!/bin/bash
export PBS_ARRAY_INDEX="$id"
export BATCH_TAG="$BATCH_TAG"
export SINGULARITY_EVAL="0"
export TOOL="$TOOL"
export SKIPPED_FILES="$SKIPPED_FILES"
export EVAL_MAX_TIME="$EVAL_MAX_TIME"
export EVAL_INTERNAL_KILL_TIME="$EVAL_INTERNAL_KILL_TIME"
export EVAL_MAX_JOB_TIME="$EVAL_MAX_JOB_TIME"
export TAG="$TAG"
export EVAL_MAX_SAMPLES="$EVAL_MAX_SAMPLES"
export EVAL_RANDOM_COVERAGE_LIMIT_PCT="$EVAL_RANDOM_COVERAGE_LIMIT_PCT"
export BENCHMARKS="$BENCHMARKS"
export EVAL_REPETITIONS="$EVAL_REPETITIONS"
export FEATURE_TAG="$FEATURE_TAG"
export LOGIC="$LOGIC"
export JOB_VALUES_STR="$JOB_VALUES_STR"
export JFS_EVALUATION_DIRECTORY="$JFS_EVALUATION_DIRECTORY"
export EVAL_NO_NEW_CONTAINER="1"
$SAMPLING_JOB_SH
EOF

    chmod +x $script_file
}

function local_parallel_jobs(){
    local total_jobs=$1
    local dir=$2
    local parallel_jobs=$3

    JOB_VALUES_LENGTH=${#JOB_VALUES[@]}
    JOB_VALUES_STR="${JOB_VALUES[*]}"
    TOTAL_JOBS=$((JOB_VALUES_LENGTH * BENCHMARKS * EVAL_REPETITIONS))

    for (( i=1; i<=$total_jobs; i++ ))
    do
        write_job_script $dir $i 
    done

#    find $dir -name '*.sh' | parallel -j $parallel_jobs bash
    find $dir -name '*.sh' | parallel -j $parallel_jobs 'echo "Found: {}"; bash {}'

}

function submit_job(){
    local additional_args=("$@")

    JOB_VALUES_LENGTH=${#JOB_VALUES[@]}
    JOB_VALUES_STR="${JOB_VALUES[*]}"
    TOTAL_JOBS=$((JOB_VALUES_LENGTH * BENCHMARKS * EVAL_REPETITIONS))

    job_id=$(qsub "${additional_args[@]}" -J 1-$TOTAL_JOBS -v "BATCH_TAG=$BATCH_TAG","SINGULARITY_EVAL=$SINGULARITY_EVAL","TOOL=$TOOL","SKIPPED_FILES=$SKIPPED_FILES","EVAL_MAX_TIME=$EVAL_MAX_TIME","EVAL_INTERNAL_KILL_TIME=$EVAL_INTERNAL_KILL_TIME","EVAL_MAX_JOB_TIME=$EVAL_MAX_JOB_TIME","TAG=$TAG","EVAL_MAX_SAMPLES=$EVAL_MAX_SAMPLES","EVAL_RANDOM_COVERAGE_LIMIT_PCT=$EVAL_RANDOM_COVERAGE_LIMIT_PCT","BENCHMARKS=$BENCHMARKS","EVAL_REPETITIONS=$EVAL_REPETITIONS","FEATURE_TAG=$FEATURE_TAG","LOGIC=$LOGIC","JOB_VALUES_STR='$JOB_VALUES_STR'" $SAMPLING_JOB_SH)

    echo $job_id
}

function submit_with_retry(){
    job_id=$(submit_job)
    submit_job "-W depend=afterany:$job_id"
}
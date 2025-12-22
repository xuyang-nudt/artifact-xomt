
SHARED_SH="$JFS_EVALUATION_DIRECTORY/runners/shared.sh"

set -e
source $SHARED_SH
export -f local_run
set +e

PARALLEL_JOBS=$(nproc)

EVAL_MAX_TIME="600" # This is the sampling time
EVAL_INTERNAL_KILL_TIME=$((EVAL_MAX_TIME * 5)) # This is the timeout used by the Python script that generates the output database.
EVAL_MAX_JOB_TIME=$((EVAL_INTERNAL_KILL_TIME + 60))  # This is the timeout used to guard the Python script
TAG="test-experiment"
#EVAL_MAX_SAMPLES="100000" # This is a safeguard; it is not actually reached.
EVAL_RANDOM_COVERAGE_LIMIT_PCT="100"
EVAL_REPETITIONS=1
SKIPPED_FILES="/tmp/evaluation-sampling/skip-files/skip-25-04-08.txt"
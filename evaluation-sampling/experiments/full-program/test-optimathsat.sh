#!/bin/bash
set -x

EXPERIMENT_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JFS_EVALUATION_DIRECTORY="$EXPERIMENT_SCRIPT_DIR/../.."
source "$EXPERIMENT_SCRIPT_DIR/conf.sh"

# WARNING: Given a FEATURE_TAG, the BATCH_TAGs must be incremental. Otherwise, there will be collisions.

LOGIC="program_3493"
#BENCHMARKS=1
BENCHMARKS=3493
#PARALLEL_JOBS=$(nproc)
PARALLEL_JOBS=60
MAX_JOB_ID=$((EVAL_REPETITIONS * BENCHMARKS))
    TOOL="optimathsat"
        FEATURE_TAG=optimathsat
            BATCH_TAG="600"
            EVAL_MAX_SAMPLES="600"
            JOB_VALUES=(600)
            JOB_DIR="$(mktemp -d)"
                local_parallel_jobs $MAX_JOB_ID $JOB_DIR $PARALLEL_JOBS && rm -r $JOB_DIR

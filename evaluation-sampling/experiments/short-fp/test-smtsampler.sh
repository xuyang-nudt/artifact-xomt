#!/bin/bash
set -x

EXPERIMENT_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JFS_EVALUATION_DIRECTORY="$EXPERIMENT_SCRIPT_DIR/../.."
source "$EXPERIMENT_SCRIPT_DIR/conf.sh"

# WARNING: Given a FEATURE_TAG, the BATCH_TAGs must be incremental. Otherwise, there will be collisions.

LOGIC="FP"
#BENCHMARKS=266
BENCHMARKS=4
PARALLEL_JOBS=$(nproc)
MAX_JOB_ID=$((EVAL_REPETITIONS * BENCHMARKS))
    TOOL="smtsampler"
        FEATURE_TAG=smtsampler-to
            BATCH_TAG="100"
            EVAL_MAX_SAMPLES="100"
            JOB_VALUES=(100)
            JOB_DIR="$(mktemp -d)"
                local_parallel_jobs $MAX_JOB_ID $JOB_DIR $PARALLEL_JOBS && rm -r $JOB_DIR

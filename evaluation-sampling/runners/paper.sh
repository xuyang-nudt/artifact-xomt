#!/bin/bash

SHARED_SH="$HOME/just-fuzz-it/jfs-evaluation/runners/shared.sh"

set -e
source $SHARED_SH
set +e

EVAL_MAX_TIME="300" # This is the sampling time
EVAL_INTERNAL_KILL_TIME=$((EVAL_MAX_TIME * 5)) # This is the timeout used by the Python script that generates the output database.
EVAL_MAX_JOB_TIME=$((EVAL_INTERNAL_KILL_TIME + 60))  # This is the timeout used to guard the Python script
TAG="12-09-24"
EVAL_MAX_SAMPLES="75000000"
EVAL_RANDOM_COVERAGE_LIMIT_PCT="10"
SINGULARITY_EVAL=1
EVAL_REPETITIONS=10
SKIPPED_FILES="/tmp/jfs-evaluation/skip-files/skip-empty.txt"

# WARNING: Given a FEATURE_TAG, the BATCH_TAGs must be incremental. Otherwise, there will be collisions.

LOGIC="FP"
BENCHMARKS=160
    TOOL="qsampler"
        FEATURE_TAG=qsampler-moead-60
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
        FEATURE_TAG=qsampler-nsga2-60
            JOB_VALUES=(0)
                submit_with_retry
    TOOL="jfs"
        FEATURE_TAG=smtsampler-heuristic-covfeedback
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
            JOB_VALUES=(1)
            BATCH_TAG="1"
                submit_with_retry
        FEATURE_TAG=smtsampler-heuristic-covfeedback-divexpr
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
            JOB_VALUES=(1)
            BATCH_TAG="1"
                submit_with_retry
    TOOL="smtsampler"
        FEATURE_TAG=smtsampler-to
            JOB_VALUES=(255s)
            BATCH_TAG="0"
                submit_with_retry

LOGIC="BVFP"
BENCHMARKS=702
    TOOL="qsampler"
        FEATURE_TAG=smtsampler-moead-60
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
            JOB_VALUES=(1)
            BATCH_TAG="1"
                submit_with_retry
    TOOL="jfs"
        FEATURE_TAG=smtsampler-heuristic-covfeedback
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
            JOB_VALUES=(1)
            BATCH_TAG="1"
                submit_with_retry
        FEATURE_TAG=smtsampler-heuristic-covfeedback-divexpr
            BATCH_TAG="0"
            JOB_VALUES=(0)
                submit_with_retry
            JOB_VALUES=(1)
            BATCH_TAG="1"
                submit_with_retry
    TOOL="smtsampler"
        FEATURE_TAG=smtsampler-to
            JOB_VALUES=(125s)
            BATCH_TAG="0"
                submit_with_retry
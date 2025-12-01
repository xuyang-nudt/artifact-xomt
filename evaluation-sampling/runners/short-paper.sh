#!/bin/bash

#SHARED_SH="$HOME/just-fuzz-it/jfs-evaluation/runners/shared.sh"
SHARED_SH="$HOME/just-fuzz-it/jfs-evaluation/runners/shared.sh" # add by yx

set -e
source $SHARED_SH
set +e

EVAL_MAX_TIME="300" # This is the sampling time
EVAL_INTERNAL_KILL_TIME=$((EVAL_MAX_TIME * 5)) # This is the timeout used by the Python script that generates the output database.
EVAL_MAX_JOB_TIME=$((EVAL_INTERNAL_KILL_TIME + 60))  # This is the timeout used to guard the Python script
TAG="13-08-24"
EVAL_MAX_SAMPLES="50000000"
EVAL_RANDOM_COVERAGE_LIMIT_PCT="10"
SINGULARITY_EVAL=1
BENCHMARKS=30
EVAL_REPETITIONS=10
SKIPPED_FILES="/tmp/jfs-evaluation/skip-files/skip-21-08-24.txt"
BATCH_TAG="0"

LOGIC="FP"
    TOOL="qsampler"
        JOB_VALUES=(0 2)
        FEATURE_TAG=qsampler-moead-60
        submit_with_retry
        JOB_VALUES=(0 2)
        FEATURE_TAG=qsampler-nsga2-60
        submit_with_retry
    TOOL="jfs"
        JOB_VALUES=(0 2)
        FEATURE_TAG=smtsampler-heuristic-covfeedback
        submit_with_retry
        FEATURE_TAG=smtsampler-heuristic-covfeedback-divexpr
        submit_with_retry
    TOOL="smtsampler"
        JOB_VALUES=(60s)
        FEATURE_TAG=smtsampler-to
        submit_with_retry

LOGIC="BVFP"
    TOOL="qsampler"
        JOB_VALUES=(0 2)
        FEATURE_TAG=qsampler-moead-60
        FEATURE_TAG=qsampler-nsga2-60
    TOOL="jfs"
        JOB_VALUES=(0 2)
        FEATURE_TAG=smtsampler-heuristic-covfeedback
        submit_with_retry
        FEATURE_TAG=smtsampler-heuristic-covfeedback-divexpr
        submit_with_retry
    TOOL="smtsampler"
        JOB_VALUES=(60s)
        FEATURE_TAG=smtsampler-to
        submit_with_retry
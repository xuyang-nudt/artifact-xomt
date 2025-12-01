#!/bin/bash

SHARED_SH="$HOME/just-fuzz-it/jfs-evaluation/runners/shared.sh"

set -e
source $SHARED_SH
set +e

EVAL_MAX_TIME="300" # This is the sampling time
EVAL_INTERNAL_KILL_TIME=$((EVAL_MAX_TIME * 5)) # This is the timeout used by the Python script that generates the output database.
EVAL_MAX_JOB_TIME=$((EVAL_INTERNAL_KILL_TIME + 60))  # This is the timeout used to guard the Python script
TAG="04-09-24"
EVAL_MAX_SAMPLES="50000000"
EVAL_RANDOM_COVERAGE_LIMIT_PCT="10"
SINGULARITY_EVAL=1
EVAL_REPETITIONS=10
SKIPPED_FILES="/tmp/jfs-evaluation/skip-files/skip-21-08-24.txt"
BATCH_TAG="0"

FEATURE_TAG=smtsampler-to
JOB_VALUES=(5s 15s 25s 35s 45s 55s 65s 75s 85s 95s 105s 115s 125s 135s 145s 155s 165s 175s 185s 195s 205s 215s 225s 235s 245s 255s 265s 275s 285s 295s)
TOOL="smtsampler"

BENCHMARKS=30

LOGIC="FP"
        submit_with_retry

LOGIC="BVFP"
        submit_with_retry
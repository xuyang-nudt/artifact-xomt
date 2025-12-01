#!/bin/bash
#PBS -l select=1:ncpus=1:mem=8gb:cpu_type=rome:filesystem_type=gpfs
#PBS -l walltime=00:31:00

#JFS_EVALUATION_DIRECTORY="${JFS_EVALUATION_DIRECTORY:-$HOME/just-fuzz-it/jfs-evaluation}"
JFS_EVALUATION_DIRECTORY="${JFS_EVALUATION_DIRECTORY:-$HOME/just-fuzz-it/evaluation-sampling}" # add by yx

if [ -z "${HOME}" ]; then
  echo "Error: HOME is not set"
  exit 1
fi

if [ -z "${PBS_ARRAY_INDEX}" ]; then
  echo "Error: PBS_ARRAY_INDEX is not set"
  exit 1
else
  echo "Executing PBS_ARRAY_INDEX ${PBS_ARRAY_INDEX}"
fi

if [ -z "${BATCH_TAG}" ]; then
  echo "Error: BATCH_TAG is not set"
  exit 1
else
  echo "BATCH_TAG is ${BATCH_TAG}"
fi

if [ -z "${FEATURE_TAG}" ]; then
  echo "Error: FEATURE_TAG is not set"
  exit 1
else
  echo "FEATURE_TAG is ${FEATURE_TAG}"
fi

if [ -z "${LOGIC}" ]; then
  echo "Error: LOGIC is not set"
  exit 1
else
  echo "LOGIC is ${LOGIC}"
fi

if [ -z "$JOB_VALUES_STR" ]; then
  echo "Error: JOB_VALUES_STR is not defined."
  exit 1
fi

if [ -z "$SKIPPED_FILES" ]; then
  echo "Error: SKIPPED_FILES is not defined."
  exit 1
fi


IFS=' ' read -r -a JOB_VALUES <<< "$JOB_VALUES_STR"

if [ -z "$BENCHMARKS" ]; then
  echo "Error: BENCHMARKS is not defined."
  exit 1
fi

if [ -z "$EVAL_REPETITIONS" ]; then
  echo "Error: EVAL_REPETITIONS is not defined."
  exit 1
fi

if [ -z "$EVAL_MAX_TIME" ]; then
  echo "Error: EVAL_MAX_TIME is not defined."
  exit 1
fi

if [ -z "$EVAL_INTERNAL_KILL_TIME" ]; then
  echo "Error: EVAL_INTERNAL_KILL_TIME is not defined."
  exit 1
fi

if [ -z "$EVAL_MAX_JOB_TIME" ]; then
  echo "Error: EVAL_MAX_JOB_TIME is not defined."
  exit 1
fi

if [ -z "$TAG" ]; then
  echo "Error: TAG is not defined."
  exit 1
fi

if [ -z "$EVAL_MAX_SAMPLES" ]; then
  echo "Error: EVAL_MAX_SAMPLES is not defined."
  exit 1
fi

if [ -z "$EVAL_RANDOM_COVERAGE_LIMIT_PCT" ]; then
  echo "Error: EVAL_RANDOM_COVERAGE_LIMIT_PCT is not defined."
  exit 1
fi

if [ -z "$TOOL" ]; then
  echo "Error: TOOL is not defined."
  exit 1
fi

if [ -z "$SINGULARITY_EVAL" ]; then
  echo "Error: SINGULARITY_EVAL is not defined."
  exit 1
fi

if [ "$SINGULARITY_EVAL" = "1" ]; then
    export FASTTMP="$TMPDIR"
else
    export FASTTMP="/tmp/fast"
fi

export SINGULARITY_EVAL="$SINGULARITY_EVAL"

echo "TMPDIR is $TMPDIR"
echo "FASTTMP is $FASTTMP"
echo JOB_VALUES_LENGTH=${#JOB_VALUES[@]}

source "$JFS_EVALUATION_DIRECTORY/runners/shared.sh"

####################################### CONFIGURE ACCORDINGLY #######################################
INIT_JOB_ID=${PBS_ARRAY_INDEX}
JOB_ID=$((INIT_JOB_ID - 1)) # MAKE IT ZERO BASED
#####################################################################################################

JOB_VALUES_LENGTH=${#JOB_VALUES[@]}

echo "Job value selected ${JOB_VALUES}"

# Defines variables FILE_ID, REP_ID and VALUE_INDEX
parse_job_id "$JOB_ID" "$BENCHMARKS" "$EVAL_REPETITIONS" "$JOB_VALUES_LENGTH"

echo "Job id parsed: FILE_ID $FILE_ID REP_ID $REP_ID VALUE_INDEX $VALUE_INDEX"

JOB_VALUE=${JOB_VALUES[$VALUE_INDEX]}

CONFIG_TAG="$FEATURE_TAG/$JOB_VALUE"
EVAL_TAG="$TAG-$TOOL-$FEATURE_TAG$JOB_VALUE"-"$LOGIC"
FOLDER_NAME="$TAG-$TOOL-$FEATURE_TAG-$BATCH_TAG-$VALUE_INDEX-$INIT_JOB_ID-$LOGIC"

OUTPUT_RESULT_FILE="$JFS_EVALUATION_DIRECTORY/results/$FOLDER_NAME/sampling-$TOOL.zip"
#if [ -e "$OUTPUT_RESULT_FILE" ]; then
#  echo "Exiting: output file already exists: $OUTPUT_RESULT_FILE"
#  exit 0
#fi
#
time sample_single "$TOOL" "$LOGIC" "$CONFIG_TAG" "$EVAL_TAG" "$FOLDER_NAME" "$EVAL_MAX_TIME" "$EVAL_REPETITIONS" "$EVAL_MAX_SAMPLES" "$EVAL_MAX_JOB_TIME" "$FILE_ID" "$REP_ID" "$EVAL_RANDOM_COVERAGE_LIMIT_PCT" "$EVAL_INTERNAL_KILL_TIME" "$SKIPPED_FILES" "$BENCHMARKS"

#if [ -e "$OUTPUT_RESULT_FILE" ]; then
#  echo "[add by yx] Info: Output file exists, skipping sampling: $OUTPUT_RESULT_FILE"
#elif [ "$TOOL" != "moceasp2" ]; then
#  echo "[add by yx] Info: TOOL is not moceasp2, skipping sampling"
#else
#  echo "[add by yx] Info: sampling execution"
#  echo '123' | sudo -S rm -f "$OUTPUT_RESULT_FILE"
#  time sample_single "$TOOL" "$LOGIC" "$CONFIG_TAG" "$EVAL_TAG" "$FOLDER_NAME" \
#                     "$EVAL_MAX_TIME" "$EVAL_REPETITIONS" "$EVAL_MAX_SAMPLES" \
#                     "$EVAL_MAX_JOB_TIME" "$FILE_ID" "$REP_ID" \
#                     "$EVAL_RANDOM_COVERAGE_LIMIT_PCT" "$EVAL_INTERNAL_KILL_TIME" \
#                     "$SKIPPED_FILES" "$BENCHMARKS"
#fi

#if [ "$FEATURE_TAG" = "qsampler-moceasp2" ]; then
#  echo "[add by yx] Info: TOOL is moceasp2, execution sampling"
#  echo '123' | sudo -S rm -f "$OUTPUT_RESULT_FILE"
#
#  time sample_single "$TOOL" "$LOGIC" "$CONFIG_TAG" "$EVAL_TAG" "$FOLDER_NAME" \
#                     "$EVAL_MAX_TIME" "$EVAL_REPETITIONS" "$EVAL_MAX_SAMPLES" \
#                     "$EVAL_MAX_JOB_TIME" "$FILE_ID" "$REP_ID" \
#                     "$EVAL_RANDOM_COVERAGE_LIMIT_PCT" "$EVAL_INTERNAL_KILL_TIME" \
#                     "$SKIPPED_FILES" "$BENCHMARKS"
#fi
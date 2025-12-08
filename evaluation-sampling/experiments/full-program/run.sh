#!/bin/bash
set -x

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JFS_EVALUATION_DIRECTORY="$RUN_DIR/../../"

EXPERIMENT_TAG="full-program"

$RUN_DIR/../optimathsat-container.sh /tmp/evaluation-sampling/experiments/$EXPERIMENT_TAG/test-optimathsat.sh
$RUN_DIR/../qsampler-container.sh /tmp/evaluation-sampling/experiments/$EXPERIMENT_TAG/test-qsampler.sh

$RUN_DIR/../qsampler-container.sh /tmp/evaluation-sampling/src/sqlite/join-all-dbs.sh --input-dir /tmp/evaluation-sampling/results --output-db /tmp/evaluation-sampling/results/output.db
mv $JFS_EVALUATION_DIRECTORY/results/ $JFS_EVALUATION_DIRECTORY/results-$EXPERIMENT_TAG

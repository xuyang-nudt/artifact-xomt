#!/bin/bash

set -x
set -e

IMAGE=optimathsat-build:ubuntu1804
SRC_PATH=/home/aaa/optimathsat/bin/optimathsat
CURRENT_DIR=$(dirname "$(readlink -f "$0")")

if [ -z "$FASTTMP" ]; then
  FASTTMP=/tmp/fast
fi

mkdir -p $FASTTMP
JFSTMP=$(mktemp -d "${FASTTMP}/tmp.XXXXXXXXXX")
chmod 775 "$JFSTMP"

cleanup() {
    local folder_path="$1"
    if [ -d "$folder_path" ]; then
        echo "Deleting folder: $folder_path"
#        echo "No delete JFS tmp.*"
        echo "123" | sudo -S rm -rf "$folder_path"
    fi
}

trap "cleanup '$JFSTMP'" EXIT

#docker run --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../../jfs:$SRC_PATH -v $CURRENT_DIR/../:/tmp/jfs-evaluation -v $CURRENT_DIR/../../jfs-fse-2019-artifact:/tmp/jfs-fse-2019-artifact $IMAGE $@

#Mount /tmp/fast to store output files.
#Mount Sampler for just-in-time debugging. Run local sampler instead of sampler in docker.
#Mount evaluation-sampling.
#Mount benchmarks.
#docker run --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../../JFSampler:$SRC_PATH -v $CURRENT_DIR/../:/tmp/evaluation-sampling -v $CURRENT_DIR/../../benchmarks:/tmp/benchmarks $IMAGE $@
docker run --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../:/tmp/evaluation-sampling -v $CURRENT_DIR/../../benchmarks:/tmp/benchmarks $IMAGE $@
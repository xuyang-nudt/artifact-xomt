#!/bin/bash

set -x
set -e

IMAGE=xomt-build:ubuntu1804
SRC_PATH=/home/aaa/xomt
CURRENT_DIR=$(dirname "$(readlink -f "$0")")

if [ -z "$FASTTMP" ]; then
  FASTTMP=/tmp/fast
fi

mkdir -p $FASTTMP
JFSTMP=$(mktemp -d "${FASTTMP}/tmp.XXXXXXXXXX")
#chmod 775 "$JFSTMP"

cleanup() {
    local folder_path="$1"
    if [ -d "$folder_path" ]; then
#        echo "No delete folder: $folder_path"
        echo "Deleting folder: $folder_path"
        echo "123" | sudo -S rm -rf "$folder_path"
    fi
}

trap "cleanup '$JFSTMP'" EXIT

#docker run --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../../QSampler/qsampler:$SRC_PATH -v $CURRENT_DIR/../:/tmp/jfs-evaluation -v $CURRENT_DIR/../../benchmarks:/tmp/jfs-fse-2019-artifact $IMAGE $@

#docker run --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../../QSampler/qsampler:$SRC_PATH -v $CURRENT_DIR/../:/tmp/evaluation-sampling -v $CURRENT_DIR/../../benchmarks:/tmp/benchmarks $IMAGE $@
docker run --log-opt max-size=10m --log-opt max-file=1 --user root --rm -it -v $JFSTMP:/tmp/fast -v $CURRENT_DIR/../:/tmp/evaluation-sampling -v $CURRENT_DIR/../../benchmarks:/tmp/benchmarks $IMAGE $@


## 必须使用 sudo，因为这些目录权限是 710 (drwx--x---)
#sudo du -ah /var/lib/docker/containers | grep "json.log$" | sort -hr | head -n 10
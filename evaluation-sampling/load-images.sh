#!/bin/bash
set -e

CURRENT_DIR=$(dirname "$(readlink -f "$0")")

pushd $CURRENT_DIR
cat images/qsampler_1804.tar | docker load
cat images/jfsampler_1804.tar | docker load
cat images/smtsampler_1804.tar | docker load
popd
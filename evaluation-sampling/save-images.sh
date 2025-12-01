#!/bin/bash
set -e

CURRENT_DIR=$(dirname "$(readlink -f "$0")")

pushd $CURRENT_DIR

mkdir -p images/
#docker save aaa_base_build:ubuntu1804 > images/aaa_base_build_1804.tar
#docker save qsampler-build:ubuntu1804 > images/qsampler_1804.tar
#docker save jfs_sampling_build:ubuntu1804 > images/jfsampler_1804.tar
#docker save jfs-smt-sampler:ubuntu1804 > images/smtsampler_1804.tar
docker save optimathsat-build:ubuntu1804 > images/optimathsat_1804.tar
docker save xomt-build:ubuntu1804 > images/xmot_1804.tar
popd


## Artifact Overview

Our experimental data were obtained on multiple servers equipped with Intel(R) Xeon(R) Gold 6458Q 128-core CPUs @ 3.1GHz and 512GB of memory. It might be impractical to obtain all the evaluation data within a short period on a personal computer.
To address this, we provide two methods for evaluation:

1. **Short Evaluation**: A quick test to verify the artifact's functional correctness. While this does not guarantee exact final results, in our case, it reflected the overall trend of the final outcomes.  
2. **Full Evaluation**: Comprehensive instructions to replicate the complete evaluation process.

## Getting Started

To evaluate this artifact, please follow these sections in the provided order:
- **Requirements**: Details the dependencies and setup needed.
- **Short Evaluation**: Conducts a preliminary verification.

## Requirements

Our evaluation has been tested for `x86-64` and `Ubuntu 18..04 LTS`. 

To run the evaluation, the following is required:
* [Docker](https://docs.docker.com/engine/install/).
    * Tested on version `24.0.2, build cb74dfc`
* bash

Load the Docker images for the following steps:

1. Change directory: `cd evaluation-sampling/`
2. The baselines and QSampler used in this experiment have been containerized as Docker images. You can pull them from dockerhub by running the following commands:
```
docker pull dockerqsf/jfs-smt-sampler:ubuntu1804
docker pull dockerqsf/jfs_sampling_build:ubuntu1804
docker pull dockerqsf/qsampler-build:ubuntu1804
```
3. The pulled images need to be renamed. Execute the following commands:
```
docker tag dockerqsf/jfs-smt-sampler:ubuntu1804 jfs-smtsampler:ubuntu1804
docker tag dockerqsf/jfs_sampling_build:ubuntu1804 jfs_sampling_build:ubuntu1804
docker tag dockerqsf/qsampler-build:ubuntu1804 qsampler-build:ubuntu1804
```

## Short Evaluation

This is a scaled evaluation to ensure functional correctness. It will run the tools on four formulas for each suite, two time per formula. 

1. Change directory: `cd evaluation-sampling/experiments/`
2. Run the tools on the FP suite: `./short-fp/run.sh`
3. After a brief run, the results are saved in the `output.db` file located in the directory `../results-short-fp/`. You will need to install `sqlite3` to open it.
4. Run the tools on the real-world program suite: `./short-program/run.sh`
5. After a brief run, the results are saved in the `output.db` file located in the directory `../results-short-program/`. You will need to install `sqlite3` to open it.
6. Delete the result folders: `rm -r ./results-short-fp/` and `rm -r ./results-short-program`. Otherwise, if the short evaluation is executed again it will fail.

## Full-scale Evaluation (Optional)

This is a comprehensive evaluation that will obtain all the data presented in the paper.

1. Change directory: `cd evaluation-sampling/experiments/`
2. The tool is executed to obtain the SMT coverage trend graph as the number of samples increases.: `./full-fp/run.sh` and `./full-program/run.sh`
3. After the execution is completed, we obtain two `output.db` files in the paths `../results-full-fp` and `../results-full-program`, respectively. Then, by running `plot_trend.py`, we can generate Figures 6 and 7 as presented in the paper. It is worth noting that the `config` in `plot_trend.py` needs to be manually modified.
4. The tool is executed to obtain the box plot of SMT coverage distribution.: `./full-fp-2000/run.sh` and `./full-program-2000/run.sh`
5. After the execution is completed, we obtain two `output.db` files in the paths `../results-full-fp` and `../results-full-program`, respectively. Then, by running `plot_box.py`, we can generate Figures 8 and 9 as presented in the paper. It is worth noting that the `config` in `plot_box.py` needs to be manually modified.
6. Delete the result folders: `rm -r ./results-full-fp/` and `rm -r ./results-full-program`. Otherwise, if the short evaluation is executed again it will fail.

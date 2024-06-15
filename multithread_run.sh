#!/bin/bash
export OPENBLAS_NUM_THREADS=1
export GOTO_NUM_THREADS=1
export OMP_NUM_THREADS=1
source autogluon/bin/activate
python /hdd/home/mzarantonello/stage/signature_inference/scripts/multithread_exposureInference.py

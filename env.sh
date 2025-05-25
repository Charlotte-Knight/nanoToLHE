#!/usr/bin/env bash

if [ -d "pylhe_env" ]; then
  export MAMBA_ROOT_PREFIX=${PWD}/pylhe_env
  eval "$(./pylhe_env/micromamba shell hook -s posix)"
  micromamba activate pylhe
else
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
  mv bin pylhe_env
  export MAMBA_ROOT_PREFIX=${PWD}/pylhe_env
  eval "$(./pylhe_env/micromamba shell hook -s posix)"
  micromamba env create -n pylhe -c conda-forge pylhe uproot -y
  micromamba activate pylhe
fi
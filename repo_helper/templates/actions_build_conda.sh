#!/bin/bash
# {{ managed_message }}

set -e -x

python -m repo_helper make-recipe || exit 1

# Switch to miniconda
source "/home/runner/miniconda/etc/profile.d/conda.sh"
hash -r
conda activate base
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install conda-build
conda install anaconda-client
conda info -a
{% for channel in conda_channels %}
conda config --add channels {{ channel }} || exit 1{% endfor %}

conda build conda {% for channel in conda_channels %}-c {{ channel }} {% endfor %}--output-folder conda/dist --skip-existing

exit 0

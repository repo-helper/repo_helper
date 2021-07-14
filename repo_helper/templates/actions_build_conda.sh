#!/bin/bash
# {{ managed_message }}

set -e -x

python -m mkrecipe --type wheel || exit 1

# Switch to miniconda
source "/home/runner/miniconda/etc/profile.d/conda.sh"
hash -r
conda activate base
conda config --set always_yes yes --set changeps1 no
conda install conda=4.8.5 conda-build=3.18.11
conda info -a
{% for channel in conda_channels %}
conda config --add channels {{ channel }} || exit 1{% endfor %}
conda config --remove channels defaults

conda build conda {% for channel in conda_channels %}-c {{ channel }} {% endfor %}--output-folder conda/dist --skip-existing

exit 0

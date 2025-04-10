FROM ubuntu:24.04

ENV PYTHON_VERSION=3.8.18
ENV STAGE="production"

WORKDIR /opt/python-aodndata/

# COPY stage_requirements.txt ./

# update apt-cache
RUN apt-get update && \
        apt-get install -y software-properties-common --no-install-recommends && \
        add-apt-repository -y -u ppa:ubuntugis/ubuntugis-unstable
#    rm -rf /var/lib/apt/lists/*

# install additional required packages
RUN apt-get install -y --no-install-recommends \
        libudunits2-dev \
        libproj-dev \
        libgeos-dev \
        libffi-dev \
        cmake \
        libgtest-dev \
        build-essential \
        curl \
        libcurl4-openssl-dev \
        git \
        libmagic1

# Set up Python using uv

# install uv & create python venv with pip
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH=$HOME/.local/bin:$PATH && \
    uv venv --python=$PYTHON_VERSION $HOME/.venv

#### Pyenv
# Set-up necessary Env vars for PyEnv
#ENV PYENV_ROOT="$PWD/.pyenv"
#ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
#
## Install pyenv
#RUN set -ex \
#    && curl https://pyenv.run | bash \
#    && pyenv install $PYTHON_VERSION \
#    && pyenv global $PYTHON_VERSION \
#    && pyenv rehash \
#    && chmod -R a+w $PYENV_ROOT/shims

# Install Python dependencies
SHELL ["/bin/bash", "-c"]
RUN source "$HOME/.venv/bin/activate" && \
    export PATH=$HOME/.local/bin:$PATH && \
    uv pip install pip==24.0 && \
    pip install pytest-runner pyshp scipy

# Mount the local directory to the container
RUN --mount=type=bind,source=.,target=/opt/python-aodndata,rw \
    source "$HOME/.venv/bin/activate" && \
    pip install -r stage_requirements.txt


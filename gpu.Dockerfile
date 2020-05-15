# Dockerfile

FROM ubuntu:18.04

ENV CONDA="/root/miniconda3"
ENV PATH="${CONDA}/bin:${PATH}"
ARG PATH="${CONDA}/bin:${PATH}"

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install -y wget && \
       rm -rf /var/lib/apt/lists/*

# install conda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -p /root/miniconda3 -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN source ~/.bashrc \
    && conda update -y conda \
    && conda init bash \
    && source ~/.bashrc

# conda environments
WORKDIR /app
ADD ./gpu.environments.yml /app/
ENV ENV_PREFIX /app/env
RUN conda env create --prefix $ENV_PREFIX -f /app/gpu.environments.yml --force \
    && conda clean --all --yes \
    && conda init bash \
    && source activate $ENV_PREFIX

# copy sources
COPY ./pdf_api /app/pdf_api
COPY ./models /app/pdf_api

WORKDIR /app/pdf_api

CMD ["python", "main.py"]
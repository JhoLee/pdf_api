# Dockerfile

FROM ubuntu:18.04
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update && \
    apt-get install -y wget && \
       rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -p /root/miniconda3 -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda update -y conda \
    && conda init bash


COPY ./* /app/
COPY models /app/models
COPY environments.yml environments.yml
ENV ENV_PREFIX $PWD/env
RUN conda env create --prefix $ENV_PREFIX -f environments.yml --force && \
    conda clean --all --yes
RUN conda init bash \
    && conda activate $ENV_PREFIX

WORKDIR /app

CMD ["python", "main.py"]
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
# conda environments
COPY environments.gpu.yml /app/environments.yml
COPY models /app/models
ENV ENV_PREFIX $PWD/env
RUN conda env create --prefix $ENV_PREFIX -f /app/environments.yml --force && \
    conda clean --all --yes
RUN conda init bash \
    && source /home/$USER/.bashrc \
    && conda activate $ENV_PREFIX

# source
COPY pdf_api /app/pdf_api

WORKDIR /app/pdf_api

CMD ["python", "main.py"]
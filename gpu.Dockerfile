# Dockerfile

FROM ubuntu:18.04
ENV PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update && \
    apt-get install -y wget && \
       rm -rf /var/lib/apt/lists/*

# install conda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -p /root/miniconda3 -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN /bin/bash -c "source ~/.bashrc" \
    && conda update -y conda \
    && conda init bash \
    && /bin/bash -c "source ~/.bashrc"

# conda environments
COPY gpu.environments.yml /app/environments.yml
ENV ENV_PREFIX /app/env
RUN conda env create --prefix $ENV_PREFIX -f /app/environments.yml --force && \
    conda clean --all --yes
RUN conda init bash \
    && source /home/$USER/.bashrc \
    && conda activate $ENV_PREFIX

# copy sources
COPY pdf_api /app/pdf_api
COPY models /app/models

WORKDIR /app/pdf_api

CMD ["python", "main.py"]
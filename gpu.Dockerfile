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
WORKDIR /app
ADD ./gpu.environments.yml /app/
ENV ENV_PREFIX /app/env
RUN conda env create --prefix $ENV_PREFIX -f /app/environments.yml --force && \
    conda clean --all --yes

# copy sources
ADD ./pdf_api /app/
ADD ./models /app/

WORKDIR /app/pdf_api

CMD ["python", "main.py"]
# Dockerfile

FROM ubuntu:18.04
MAINTAINER Jho Lee "jho.lee@kakao.com"


ENV CONDA="/root/miniconda3"
ENV PATH="${CONDA}/bin:${PATH}"
ARG PATH="${CONDA}/bin:${PATH}"

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install -y wget && \
       rm -rf /var/lib/apt/lists/*
WORKDIR /app

# copy sources
COPY ./pdf_api /app/pdf_api
COPY ./models /app/models

# install conda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -p /root/miniconda3 -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

#RUN curl -O -J -L \
#    https://bit.ly/pytorch_mrcnn_coco_pth \
# && mv mask_rcnn_coco.pth models

RUN source ~/.bashrc \
    && conda update -y conda \
    && conda init bash \
    && source ~/.bashrc

# conda environments
RUN conda install -c pytorch \
        pytorch \
        torchvision \
        cudatoolkit \
        cudnn \
 && conda install \
        opencv \
        Pillow \
        tqdm \
        django \
        Celery \
        Cython \
        matplotlib \
 && conda clean -afy \
 && pip install --no-cache-dir \
        segmentation-models-pytorch==0.1.0 \
        djangorestframework==3.11.0 \
        markdown==3.2.2 \
        django-filter==2.2.0


WORKDIR /app/pdf_api

RUN python gen_secret_key.py && \
    python init_torch.py


RUN python manage.py makemigrations && \
    python manage.py migrate
CMD ["python", "manage.py", "runserver", "0:8000"]

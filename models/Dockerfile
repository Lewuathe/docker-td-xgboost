FROM continuumio/miniconda3:latest

MAINTAINER Kai Sasaki <lewuathe@me.com>

USER root

# libav-tools for matplotlib anim
RUN apt-get update && \
    apt-get install -y --no-install-recommends libav-tools git make gcc g++ unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --upgrade --user awscli
ENV PATH /root/.local/bin:$PATH
RUN pip install boto3
RUN pip install td-client certifi
RUN pip install numpy scipy sklearn

# Install XGBoost library
RUN git clone --recursive https://github.com/dmlc/xgboost && \
    cd xgboost && \
    make -j4 && \
    cd python-package; python setup.py install

ADD xgb.py /root/xgb.py

WORKDIR /root

ENTRYPOINT ["python", "xgb.py"]

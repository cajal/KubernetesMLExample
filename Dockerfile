FROM nvidia/cuda:10.0-runtime-ubuntu18.04
LABEL maintainer="Synicix"

# Github username and password
ARG username
ARG password

# Ubuntu OS Requirements
RUN apt-get -y update
RUN apt-get -y install python3.6
RUN apt -y install python3-pip
RUN apt -y install git

# Install python dependices
RUN pip3 install h5py opencv-python seaborn pandas datajoint jupyter

# Pytorch
RUN pip3 install https://download.pytorch.org/whl/cu100/torch-1.1.0-cp36-cp36m-linux_x86_64.whl
RUN pip3 install https://download.pytorch.org/whl/cu100/torchvision-0.3.0-cp36-cp36m-linux_x86_64.whl

# Apex FP16 pytorch library
RUN pip3 install git+https://www.github.com/nvidia/apex

# Clone the GitHub respitory and set workdir to that
RUN git clone https://${username}:${password}@github.com/cajal/KubernetesMLExample.git
WORKDIR /KubernetesMLExample
FROM ubuntu:18.04

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Basic packages
RUN apt-get update && apt-get install -y \
    bash \
    sudo \
    ca-certificates \
    curl \
    wget \
    gnupg \
    libx11-xcb1 \
    libxkbfile1 \
    libgtk-3-0 \
    libnss3 \
    libasound2 \
    libxss1 \
    libgbm1 \
    xauth \
    xdg-utils \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    build-essential \
    jq \
    vim \
    apt-utils \
    tmux \
    net-tools \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
 && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && rm -rf /var/lib/apt/lists/*

# Gstreamer
RUN apt-get update && \
	apt-get install -y \
	libgstreamer1.0-dev \
	libgstreamer-plugins-base1.0-dev \
	libgstreamer-plugins-bad1.0-dev \
	gstreamer1.0-plugins-base \
	gstreamer1.0-plugins-good \
	gstreamer1.0-plugins-bad \
	gstreamer1.0-plugins-ugly \
	gstreamer1.0-libav \
	gstreamer1.0-tools \
	gstreamer1.0-x \
	gstreamer1.0-alsa \
	gstreamer1.0-gl \
	gstreamer1.0-gtk3 \
	gstreamer1.0-qt5 \
	gstreamer1.0-pulseaudio \
	    && rm -rf /var/lib/apt/lists/*
	    
# Opencv
RUN apt-get update && \
	apt-get install -y libgl1-mesa-glx &&\
	pip3 install --upgrade pip && \
	pip3 install opencv-python==4.6.0.66
	

# Create group and user
RUN groupadd --gid ${GID} ${USERNAME} \
    && useradd --uid ${UID} --gid ${GID} -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

# Switch to user
USER ${USERNAME}
WORKDIR /home/${USERNAME}
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt


	
COPY code_1.85.2-1705561292_amd64.deb .
RUN sudo apt install ./code_1.85.2-1705561292_amd64.deb

RUN sudo ln -s /usr/bin/python3 /usr/bin/python
RUN sudo ln -s /usr/bin/pip3 /usr/bin/pip

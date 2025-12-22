FROM ubuntu:18.04

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Basic packages
RUN apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*

# Create group and user
RUN groupadd --gid ${GID} ${USERNAME} \
    && useradd --uid ${UID} --gid ${GID} -m ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

# Switch to user
USER ${USERNAME}
WORKDIR /home/${USERNAME}

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY code_1.85.2-1705561292_amd64.deb .
RUN sudo apt install ./code_1.85.2-1705561292_amd64.deb


# Base image
FROM ubuntu:20.04

# Pas d’interactions apt
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true

# Mise à jour et dépendances
RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -y \
      git build-essential libtool-bin libglib2.0-dev \
      wget autoconf automake bison curl clang make unzip \
      pkg-config libfdt-dev libpixman-1-dev \
      python3 vim-common

# Variables d’environnement
ENV SLOTH_WORK_DIR=/sloth/src \
    ANDROID_NDK_HOME=/opt/android-ndk

# Préparation du workspace
WORKDIR ${SLOTH_WORK_DIR}

# 1) Cloner QEMU (avec les patchs à venir)
RUN git clone --depth 1 --branch v5.1.0 https://github.com/qemu/qemu.git qemu

# 2) Récupérer LibFuzzer (compiler-rt/lib/fuzzer) par Git
WORKDIR ${SLOTH_WORK_DIR}/fuzzer
RUN git clone --depth 1 --branch release/12.x https://github.com/llvm/llvm-project.git /tmp/llvm-project && \
    cp -r /tmp/llvm-project/compiler-rt/lib/fuzzer/* . && \
    rm -rf /tmp/llvm-project

# 3) Installer Android NDK
WORKDIR ${SLOTH_WORK_DIR}
RUN curl -LO https://dl.google.com/android/repository/android-ndk-r21d-linux-x86_64.zip && \
    unzip android-ndk-r21d-linux-x86_64.zip && \
    mv android-ndk-r21d ${ANDROID_NDK_HOME} && \
    rm android-ndk-r21d-linux-x86_64.zip

# Ajouter le NDK au PATH
ENV PATH=${PATH}:${ANDROID_NDK_HOME}

# 4) Ajouter le code Sloth (sloth.c + Makefile)
ADD src/sloth.c ${SLOTH_WORK_DIR}/
ADD src/Makefile ${SLOTH_WORK_DIR}/

# 5) Appliquer le patch Sloth sur QEMU
ADD resources/patches/qemu.patch /setup/qemu.patch
WORKDIR ${SLOTH_WORK_DIR}/qemu
RUN git apply --stat /setup/qemu.patch && \
    git apply --check /setup/qemu.patch && \
    git apply /setup/qemu.patch

# 6) Appliquer le patch Sloth sur LibFuzzer
ADD resources/patches/libfuzzer.patch /setup/libfuzzer.patch
WORKDIR ${SLOTH_WORK_DIR}/fuzzer
RUN git apply --stat /setup/libfuzzer.patch && \
    git apply --check /setup/libfuzzer.patch && \
    git apply /setup/libfuzzer.patch

# 7) Retour au workspace principal
WORKDIR ${SLOTH_WORK_DIR}

# 8) Ajouter le script de fuzzing
ADD src/fuzz_runner.py /sloth/src/

# 9) Ouvrir un shell interactif pour compiler manuellement
RUN /bin/bash
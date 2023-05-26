# docker build -t whisper-webui --build-arg WHISPER_IMPLEMENTATION=whisper .

# Start with the nvidia/cuda image as base
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu20.04 as base

# Latest version of transformers-pytorch-gpu seems to lack tk. 
# Further, pip install fails, so we must upgrade pip first.
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y git-all
RUN apt-get install -y python3 python3-pip python3-tk
RUN python3 -m pip install --upgrade pip
RUN apt-get install -y ffmpeg

EXPOSE 7860

ARG WHISPER_IMPLEMENTATION=faster-whisper
ENV WHISPER_IMPLEMENTATION=${WHISPER_IMPLEMENTATION}

ADD requirements-fasterWhisper.txt /opt/whisper-webui/
ADD requirements-whisper.txt /opt/whisper-webui/
RUN if [ "${WHISPER_IMPLEMENTATION}" = "whisper" ]; then \
    python3 -m pip install -r /opt/whisper-webui/requirements-whisper.txt; \
  else \
    python3 -m pip install -r /opt/whisper-webui/requirements-fasterWhisper.txt; \
  fi

ADD . /opt/whisper-webui/
# Note: Models will be downloaded on demand to the directory /root/.cache/whisper.
# You can also bind this directory in the container to somewhere on the host.

# To be able to see logs in real time
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/whisper-webui/
ENTRYPOINT ["python3"]

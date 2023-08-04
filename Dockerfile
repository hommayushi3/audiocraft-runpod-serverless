FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir data
RUN apt-get install ffmpeg -y
WORKDIR /data

# Install Python dependencies (Worker Template)
RUN pip install --upgrade pip && \
    pip install git+https://git@github.com/facebookresearch/audiocraft#egg=audiocraft runpod

COPY handler.py /data/handler.py

CMD [ "python", "-m", "handler" ]

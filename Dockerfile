FROM python:3.9.1-buster

# Add image info
LABEL org.opencontainers.image.source https://github.com/ranking-agent/mouse-trapi

# install basic tools
RUN apt-get update
RUN apt-get install -yq \
    vim sudo

# set up murphy
ARG UID=1000
ARG GID=1000
RUN groupadd -o -g $GID murphy
RUN useradd -m -u $UID -g $GID -s /bin/bash murphy

# set up requirements
WORKDIR /home/murphy
ADD --chown=murphy:murphy ./requirements.txt .
RUN pip install -r /home/murphy/requirements.txt

# Copy in files
ADD --chown=murphy:murphy . .

# become murphy
ENV HOME=/home/murphy
ENV USER=murphy
USER murphy

# set up base for command
ENTRYPOINT ["uvicorn", "mouse_trapi.server:app"]

# default variables that can be overridden
CMD [ "--host", "0.0.0.0", "--port", "30653" ]

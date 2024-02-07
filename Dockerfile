FROM docker.io/library/python:2.7.18-slim-buster AS installer

RUN apt-get update \
    && apt-get install -y locate libgl1-mesa-glx \
    && apt-get clean autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && updatedb

WORKDIR /app
COPY installer installer
RUN yes '' | python installer/malpem-install

# it'd be a better practice to put apt-get before malpem-install
# locate and updatedb are for the malpem-proot wrapper script

ENV PATH=/opt/malpem-1.3/bin:$PATH

CMD ["/opt/malpem-1.3/bin/malpem-proot"]

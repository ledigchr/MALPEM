FROM docker.io/library/python:2.7.18-slim-buster AS installer

RUN ln -s $(which python) /usr/bin/python

WORKDIR /app
COPY installer installer
RUN yes '' | ./installer/malpem-install

ENV PATH=/opt/malpem-1.3/bin:$PATH \
    PYTHONPATH=/opt/malpem-1.3/lib/care/rootfs/usr/lib/python2.7/dist-packages:$PYTHONPATH

CMD ["/opt/malpem-1.3/bin/malpem"]

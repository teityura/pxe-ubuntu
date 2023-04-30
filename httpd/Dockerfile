FROM alpine:3.17

ARG UBUNTU_CODENAME

RUN set -x && \
  apk add --no-cache apache2

# [Copy ISO Image from docker-host]
# COPY tmp-iso/${UBUNTU_CODENAME}-live-server-amd64.iso /tmp/ubuntu-live-server-amd64.iso
# RUN mkdir -p /srv/httpd/iso && \
#     mv /tmp/ubuntu-live-server-amd64.iso /srv/httpd/iso/ubuntu-live-server-amd64.iso

# [Download ISO Image from ubuntu.com]
RUN wget -O /tmp/ubuntu-live-server-amd64.iso \
    https://cdimage.ubuntu.com/ubuntu-server/${UBUNTU_CODENAME}/daily-live/current/${UBUNTU_CODENAME}-live-server-amd64.iso && \
    mkdir -p /srv/httpd/iso && \
    mv /tmp/ubuntu-live-server-amd64.iso /srv/httpd/iso/ubuntu-live-server-amd64.iso

CMD /usr/sbin/httpd \
  -D FOREGROUND \
  -E /dev/stdout \
  -e info \
  -c 'ErrorLog /dev/stdout' \
  -c 'CustomLog /dev/stdout combined'

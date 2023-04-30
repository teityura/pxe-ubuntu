# Define build arg for base image
ARG UBUNTU_CODENAME

FROM ubuntu:${UBUNTU_CODENAME} as image-extractor

# Re-define build arg for current stage
ARG UBUNTU_CODENAME

RUN set -x && apt-get update && apt-get install -y \
    wget p7zip-full \
    shim-signed grub-efi-amd64-signed grub-common \
    pxelinux

# [Copy ISO Image from docker-host]
# COPY tmp-iso/${UBUNTU_CODENAME}-live-server-amd64.iso /tmp/ubuntu-live-server-amd64.iso

# [Download ISO Image from ubuntu.com]
RUN wget -O /tmp/ubuntu-live-server-amd64.iso \
    https://cdimage.ubuntu.com/ubuntu-server/${UBUNTU_CODENAME}/daily-live/current/${UBUNTU_CODENAME}-live-server-amd64.iso

# [Casper] Put kernel image
RUN mkdir -p /srv/tftp/casper && \
    7z x /tmp/ubuntu-live-server-amd64.iso -o/tmp/ && \
    mv /tmp/casper/vmlinuz /tmp/casper/initrd /srv/tftp/casper/

# [UEFI] Put boot file
RUN cp -a /usr/lib/shim/shimx64.efi.signed.latest /srv/tftp/shimx64.efi && \
    cp -a /usr/lib/grub/x86_64-efi-signed/grubnetx64.efi.signed /srv/tftp/grubx64.efi && \
    cp -a /usr/share/grub/unicode.pf2 /srv/tftp/unicode.pf2

# [Legacy] Put boot file
RUN mkdir -p /srv/tftp/legacy/ && \
    cp -a /usr/lib/PXELINUX/pxelinux.0 /srv/tftp/legacy/pxelinux.0

FROM alpine:3.17

RUN set -x && \
  apk add --no-cache dnsmasq

COPY --from=image-extractor /srv/tftp /srv/tftp

CMD ["/usr/sbin/dnsmasq", "--no-daemon"]

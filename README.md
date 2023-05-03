# pxe-ubuntu

UBUNTU環境において、僕の考える最強のPXEブート環境を作りました

docker-compose up -d すれば ubuntu の autoinstall 環境が完成します

## Quick Start

1. .env で UBUNTU_CODENAME を定義します
2. jinja2/hosts.json で Dockerホスト, PXEクライアント を定義します
3. docker-compose up -d したら PXEブート環境が出来上がります

```
# define UBUNTU_CODENAME
vim .env

# define docker_host, pxe_clients
cd jinja2/
cp hosts.json.sample hosts.json
vim hosts.json
./generate_config.py

# docker-compose
cd ../
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

## Overview

- [docker-compose.yml](docker-compose.yml) には
  - dnsmasq
  - httpd

という、2つのサービスが存在します

``` log
# [overview]
# docker-compose ps
        Name                      Command               State                Ports
------------------------------------------------------------------------------------------------
pxe-ubuntu_dnsmasq_1   /usr/sbin/dnsmasq --no-daemon    Up
pxe-ubuntu_httpd_1     /bin/sh -c /usr/sbin/httpd ...   Up      0.0.0.0:80->80/tcp,:::80->80/tcp
```

## 機能1: confの動的生成

- [jinja2/hosts.json](jinja2/hosts.json.sample) に定義した
  - Dockerホスト情報(docker_host)
  - PXEクライアント情報(pxe_clients)

の情報をもとに、

- dnsmasq の設定ファイル
- httpd の設定ファイル

を動的に生成できます

### confの生成

- Dockerホストに python環境があれば、以下のコマンドで生成できます

```
cd jinja2/
./generate_config.py
```

- Dockerホストに python環境なければ、以下のコマンドで生成できます

```
docker run --rm -it \
  -v $(pwd)/hosts.json:/work/hosts.json \
  -v $(pwd)/templates:/work/templates \
  -v $(pwd)/templates_generated:/work/templates_generated \
  -v $(pwd)/generate_config.py:/work/generate_config.py \
  -v $(pwd)/requirements.txt:/work/requirements.txt \
  -w /work \
  python:3.9 /bin/sh -c "pip install -r requirements.txt && python generate_config.py"
```

### 生成後

生成後は jinja2/templates_generated のパスに conf が生成されます

``` log
# tree jinja2/
jinja2/
├── generate_config.py
├── hosts.json
├── hosts.json.sample
├── requirements.txt
├── templates
│   ├── dnsmasq
│   │   ├── default.j2
│   │   ├── grub.cfg.j2
│   │   └── pxe-dnsmasq.conf.j2
│   └── httpd
│       └── user-data.j2
└── templates_generated
    ├── dnsmasq
    │   ├── default
    │   ├── grub.cfg
    │   └── pxe-dnsmasq.conf
    └── httpd
        └── autoinstall
            ├── client1
            │   ├── meta-data
            │   └── user-data
            └── client2
                ├── meta-data
                └── user-data

9 directories, 15 files
```

## 機能2: dnsmasq, httpd サーバの自動構築

- dnsmasq が動作するサービス
- httpd が動作するサービス

の2つがあり、それぞれのイメージをビルドして、コンテナとして起動します

``` log
# docker image ls
REPOSITORY           TAG       IMAGE ID       CREATED       SIZE
pxe-ubuntu/httpd     jammy     ce5301b0808d   2 days ago    2.08GB
pxe-ubuntu/dnsmasq   jammy     ebc847d90101   2 days ago    137MB
```

### dnsmasq イメージについて

[dnsmasq](dnsmasq/Dockerfile) では マルチステージングビルドを利用しています

- ubuntu:${UBUNTU_CODENAME} のイメージでPXEブートの構成ファイル取得
- PXEブートの構成ファイルを alpine ベースのイメージにコピーします

### dnsmasq コンテナについて

--network host --cap-add=NET_ADMIN が必要になります

DHCP機能を使いますので *PXEブートを実行するセグメント* において、
*DHCPサーバを停止* しておいてください

conf ファイルは、Jinja2テンプレートで動的に生成したものをマウントします

``` log
# tree dnsmasq/
dnsmasq/
├── default -> ../jinja2/templates_generated/dnsmasq/default
├── Dockerfile
├── grub.cfg -> ../jinja2/templates_generated/dnsmasq/grub.cfg
└── pxe-dnsmasq.conf -> ../jinja2/templates_generated/dnsmasq/pxe-dnsmasq.conf

0 directories, 4 files
```

### httpd イメージについて

[httpd](httpd/Dockerfile) イメージは *ISOファイルを含めてビルド* するため、約2GBになっています

ポートは -p 80:80/tcp で動作させています  

### httpd コンテナについて

- conf ファイルは、Jinja2テンプレートで動的に生成したものをマウントします
- pxe_clients で定義したホストごとに、autoinstall設定を生成します

``` log
# tree httpd/
httpd/
├── autoinstall -> ../jinja2/templates_generated/httpd/autoinstall
├── Dockerfile
└── pxe-httpd.conf

1 directory, 2 files

# ===

# tree httpd/autoinstall/
httpd/autoinstall/
├── client1
│   ├── meta-data
│   └── user-data
└── client2
    ├── meta-data
    └── user-data

2 directories, 4 files
```

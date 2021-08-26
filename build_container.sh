#!/bin/bash

FILE=Dockerfile
if [ ! -f "$FILE" ]
then
  echo "$FILE does not exist"
  echo "Exit script"
  exit 1
fi

BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
COMMIT_ID=$(git rev-parse --verify HEAD | cut -c 1-8)
DATE=$(date -u +'%Y%m%d')
VER="${DATE}_${COMMIT_ID}"
TAG=${PWD##*/}

docker build --build-arg BUILD_DATE=$BUILD_DATE --build-arg TITLE=$TAG -t $TAG:$VER .

if [ $# -eq 0 ]
then
  DOCKER_HOST_PORT=5011
  echo "argument Docker Host Port not provided. Port set to $DOCKER_HOST_PORT by default"
else
  DOCKER_HOST_PORT=$1
fi
APP_PORT=80


# env
TIMEZONE="TZ=Asia/Hong_Kong"
MODULE_NAME="MODULE_NAME=main"
MAX_WORKERS="MAX_WORKERS=1"
TIMEOUT="TIMEOUT=3600"

docker run -d --name $TAG -p $DOCKER_HOST_PORT:$APP_PORT --restart unless-stopped -e $MAX_WORKERS -e $TIMEOUT -e $TIMEZONE -e $MODULE_NAME $TAG:$VER
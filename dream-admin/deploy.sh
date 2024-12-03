#!/bin/bash

# docker system prune -a -f
docker image prune -a -f

DOCKER_APP_NAME=admin
BLUE_PORT=7011
GREEN_PORT=7012

EXIST_BLUE=$(/usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-blue -f ./compose/${DOCKER_APP_NAME}.blue.yml ps | grep Up)

if [ -z "$EXIST_BLUE" ]; then

    echo "================== start green down -> blue up"
    /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-blue -f ./compose/${DOCKER_APP_NAME}.blue.yml up -d --build

    sleep 10

    RES_CODE_BLUE=$(curl -o /dev/null -w "%{http_code}" "http://localhost:${BLUE_PORT}/healthz")
    echo ""
    echo "http://localhost:${BLUE_PORT}/healthz RES_CODE_BLUE ${RES_CODE_BLUE}"
    echo ""
    
    if [ $RES_CODE_BLUE -eq 200 ]; then
        echo "================== end green down"
        /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-green -f ./compose/${DOCKER_APP_NAME}.green.yml down
    else
        echo "================== end blue down"
        /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-blue -f ./compose/${DOCKER_APP_NAME}.blue.yml down
    fi
    
else

    echo "================== start blue down -> green up"
    /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-green -f ./compose/${DOCKER_APP_NAME}.green.yml up -d --build

    sleep 10

    RES_CODE_GREEN=$(curl -o /dev/null -w "%{http_code}" "http://localhost:${GREEN_PORT}/healthz")
    echo ""
    echo "http://localhost:${GREEN_PORT}/healthz RES_CODE_GREEN ${RES_CODE_GREEN}"
    echo ""

    if [ $RES_CODE_GREEN -eq 200 ]; then
        echo "================== end blue down"
        /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-blue -f ./compose/${DOCKER_APP_NAME}.blue.yml down
    else
        echo "================== end green down"
        /usr/local/bin/docker-compose -p ${DOCKER_APP_NAME}-green -f ./compose/${DOCKER_APP_NAME}.green.yml down
    fi
    
fi
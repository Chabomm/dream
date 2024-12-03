# dream
복지드림 통합복지시스템

# ui ref
https://flowbite.com/docs/getting-started/introduction/
https://tailwindcss.com/docs/justify-content
https://headlessui.com/react/popover

# development
UP `docker-compose up --build -d`
DN `docker-compose down --rmi all`

# Production

## nginx
TT `sudo nginx -t`
RE `sudo service nginx restart`

## network 통합
- `docker network create common`
- `docker network ls`

# 컨테이너 logs
docker logs --tail 20 -f backend

## nginx
TT `nginx -t`
RE `sudo service nginx restart`

# 데이터베이스 compose UP
cd /data/dream/database
docker-compose up --build -d

# 데이터베이스 compose DOWN
cd /data/dream/database
docker-compose down --rmi all

# 백앤드 compose UP
cd /data/dream/dream-backend
docker-compose up --build -d

# 백앤드 compose DOWN
cd /data/dream/dream-backend
docker-compose down --rmi all






































## cd deploy database
sudo /usr/local/bin/docker-compose -f docker-compose.db.yml up --build -d
sudo /usr/local/bin/docker-compose -f docker-compose.db.yml down --rmi all

## cd deploy backend
CH `docker-compose -f docker-compose.backend.yml config`
UP `sudo /usr/local/bin/docker-compose -f docker-compose.backend.yml up --build -d`
DN `sudo /usr/local/bin/docker-compose -f docker-compose.backend.yml down --rmi all`
로그 `sudo docker logs --tail 20 -f backend`

1. schemas
2. models
3. service
4. routers
5. main.py

# 어드민 콘솔 dream 
첫 배포 `sudo /usr/local/bin/docker-compose -p dream-blue -f dream.blue.yml up -d --build`
로그 `sudo docker logs --tail 20 -f dream_blue`

# 어드민 콘솔 dream-admin 
첫 배포 `docker-compose -p admin-blue -f admin.blue.yml up -d --build`
docker DOWN `docker-compose -p admin-green -f admin.green.yml down`
배포 `./admin.deploy.sh`
원격 `docker exec -it admin_blue sh`
로그 `docker logs --tail 20 -f admin_blue`
메모리 `docker exec admin_green ps -eo pid,ppid,user,args`
메모리 `docker exec admin_green pmap -x 249`

# 도커 메모리 CPU 사용량 확인
`docker stats`

## 6. 컨테이너 강제 삭제
docker rm -f 9b6a6fb4d43b

## 도커 정리 docker clean (https://depot.dev/blog/docker-clear-cache)
docker-compose down --rmi all
docker image prune -a -f
docker container prune -f
docker builder prune -f
docker volume prune -f
docker system prune -a  -f
docker buildx prune -f
docker network prune -f
docker volume rm $(docker volume ls -f dangling=true -q)
docker network create common
docker system df

## nginx
TT `nginx -t`
RE `sudo service nginx restart`

## database 컨테이너 안에서 db접속
docker exec -it database /bin/bash
[bash-4.4#] mysql -uroot -pmysql_root_password
mysql -uroot -p3y7g8p!!
mysql> use mysql
Database changed
mysql> select user, host from user;

# vscode에서 파일이 업로드 안될때
sudo chown -R centos:centos /data/dream/data/dream-backend

# deploy.sh 실행권한 추가
sudo chmod +x ./deploy.sh

# 리눅스 디렉토리 삭제 directory
rm -rf node_modules
TAG=${1:-latest}
NAME=notiziario

docker build -t ${NAME}:${TAG} -t ${NAME}:latest -f docker/Dockerfile .

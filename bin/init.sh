
docker build -f docker/Dockerfile . -t cranient/craniutil

docker-compose -f docker/docker-compose.yml run craniutil-console nosetests . --all-modules --exe -vv


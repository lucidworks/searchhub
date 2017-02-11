docker rmi searchhub
docker rm searchhub
docker build -t searchhub .
docker create -p 80:80 --name searchhub searchhub

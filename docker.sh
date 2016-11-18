#Simple script for creating and running the docker instance on production
#sudo service docker-searchhub stop
docker rmi --force searchhub
docker rm --force searchhub
echo "Build the UI"
node_modules/gulp/bin/gulp.js build --production
cd python
echo "Build the Docker container"
docker build -t searchhub .
#docker create -p 8000:80 --name searchhub searchhub
docker run -it --rm -p 8000:80 --name searchhub searchhub

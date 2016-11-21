#Simple script for creating and running the docker instance on production
sudo service docker-searchhub stop
docker rmi --force searchhub
docker rm --force searchhub
./gradlew installBower
echo "Building the UI"
node_modules/gulp/bin/gulp.js build --production
cd python
echo "Building Docker Container"
docker build -t searchhub .
docker create -p 80:80 --name searchhub searchhub
sudo service docker-searchhub start

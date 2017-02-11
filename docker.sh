#Simple script for creating and running the docker instance on production

./gradlew installBower
echo "Building the UI"
node_modules/gulp/bin/gulp.js build --production
cd python
echo "Building Docker Container"
docker build -t searchhub .
#
sudo service docker-searchhub stop
sudo service docker-searchhub start

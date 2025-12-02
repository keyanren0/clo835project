To test locally:

fill in the .env var


docker build -t sample-app .

docker network create clo-network

docker run --name mysql-db --network clo-network \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=employees \
  -p 3306:3306 \
  mysql:5.7

docker run -p 8080:81 --network clo-network sample-app --env-file .env

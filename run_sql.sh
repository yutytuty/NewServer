docker run -d -p 3306:3306 --name mysql-docker-container -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=game -e \
MYSQL_USER=gameserver -e MYSQL_PASSWORD=bestToDoItSimple mysql/mysql-server:latest

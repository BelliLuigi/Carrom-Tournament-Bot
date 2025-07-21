FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_DATABASE=carrom
COPY ./MySQL_solutions.ipynb /docker-entrypoint-initdb.d/

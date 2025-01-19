FROM nginx:stable 

RUN apt update
RUN apt upgrade -y
RUN apt install openssl nginx -y

ARG SERVER_HOST
ARG SERVER_URL

ENV SERVER_HOST=$SERVER_HOST
ENV SERVER_URL=$SERVER_URL

COPY config/nginx.conf /etc/nginx/nginx.conf

COPY files/dist /var/www/html
COPY files/img /var/www/html/img
RUN chmod -R 777 /var/www

STOPSIGNAL SIGKILL

ENTRYPOINT ["nginx", "-g", "daemon off;"]
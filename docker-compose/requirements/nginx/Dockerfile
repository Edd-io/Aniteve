FROM nginx:stable 

RUN apt update
RUN apt upgrade -y
RUN apt install openssl nginx -y

ARG SERVER_HOST
ARG SERVER_URL

ENV SERVER_HOST=$SERVER_HOST
ENV SERVER_URL=$SERVER_URL

RUN mkdir -p /etc/nginx/ssl
RUN openssl req -x509 -nodes -out /etc/nginx/ssl/aniteve.crt -keyout /etc/nginx/ssl/aniteve.key -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=$SERVER_URL/UID=$SERVER_HOST"

COPY config/nginx.conf /etc/nginx/nginx.conf
RUN sed -i 's/||SERVER_URL||/'"$SERVER_URL"'/g' /etc/nginx/nginx.conf

COPY files/dist /var/www/html
COPY files/img /var/www/html/img
RUN chmod -R 777 /var/www

STOPSIGNAL SIGKILL

ENTRYPOINT ["nginx", "-g", "daemon off;"]
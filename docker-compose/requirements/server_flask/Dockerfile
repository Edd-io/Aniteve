FROM ubuntu:latest

RUN apt update
RUN apt upgrade -y
RUN apt install python3 python3-pip uvicorn -y
RUN apt-get update && apt-get install -y curl build-essential

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs


ARG KEY_API_TMDB
ARG PASSWORD_SERVER
ARG SECRET_KEY
ARG WEBHOOK_URL

ENV KEY_API_TMDB=$KEY_API_TMDB
ENV PASSWORD_SERVER=$PASSWORD_SERVER
ENV SECRET_KEY=$SECRET_KEY
ENV WEBHOOK_URL=$WEBHOOK_URL

COPY files/ /app

WORKDIR /app

RUN pip install -r requirements.txt --b

RUN echo 'key_api_tmdb="'$KEY_API_TMDB'"' > credientials.py
RUN echo 'password="'$PASSWORD_SERVER'"' >> credientials.py
RUN echo 'secret_key="'$SECRET_KEY'"' >> credientials.py
RUN echo 'webhook_url="'$WEBHOOK_URL'"' >> credientials.py

STOPSIGNAL SIGKILL

ENTRYPOINT [ "python3", "-u", "main.py" ]
# ENTRYPOINT ["hypercorn", "main:app", "--bind", "0.0.0.0:8000"]
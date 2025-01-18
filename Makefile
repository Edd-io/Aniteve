# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: edbernar <edbernar@student.42angouleme.    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/10/28 19:26:13 by tomoron           #+#    #+#              #
#    Updated: 2025/01/18 12:15:35 by edbernar         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

FILE = docker-compose/docker-compose.yml
WEBSITE_PATH = docker-compose/requirements/nginx/files

COMPOSE = docker compose -f $(FILE)

all: up

up: build
	$(COMPOSE) up  --build -d

up_att: build
	$(COMPOSE) up --build

watch:
	$(COMPOSE) watch 

down:
	$(COMPOSE) down

clean: down
	docker system prune -af

fclean:clean
	$(COMPOSE) down -v
	docker system prune -af

build:
	cd $(WEBSITE_PATH) && npm run build

re: fclean all

.PHONY: all up up_att down fclean re
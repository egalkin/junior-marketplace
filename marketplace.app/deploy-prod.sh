#!/bin/bash

source ../DOCKER_ENV_PRODUCTION
source ../.env.prod

docker volume create marketplace_user_image
docker network create marketplace

docker-compose -f docker-compose-prod.yml up --build

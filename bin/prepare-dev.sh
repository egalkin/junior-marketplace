#!/bin/bash

docker volume create marketplacedb
docker volume create marketplace.app

docker network create marketplace

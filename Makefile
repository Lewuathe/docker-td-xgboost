.PHONY: test clean

build:
	docker build -t lewuathe/docker-td-xgboost models

all: build

push: build
	docker push lewuathe/docker-td-xgboost:latest

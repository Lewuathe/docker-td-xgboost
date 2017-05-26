XGBoost Docker image with Treasure Data
===


## How to build

```
$ make build
```

## How to run

```
$ docker run lewuathe/docker-td-xgboost train \
  --apikey $TD_API_KEY \
  --database <Database Name> \
  --table <Table Name> \
  --feature sepal_width \
  --feature sepal_length \
  --target class \
  --model awesome-model
```

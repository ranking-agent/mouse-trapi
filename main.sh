#!/usr/bin/env bash

export $(egrep -v '^#' .env | xargs)

# run api server
uvicorn mouse_trapi.server:app --host 0.0.0.0 --port 30653 --reload

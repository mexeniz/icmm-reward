#!/bin/sh

BIND_ADDRESS="localhost"
PORT="8060"

gunicorn -b "${BIND_ADDRESS}:${PORT}" -w 4 app:app
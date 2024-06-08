#!/bin/sh
curl -X POST -H "Content-Type: application/json" --data @mongo-sink-connector-tem.json http://kafka_connect:8083/connectors -w "\n" &
curl -X POST -H "Content-Type: application/json" --data @mongo-sink-connector-hum.json http://kafka_connect:8083/connectors -w "\n"

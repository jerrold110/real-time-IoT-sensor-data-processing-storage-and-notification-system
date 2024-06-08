#!/bin/bash

docker exec flink-jobmanager python code/stream_window_eventtime.py &
docker exec kafka-connect /bin/sh entrypoint.sh &
echo "Flink and Kafka-Connect started..."
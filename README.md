# Real-time IoT sensor data processing, storage, and notification system

#### Run this project
```
docker compose up -d
# Wait for the all containers to start
# ./init.sh starts Flink and Kafka Connect
./init.sh 
```
## Overview

Developed a comprehensive IoT sensor monitoring system leveraging Kafka-based pub-sub architecture to manage data streams from numerous sensors. Utilized Flink for real-time, stateful, event-time sliding window processing to detect and alert users of overheating issues, enabling automatic device shutdowns. Implemented Kafka Connect to integrate with MongoDB for persistent data storage for detailed analysis and reporting.

## IoT system architecture and Kafka

## Flink

## MongoDB
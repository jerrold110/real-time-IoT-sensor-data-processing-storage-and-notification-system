# Real-time IoT sensor data processing, storage, and notification system

#### Run this project
```
docker compose up -d
# Wait for the all containers to start
# ./init.sh starts Flink and Kafka Connect
./init.sh 
```
## Overview

This project is a comprehensive IoT sensor monitoring system utilizing a Kafka-based pub-sub architecture to manage data streams from numerous sensors. It employs Flink for real-time, stateful, event-time sliding window processing to detect and alert users of overheating issues, enabling automatic device shutdowns. Additionally, Kafka Connect is used to integrate with MongoDB for persistent data storage, facilitating detailed analysis and reporting.

## Architecture
IoT sensors: Devices streaming messages every second to Kafka
Kafka: Acts as the messaging broker.
Flink: Processes incoming sensor data in real-time.
Kafka Connect: Connects Kafka with MongoDB.
MongoDB: Stores sensor data for analysis and reporting.

## Docker Compose Services
Kafka
* kafka_broker: Kafka broker configured in KRaft mode.
* kafka_init: Initializes Kafka topics for temperature and humidity data.
* kafka_connect: Kafka Connect service configured to use MongoDB as a sink.

Sensors
Multiple Kafka producers simulate sensor data for both temperature and humidity every second.

* kafka-producer-0
* kafka-producer-1
* kafka-producer-2
* kafka-producer-3
* kafka-producer-4

Flink
* flink_jobmanager: Manages Flink jobs.
* flink_taskmanager: Executes tasks assigned by the job manager.

MongoDB
* mongodb: MongoDB instance for storing sensor data.

## Kafka and serialisation
Kafka acts as the central messaging system, facilitating the efficient transfer of sensor data across the architecture. Sensors produce streams of data to temperature and humidity topics, with the key of the message being the sensor_id. 

The messages are serialised at the consumer, sent to the broker, and deseralised by the consumers: Flink and Kafka Connect

## Flink and watermark strategy
Flink is utilized for processing these data streams. It performs real-time, stateful computations, employing event-time sliding windows to monitor and detect overheating. I work with *event time processing* so it is necessary to use a watermarking strategy as events may not arrive to the broker in exact order.

Watermarks address this by providing a mechanism to signal the system about the event time up to which all relevant events have been processed. This allows Flink to close windows and trigger computations at the right time, ensuring accurate and timely analysis. 

I create flink timestamps based on the value of the string timestamp in the message, and periodic watermark generation strategy from the builtin watermark generator.

[Monotonously Increasing Timestamps](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/event-time/built_in/#monotonously-increasing-timestamps)

## Kafka connect to MongoDB

In this project, Kafka Connect is employed to facilitate the seamless integration of Kafka with MongoDB. It acts as a scalable and reliable framework for streaming data between Kafka and other systems, enabling real-time data movement and transformation.

In our IoT sensor monitoring system, Kafka Connect uses sink connectors to stream sensor data from Kafka topics into MongoDB. This integration allows for persistent storage of sensor data, enabling detailed analysis and reporting. 

The use of Kafka Connect ensures that the data pipeline remains robust and scalable, capable of handling varying data loads and seamlessly integrating new data sources or destinations as the system evolves.
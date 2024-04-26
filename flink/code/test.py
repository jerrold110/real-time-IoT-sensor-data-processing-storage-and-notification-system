"""
This file reads data from the Kafka topic with Flink, observes for overheating, then alerts.
Using: Flink Python Datastream API
"""
import argparse
import logging
import sys

from pyflink.common import WatermarkStrategy, Row
from pyflink.common.serialization import Encoder
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.execution_mode import RuntimeExecutionMode

from pyflink.datastream import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.state import KafkaOffsetsInitializer
# from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig
# from pyflink.datastream.connectors.number_seq import NumberSequenceSource
# from pyflink.datastream.functions import RuntimeContext, MapFunction
# from pyflink.datastream.state import ValueStateDescriptor


print('Hello world')

# Create Datastream
# Create environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
env.set_parallelism(1)

# Add Jar files
env.add_jars('jar/flink-connector-kafka-1.17.0.jar')

# Define source from Data source API
# KafkaSource = 

# Define source as Kafka
source = KafkaSource.builder() \
    .set_bootstrap_servers('blablabla') \
    .set_topics("temperature-topic") \
    .set_group_id("my-group") \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")

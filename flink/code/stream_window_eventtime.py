"""
This is the Flink consumer that consumes data from a Kafka topic, that employs a sliding window state logic.
This file:
1. Sets up the stream environment to receive data from the Kafka topic
2. Sets watermarks and deserialisation schema
3. Processes the data in the stream as a windowStream, and sends email alerts in the process function

"""
from typing import Iterable
from statistics import mean
import json
import datetime
import time

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer

from pyflink.common.serialization import SimpleStringSchema # This should be able to deserialize the records from Kafk
from pyflink.common import WatermarkStrategy, Time
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.common.time import Duration
from pyflink.datastream import StreamExecutionEnvironment, ProcessWindowFunction
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.window import SlidingEventTimeWindows, TimeWindow, SlidingProcessingTimeWindows


print('Pyflink event time processing running...')

# Temperature threshold variables for overheating
overheat_mean_threshold = 90.0
overheat_constant_threshold = 89.0

# Create StreamExecutionEnvironment
env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars('file:///opt/flink/jar/flink-sql-connector-kafka-1.17.2.jar')

# Create KafkaSource
"""
Offset
# https://nightlies.apache.org/flink/flink-docs-master/api/python/reference/pyflink.datastream/api/pyflink.datastream.connectors.kafka.KafkaOffsetsInitializer.html#pyflink.datastream.connectors.kafka.KafkaOffsetsInitializer

Pyflink Kafka source onlly allows value deserialization as of 1.17.2
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/connectors/datastream/kafka/
https://nightlies.apache.org/flink/flink-docs-master/api/python/reference/pyflink.datastream/api/pyflink.datastream.connectors.kafka.KafkaRecordSerializationSchemaBuilder.html#pyflink.datastream.connectors.kafka.KafkaRecordSerializationSchemaBuilder

FlinkKafkaConstumer allows more configuration with a custom deserialization schema but is being phased out. Uses add_source() instead from_source()
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/python/datastream/intro_to_datastream_api/#create-using-datastream-connectors
https://nightlies.apache.org/flink/flink-docs-master/api/python/reference/pyflink.datastream/api/pyflink.datastream.connectors.kafka.FlinkKafkaConsumer.html#pyflink.datastream.connectors.kafka.FlinkKafkaConsumer

Kafka source is able to consume messages starting from different offsets by specifying OffsetsInitializer. Offsets are unique messages associated with each message within a partition of a topic
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/connectors/datastream/kafka/#starting-offset

Kafka and idle
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/event-time/generating_watermarks/#watermark-strategies-and-the-kafka-connector
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/event-time/generating_watermarks/#how-operators-process-watermarks
"""
deserialization_schema = SimpleStringSchema()
offset = KafkaOffsetsInitializer.earliest() 
properties = {'bootstrap.servers':'broker:9092',
              'group.id':'test_group'}
# kafka_source = KafkaSource.builder() \
#         .set_topics("temperature-topic") \
#         .set_properties(properties) \
#         .set_starting_offsets(offset) \
#         .set_value_only_deserializer(deserialization_schema)\
#         .build()
kafka_source = FlinkKafkaConsumer(
    'temperature-topic',
    deserialization_schema,
    properties=properties)

# Create Datastream
# watermarks in parallel streams
"""
TimeStampAssigner will overwrite the Kafka timestamps the timestamps of the Kafka records themselves will be used instead.
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/event-time/generating_watermarks/#writing-watermarkgenerators
https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/concepts/time/#watermarks-in-parallel-streams

"""

extract_value = lambda x:float(json.loads(x)['value'])
extract_timestamp = lambda x:json.loads(x)['timestamp']

class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp) -> int:
        ts_string = extract_timestamp(value)
        timestamp_obj = datetime.datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timestamp_obj.timetuple()))
        print(timestamp)
        return timestamp

"""
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/event-time/generating_watermarks/#watermark-strategies-and-the-kafka-connector
.for_bounded_out_of_orderness()
multiple partitions often get consumed in parallel, interleaving the events from the partitions and destroying the per-partition patterns

.for_monotonous_timestamps()
.for_bounded_out_of_orderness(Duration.of_seconds(2))
"""
watermark_strategy = WatermarkStrategy \
.for_monotonous_timestamps()\
.with_timestamp_assigner(CustomTimestampAssigner()) \
.for_bounded_out_of_orderness(Duration.of_seconds(2)) \
.with_idleness(Duration.of_seconds(5))

datastream = env.add_source(kafka_source)\
                .assign_timestamps_and_watermarks(watermark_strategy)

# Process the data stream with key, window, transformation
"""
Good examples here with data_stream.assign_timestamps_and_watermarks(watermark_strategy)
https://nightlies.apache.org/flink/flink-docs-master/api/python/examples/datastream/window.html#sliding-window
"""

# This follows the input format
# The key in this stream is an int
# I am using my producer embedded timestamp
        # These don't work for some reason, program keeps crashing. use TYPES.INT() as output
        #          context.window().start, 
        #          context.window().end]
class WindowProcessFunction(ProcessWindowFunction[tuple, tuple, int, TimeWindow]):
    """
    Calculates mean and threshold of the window. 90 Degrees, 10 seconds.
    Returns the key, windowed-value, first timestamp, last timestamp
    """
    def process(self,
                key: int,
                context: ProcessWindowFunction.Context[TimeWindow],
                elements: Iterable[tuple]) -> Iterable[tuple]:
        # Convert all the elements in the window to json strings, then extract the data from fields
        # The string to dict conversion process is the most demanding process
        json_to_dic = [json.loads(e) for e in elements]
        values_l = [d['value'] for d in json_to_dic] 
        timestamps_l = [d['timestamp'] for d in json_to_dic]

        # Alerting and machine throttle logic
        overheat_constant = True if all(x > overheat_constant_threshold for x in values_l) else False
        mean_temp = round(mean(values_l), 3)

        if mean_temp > overheat_mean_threshold or overheat_constant:
            # Send email with SMTPLIB
            None

        return [(key, 
                 mean_temp,
                 overheat_constant, 
                 timestamps_l[0],
                 timestamps_l[-1]
                 )]
                 
# There is an error with the watermarking, EventTimeWindow does nothing
slidingwindowstream = datastream\
        .key_by(lambda x:int(x[6]), key_type=Types.INT()) \
        .window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(1))) \
        .process(WindowProcessFunction(),
                 Types.TUPLE([Types.INT(), # This follows the output format (key, value, start, end)
                              Types.FLOAT(),
                              Types.BOOLEAN(),
                              Types.STRING(),
                              Types.STRING()])) \
        #.filter(lambda x:x[2]==True or x[1]>overheat_mean_threshold)  

slidingwindowstream.print()
env.execute("Temperature monitoring windowed stream")
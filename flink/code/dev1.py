"""
This is the Pyflink consumer that consumes data from a Kafka topic, that employs a sliding window with max and mean aggregate functions

"""
from typing import Iterable
from statistics import mean
import json
import datetime

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


print('Pyflink running.....')

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

"""
deserialization_schema = SimpleStringSchema()
offset = KafkaOffsetsInitializer.earliest() 
properties = {'bootstrap.servers':'broker:9092',
              'group.id':'test_group'}
kafka_source = KafkaSource.builder() \
        .set_topics("temperature-topic") \
        .set_properties(properties) \
        .set_starting_offsets(offset) \
        .set_value_only_deserializer(deserialization_schema)\
        .build()

# Create Datastream
# watermarks in parallel streams
"""
TimeStampAssigner will overwrite the Kafka timestamps the timestamps of the Kafka records themselves will be used instead.
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/event-time/generating_watermarks/#writing-watermarkgenerators
https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/concepts/time/#watermarks-in-parallel-streams
"""
extract_timestamp = lambda x:float(json.loads(x)['timestamp'])

# class MyTimestampAssigner(TimestampAssigner):
#     def __init__(self):
#         self.epoch = datetime.datetime.now()

#     def extract_timestamp(self, value, record_timestamp) -> int:
#         return str(extract_timestamp(value))


watermark_strategy = WatermarkStrategy.for_monotonous_timestamps()\
        #.for_bounded_out_of_orderness(Duration.of_seconds(2))\
        #.with_timestamp_assigner(MyTimestampAssigner()) #WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(20))  #

datastream = env.from_source(kafka_source, \
                             watermark_strategy, \
                             "Kafka Source")\
                #.assign_timestamps_and_watermarks(watermark_strategy)

# Process the data stream with key, window, transformation
"""
Good examples here with data_stream.assign_timestamps_and_watermarks(watermark_strategy)
https://nightlies.apache.org/flink/flink-docs-master/api/python/examples/datastream/window.html#sliding-window

"""

extract_value = lambda x:float(json.loads(x)['value'])

# This follows the input format
# The key in this stream is a key for now.
class MeanWindowProcessFunction(ProcessWindowFunction[tuple, tuple, str, TimeWindow]):
    def process(self,
                key: str,
                context: ProcessWindowFunction.Context[TimeWindow],
                elements: Iterable[tuple]) -> Iterable[tuple]:
        
        return [(key, 
                 mean([extract_value(e) for e in elements])),
                 context.window().start, 
                 context.window().end]
                 
# There is an error with the watermarking, EventTimeWindow does nothing
slidingwindowstream = datastream\
        .key_by(lambda x:x[6], key_type=Types.STRING()) \
        .window(SlidingProcessingTimeWindows.of(Time.seconds(1), Time.seconds(1))) \
        .process(MeanWindowProcessFunction(),
                 Types.TUPLE([Types.STRING(), 
                              Types.FLOAT(), 
                              Types.INT(),
                              Types.INT()])) # This follows the output format (key, value, start, end)

slidingwindowstream.print()

# datastream = datastream.map(lambda x:type(x[6]).timestamp())
# #datastream = datastream.map(lambda x:x.timestamp())
# datastream.print()

env.execute("PyFlink Kafka Example")
print('End successful')
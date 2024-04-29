"""
This is the Pyflink consumer that consumes data from a Kafka topic, that employs a sliding window with max and mean aggregate functions

"""
from typing import Iterable
from statistics import mean

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer

from pyflink.common.serialization import SimpleStringSchema # This should be able to deserialize the records from Kafk
from pyflink.common import WatermarkStrategy, Time
from pyflink.common.time import Duration
from pyflink.datastream import StreamExecutionEnvironment, ProcessWindowFunction
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.window import SlidingEventTimeWindows, TimeWindow


print('')

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

watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(20))  #WatermarkStrategy.for_monotonous_timestamps()
datastream = env.from_source(kafka_source, \
                             watermark_strategy, \
                             "Kafka Source")

# Process the data stream with key, window, transformation
"""
Good examples here with data_stream.assign_timestamps_and_watermarks(watermark_strategy)
https://nightlies.apache.org/flink/flink-docs-master/api/python/examples/datastream/window.html#sliding-window

"""

class MeanWindowProcessFunction(ProcessWindowFunction[tuple, tuple, str, TimeWindow]):
    def process(self,
                key: str,
                context: ProcessWindowFunction.Context[TimeWindow],
                elements: Iterable[tuple]) -> Iterable[tuple]:
        return [(key, context.window().start, context.window().end, mean([e for e in elements]) )]

slidingwindowstream = datastream\
        .key_by(lambda x:int(x[6])) \
        .window(Time.seconds(10)) \
        .process(MeanWindowProcessFunction(),
                 Types.TUPLE([Types.INT(), Types.INT(), Types.INT(), Types.FLOAT()]))

slidingwindowstream.print()
#data_stream.map(lambda x: "Processed" + str(uuid.uuid4()) + " : " + x, output_type=Types.STRING()).print()
#datastream.map(lambda x: "\n" + x, output_type=Types.STRING()).print()

env.execute("PyFlink Kafka Example")
print('hello')
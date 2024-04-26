from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer

from pyflink.common.serialization import SimpleStringSchema # This should be able to deserialize the records from Kafka
from pyflink.datastream.formats.json import JsonRowDeserializationSchema

from pyflink.common import WatermarkStrategy, Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer


print('hello world')

# Create StreamExecutionEnvironment
env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars('file:///opt/flink/jar/flink-sql-connector-kafka-1.17.2.jar')

# Deserialization schema
# Try this, see it it works, if not find an alternative deserializer
# deserialization_schema = JsonRowDeserializationSchema.builder()\
#                             .type_info(type_info=Types.ROW([Types.PRIMITIVE_ARRAY(Types.CHAR()), Types.PRIMITIVE_ARRAY(Types.CHAR())])).build()

deserialization_schema = SimpleStringSchema()

# kafka_consumer = FlinkKafkaConsumer(
#     topics='temperature-topic',
#     deserialization_schema=deserialization_schema,
#     properties={'bootstrap.servers':'broker:9092', 'group.id':'test_group'})\
    
# datastream = env.add_source(kafka_consumer)

earliest = False
offset = KafkaOffsetsInitializer.earliest() if earliest else KafkaOffsetsInitializer.latest()

properties = {'bootstrap.servers':'broker:9092', 'group.id':'test_group'}
kafka_source = KafkaSource.builder() \
        .set_topics("temperature-topic") \
        .set_properties(properties) \
        .set_starting_offsets(offset) \
        .set_value_only_deserializer(SimpleStringSchema())\
        .build()

datastream = env.from_source(kafka_source, WatermarkStrategy.for_monotonous_timestamps(), "Kafka Source") #timestamps seen by a given source task occur in ascending order

#keyed = datastream.key_by(lambda row: row[0])

datastream.print()
#data_stream.map(lambda x: "Processed" + str(uuid.uuid4()) + " : " + x, output_type=Types.STRING()).print()
#datastream.map(lambda x: "\n" + x, output_type=Types.STRING()).print()

env.execute("PyFlink Kafka Example")
print('hello')
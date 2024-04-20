package sensors;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.serialization.IntegerSerializer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

public class SensorProducerApplication {

    private final Producer<Integer, String> producer;
    final String outTopic;
    // class constructor
    public SensorProducerApplication(final Producer<Integer, String> producer, final String topic) {
        this.producer = producer;
        outTopic = topic;
    }
    // produce a record
    // Key: ID int, Value: JSON String
    public void produce(int key, String value) {
        try {
            final ProducerRecord<Integer, String> producerRecord = new ProducerRecord<>(outTopic, Integer.valueOf(key), value);
            producer.send(producerRecord);
            System.out.println("Sent record to Broker: " + value);
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
    }
    // shutdown
    public void shutdown() {
        producer.close();
    }
    // read properties
    public static Properties loadProperties(String fileName) throws IOException {
        final Properties envProps = new Properties();
        final FileInputStream input = new FileInputStream(fileName);
        envProps.load(input);
        input.close();

        return envProps;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            throw new IllegalArgumentException(
                    "This program takes two arguments: the path to an environment configuration file and" +
                            "the path to the file with records to send" );
        }

        final Properties props = SensorProducerApplication.loadProperties(args[0]);
        final String topic = "topic.temperature.name";
        final Producer<Integer, String> producer = new KafkaProducer<>(props);
        final SensorProducerApplication producerApp = new SensorProducerApplication(producer, topic);

        String filePath = args[1];
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode jsonArray = mapper.readTree(new File(args[1]));
            for (JsonNode jsonNode : jsonArray){
                int key = jsonNode.get("id").asInt();
                String value = jsonNode.toString();
                producerApp.produce(key, value);
            }
        } catch (IOException e) {
            System.err.printf("Error reading file %s due to %s %n", filePath, e);
        }
        finally {
            producerApp.shutdown();
        }
    }
}

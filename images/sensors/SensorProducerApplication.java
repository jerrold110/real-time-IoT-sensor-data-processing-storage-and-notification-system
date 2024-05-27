package sensors;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
//import org.apache.kafka.common.serialization.StringSerializer;
//import org.apache.kafka.common.serialization.IntegerSerializer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.File;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.util.Collection;
// import java.util.List;
import java.util.Properties;
// import java.util.concurrent.ExecutionException;
// import java.util.concurrent.Future;
// import java.util.stream.Collectors;

public class SensorProducerApplication {

    private final Producer<String, String> producer;
    final String outTopic;
    // class constructor
    public SensorProducerApplication(final Producer<String, String> producer, final String topic) {
        this.producer = producer;
        outTopic = topic;
    }
    // produce a record
    // Key: ID int, Value: JSON String
    public void produce(String key, String value) {
        try {
            final ProducerRecord<String, String> producerRecord = new ProducerRecord<>(outTopic, key, value);
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
        System.out.println("Producer started!");
        if (args.length < 3) {
            throw new IllegalArgumentException(
                    "This program takes 3 arguments: the path to an environment configuration file," +
                            "the path to the file with records to send, and the topic name" );
        }

        final Properties props = SensorProducerApplication.loadProperties(args[0]);
        final String topic = args[2];//"temperature-topic";
        final Producer<String, String> producer = new KafkaProducer<>(props);
        final SensorProducerApplication producerApp = new SensorProducerApplication(producer, topic);

        String filePath = args[1];
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode jsonArray = mapper.readTree(new File(args[1]));
            for (JsonNode jsonNode : jsonArray){
                String key = jsonNode.get("id").toString();
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

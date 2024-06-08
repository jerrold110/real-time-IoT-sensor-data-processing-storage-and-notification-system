FROM confluentinc/cp-kafka-connect:7.4.1

RUN confluent-hub install --no-prompt --verbose mongodb/kafka-connect-mongodb:latest

ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from kafka import KafkaConsumer

server = 'localhost:9092'
topic_name = 'green-trips'


def deserializer(data):
    return json.loads(data.decode('utf-8'))


consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],
    auto_offset_reset='earliest',
    group_id='green-trips-counter',
    value_deserializer=deserializer,
    consumer_timeout_ms=10000,
)

count_over_5 = 0
total = 0

for message in consumer:
    ride = message.value
    total += 1
    if ride['trip_distance'] > 5.0:
        count_over_5 += 1

consumer.close()
print(f"Total trips: {total}")
print(f"Trips with trip_distance > 5: {count_over_5}")

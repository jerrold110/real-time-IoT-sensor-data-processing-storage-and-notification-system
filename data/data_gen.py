import random
import csv
import json
from datetime import datetime, timedelta
from faker import Faker
random.seed(1)
Faker.seed(0)

fake = Faker()

locations = 4
temp_sensors = 3
humidity_sensors = 2
# sensors return secondly values. 600 values per sensor dataset
minutes = 10

# location_data
location_data = [['sensor_id','address','topography']]
features = ['road', 'lake', 'field', 'desert']
for i in range(locations):
    id = i
    n = random.randint(1, 3)
    address = fake.address()
    topographical = random.sample(features, n)
    location_data.append([id, address, topographical])

with open ('locations.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(location_data)
    

# sensor data
sensor_id = 0
start_datetime = datetime(2010, 1, 2, 12, 25, 0)

for _ in range(humidity_sensors):
    sensor_data = []
    location_id = random.randint(0, locations-1)
    latitude = round(random.uniform(-90, 90), 2)
    longitude = round(random.uniform(-180, 180), 2)
    elevation = round(random.uniform(0, 1000), 2)
    sensor_type = 'humidity'
    current_time = start_datetime

    # Generate the row of data
    for _ in range(minutes * 60):
        sensor_data.append({
            'id':sensor_id ,
            'location_id':location_id,
            'latitude':latitude,
            'longitude':longitude,
            'elevation':elevation,
            'sensor_type':sensor_type,
            'timestamp':current_time.strftime("%Y-%m-%d %H:%M:%S"),
            'value':random.randint(50, 100)})
        current_time += timedelta(seconds=1)

    # Write the data for the sensor
    with open(f'sensor_{sensor_id}.json', mode='w') as file:
        json.dump(sensor_data, file, indent=4)
    sensor_id  += 1

for _ in range(temp_sensors):
    sensor_data = []
    location_id = random.randint(0, locations-1)
    latitude = round(random.uniform(-90, 90), 2)
    longitude = round(random.uniform(-180, 180), 2)
    elevation = round(random.uniform(0, 1000), 2)
    sensor_type = 'temperature'
    current_time = start_datetime

    # Generate the row of data
    for _ in range(minutes * 60):
        sensor_data.append({
            'id':sensor_id ,
            'location_id':location_id,
            'latitude':latitude,
            'longitude':longitude,
            'elevation':elevation,
            'sensor_type':sensor_type,
            'timestamp':current_time.strftime("%Y-%m-%d %H:%M:%S"),
            'value':random.randint(50, 100)})
        current_time += timedelta(seconds=1)

    # Write the data for the sensor
    with open(f'sensor_{sensor_id}.json', mode='w') as file:
        json.dump(sensor_data, file, indent=4)
    sensor_id  += 1





import json
import paho.mqtt.client as mqtt
import numpy as np
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import tensorflow as tf
import asyncio
import websockets

interpreter = tf.lite.Interpreter(model_path="../Model/env_model.tflite")
interpreter.allocate_tensors()
# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

bucket = "sr3"
org = "elfak"
token = "aKz2phkbpB5kHegQ5A8e-iqk7J8oXao9WG0J8M8rcdgCfVOQdIHPnmyqyq8SyitgDPNJzdLJ4roV-clWSnpcKg=="
url="http://localhost:8086/"
wsurl = "ws://localhost:8765/"

influx_client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)

async def on_message(client, userdata, message):

    my_new_string_value = message.payload.decode("utf-8").replace("'", '"')
    data = json.loads(my_new_string_value)

    p = (influxdb_client.Point("measurement")
         .field("temperature", np.float32(data['temperature']))
         .field("pressure", np.float32(data['pressure']))
         .time(datetime.now())
    )
    write_api.write(bucket=bucket, record=p)
    print(data['temperature'], data['pressure'])

    input_data = np.array([[data['temperature'], data['pressure']]], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction = np.float32(output_data[0][0])
    print(prediction)
    prediction_string = "Predicting nice weather!" if prediction > 0.5 else "Predicting bad weather!"

    emit_data = emit_data = {
        "prediction": prediction_string,
        "temperature": float(data['temperature']),
        "pressure": float(data['pressure'])
    }
    async with websockets.connect(wsurl) as websocket:
        await websocket.send(json.dumps(emit_data))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("serial-reader/data")


def mqtt_on_message(client, userdata, message):
    asyncio.run(on_message(client, userdata, message))


# Start MQTT loop
client = mqtt.Client(client_id="user")
client.on_connect = on_connect
client.on_message = mqtt_on_message
client.username_pw_set(username="user", password="user")
client.connect("127.0.0.1", 1883)
client.loop_forever()
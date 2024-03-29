from flask import Flask, render_template, request, jsonify
import serial
import json
import time
from influxdb import InfluxDBClient

app = Flask(__name__)
ser_arduino1 = serial.Serial('/dev/ttyACM0', 9600)
ser_arduino2 = serial.Serial('/dev/ttyUSB0', 115200)
lamp_states = [0, 0, 0, 0, 0, 0, 0, 0]
sensor_data_arduino2 = {} 

INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'arduino_data'
client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
client.create_database(INFLUXDB_DATABASE)
client.switch_database(INFLUXDB_DATABASE)

def update_sensor_data_arduino2():
    global sensor_data_arduino2
    try:
        raw_data = ser_arduino2.readline().decode()
        cleaned_data = raw_data.replace("\\", "")
        new_sensor_data_arduino2 = json.loads(cleaned_data)

        if new_sensor_data_arduino2 != sensor_data_arduino2:
            sensor_data_arduino2 = new_sensor_data_arduino2

            json_body = [
                {
                    "measurement": "sensor_data",
                    "fields": new_sensor_data_arduino2['measure']
                }
            ]
            client.write_points(json_body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error decoding sensor data: {e}")

@app.route('/')
def index():
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/toggle/<int:lamp_id>')
def toggle_lamp(lamp_id):
    if 1 <= lamp_id <= 8: 
        lamp_states[lamp_id - 1] = 1 - lamp_states[lamp_id - 1]
        data = {"lamp_id": lamp_id, "state": lamp_states[lamp_id - 1]}
        ser_arduino1.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/turn-off-all')
def turn_off_all():
    for i in range(8):
        lamp_states[i] = 1
        data = {"lamp_id": i + 1, "state": 1}
        ser_arduino1.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/turn-on-all')
def turn_on_all():
    for i in range(8):
        lamp_states[i] = 0
        data = {"lamp_id": i + 1, "state": 0}
        ser_arduino1.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/random-toggle')
def random_toggle():
    for i in range(8):
        if random.random() < 0.5:
            lamp_states[i] = 1 - lamp_states[i]
            data = {"lamp_id": i + 1, "state": lamp_states[i]}
            ser_arduino1.write((json.dumps(data) + '\n').encode())
    time.sleep(1)
    return render_template('index.html', lamp_states=lamp_states)

def background_update():
    while True:
        update_sensor_data_arduino2()
        time.sleep(0.01)

if __name__ == '__main__':
    import threading
    update_thread = threading.Thread(target=background_update)
    update_thread.daemon = True
    update_thread.start()

    app.run(host='0.0.0.0', debug=True)
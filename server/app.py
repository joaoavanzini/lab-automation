from flask import Flask, render_template, request, jsonify
import serial
import json
import random
import time

app = Flask(__name__)
ser = serial.Serial('/dev/cu.usbmodem101', 9600)
lamp_states = [0, 0, 0, 0, 0, 0, 0, 0]

@app.route('/')
def index():
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/toggle/<int:lamp_id>')
def toggle_lamp(lamp_id):
    if 1 <= lamp_id <= 8: 
        lamp_states[lamp_id - 1] = 1 - lamp_states[lamp_id - 1]
        data = {"lamp_id": lamp_id, "state": lamp_states[lamp_id - 1]}
        ser.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/turn-off-all')
def turn_off_all():
    for i in range(8):
        lamp_states[i] = 1
        data = {"lamp_id": i + 1, "state": 0}
        ser.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/turn-on-all')
def turn_on_all():
    for i in range(8):
        lamp_states[i] = 0
        data = {"lamp_id": i + 1, "state": 1}
        ser.write((json.dumps(data) + '\n').encode())
    return render_template('index.html', lamp_states=lamp_states)

@app.route('/random-toggle')
def random_toggle():
    for i in range(8):
        if random.random() < 0.5:
            lamp_states[i] = 1 - lamp_states[i]
            data = {"lamp_id": i + 1, "state": lamp_states[i]}
            ser.write((json.dumps(data) + '\n').encode())
    time.sleep(1)
    return render_template('index.html', lamp_states=lamp_states)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

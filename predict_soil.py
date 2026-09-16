import csv
import time
import threading
from datetime import datetime

import serial
from flask import Flask, jsonify, render_template

# ===== НАСТРОЙКИ =====
SERIAL_PORT = 'COM4'         # Замени на свой порт (COM3, COM4 и т.д.)
BAUDRATE = 9600
CSV_FILENAME = 'data.csv'

app = Flask(__name__, static_folder='static')

# ===== ХРАНИЛИЩЕ ДАННЫХ =====
latest_data = {
    'soil': 0,
    'temp': 0.0,
    'light': 0,
    'watering': 'OFF',
    'time': ''
}

history = []


def read_from_arduino():
    """Читает данные с Arduino и сохраняет их"""
    global latest_data, history

    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        time.sleep(2)
        print(f"Connected to {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Error: {e}")
        return

    # Создаём CSV с заголовками (если файла нет)
    try:
        with open(CSV_FILENAME, 'x', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Soil', 'Temp', 'Light', 'Watering'])
    except FileExistsError:
        pass

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if line:
                parts = line.split(',')

                if len(parts) == 4:
                    soil = int(parts[0])
                    temp = float(parts[1])
                    light = int(parts[2])
                    watering = parts[3]

                    now = datetime.now().strftime('%H:%M:%S')

                    latest_data = {
                        'soil': soil,
                        'temp': temp,
                        'light': light,
                        'watering': watering,
                        'time': now
                    }

                    history.append({
                        'time': now,
                        'soil': soil,
                        'temp': temp,
                        'light': light
                    })

                    if len(history) > 100:
                        history.pop(0)

                    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([now, soil, temp, light, watering])

                    print(f"[{now}] Soil: {soil} | Temp: {temp} | Light: {light} | Watering: {watering}")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def get_data():
    return jsonify(latest_data)


@app.route('/history')
def get_history():
    return jsonify(history)


if __name__ == '__main__':
    thread = threading.Thread(target=read_from_arduino, daemon=True)
    thread.start()
    print("Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
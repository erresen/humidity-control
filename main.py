#!/usr/bin/env python3

import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import statistics

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
RELAY_GPIO = 27
READ_BUFFER = 8
MAX_HUMIDITY = 88
MIN_HUMIDITY = 83
SLEEP = 15
relay_state = 0

def main():
    initialise()

    try:
        humidity, temperature = initial_read()

        temps = [temperature]
        humids = [humidity]

        while True:
            read_humidity(temps, humids)
            time.sleep(SLEEP)

    finally:
        clean_up()

def initial_read():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    if humidity >= MAX_HUMIDITY:
        set_relay_high()
    else:
        set_relay_low()
    
    save_metrics(humidity, temperature)
    
    time.sleep(5)

    return humidity, temperature

def read_humidity(temps, humids):
    global relay_state

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        humids.append(humidity)
        temps.append(temperature)

        if len(temps) >= READ_BUFFER:
            humids.pop(0)
            temps.pop(0)
        
        h = statistics.median(humids)
        t = statistics.median(temps)

        if h >= MAX_HUMIDITY and relay_state == 0:
            set_relay_high()
        elif h <= MIN_HUMIDITY and relay_state == 1:
            set_relay_low()
        
        save_metrics(h, t)

def initialise():
    init_gpio()

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_GPIO, GPIO.OUT)

def set_relay_low():
    global relay_state
    relay_state = 0
    GPIO.output(RELAY_GPIO, GPIO.LOW)

def set_relay_high():
    global relay_state
    relay_state = 1
    GPIO.output(RELAY_GPIO, GPIO.HIGH)

def clean_up():
    set_relay_low()
    GPIO.cleanup()

def save_metrics(humidity, temperature):
    global relay_state
    
    metrics = []
    metrics.append('# HELP dht_humidity Current humidity from DHT22 sensor\n')
    metrics.append('# TYPE dht_humidity gauge\n')
    metrics.append(f'dht_humidity {humidity}\n')
    metrics.append('\n')
    metrics.append('# HELP dht_temperature Current temperature from DHT22 sensor\n')
    metrics.append('# TYPE dht_temperature gauge\n')
    metrics.append(f'dht_temperature {temperature}\n')
    metrics.append('\n')
    metrics.append('# HELP relay_state Current relay state\n')
    metrics.append('# TYPE relay_state gauge\n')
    metrics.append(f'relay_state {relay_state}\n')

    with open('/home/pi/metrics', 'w') as file:
        file.writelines(metrics)

if __name__  == "__main__":
    main()
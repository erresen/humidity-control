#!/usr/bin/env python3

import Adafruit_DHT
import RPi.GPIO as GPIO
import datetime
import time
import sqlite3
import statistics
from enum import IntEnum

class Event(IntEnum):
    START = 1
    STOP = 2
    READ_FAIL = 3

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
RELAY_GPIO = 27
DB_PATH = '/home/pi/humidity.db'
READ_BUFFER = 10
MAX_HUMIDITY = 88
MIN_HUMIDITY = 83
SLEEP = 60
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
    
    save_humidity_log(temperature, humidity)

    if humidity >= MAX_HUMIDITY:
        set_relay_high()
    else:
        set_relay_low()
    
    time.sleep(5)

    return humidity, temperature

def read_humidity(temps, humids):
    global relay_state

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        temps.append(temperature)
        humids.append(humidity)

        if len(temps) >= READ_BUFFER:
            t = statistics.median(temps)
            temps.clear()

            h = statistics.median(humids)
            humids.clear()

            save_humidity_log(t, h)

            if h >= MAX_HUMIDITY and relay_state == 0:
                set_relay_high()
            elif h <= MIN_HUMIDITY and relay_state == 1:
                set_relay_low()
    else:
        save_event(Event.READ_FAIL)

def initialise():
    init_gpio()
    init_db()
    save_event(Event.START)

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_GPIO, GPIO.OUT)

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''create table if not exists humidity_log (date timestamp, temperature real, humidity real);''')
    cur.execute('''create table if not exists relay (date timestamp, state integer not null);''')
    cur.execute('''create table if not exists event_log (date timestamp, event integer not null);''')
    con.commit()

def set_relay_low():
    global relay_state
    relay_state = 0
    GPIO.output(RELAY_GPIO, GPIO.LOW)
    save_relay_state()

def set_relay_high():
    global relay_state
    relay_state = 1
    GPIO.output(RELAY_GPIO, GPIO.HIGH)
    save_relay_state()

def save_humidity_log(temp, humidity):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        INSERT INTO humidity_log (date, temperature, humidity) 
        VALUES (:now, :temperature, :humidity);''', 
        {'now': datetime.datetime.now(), 'temperature': temp, 'humidity': humidity})
    con.commit()
    con.close()

def save_relay_state():
    global relay_state
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        INSERT INTO relay (date, state) 
        VALUES (:now, :state);''', 
        {'now': datetime.datetime.now(), 'state': relay_state})
    con.commit()
    con.close()

def save_event(event):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        INSERT INTO event_log (date, event) 
        VALUES (:now, :event);''', 
        {'now': datetime.datetime.now(), 'event': event})
    con.commit()
    con.close()

def clean_up():
    set_relay_low()
    GPIO.cleanup()
    save_event(Event.STOP)

if __name__  == "__main__":
    main()
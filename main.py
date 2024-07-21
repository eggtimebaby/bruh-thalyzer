# config.py
"""Configuration file for MQ3 sensor and OLED display."""
MQ3_PIN = 34
OLED_SCL_PIN = 22
OLED_SDA_PIN = 21
BUTTON_PIN = 0  # Assuming we're using the BOOT button
OLED_WIDTH = 128
OLED_HEIGHT = 64
AIR_R0_RATIO = 60.0
WARM_UP_TIME = 20
NUM_CALIBRATION_READINGS = 10
LONG_PRESS_TIME = 3  # seconds
LOG_LEVEL = 20  # INFO level
LOG_FILE = "sensor_log.txt"

# hardware.py
"""Hardware initialization and management."""
from machine import Pin, ADC, I2C
import ssd1306
from config import *
import utime

class Hardware:
    def __init__(self):
        self.mq3_pin = ADC(Pin(MQ3_PIN))
        self.mq3_pin.atten(ADC.ATTN_11DB)  # Full 3.3V range
        self.oled = self._init_oled()
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        self.button_press_time = 0

    def _init_oled(self):
        try:
            i2c = I2C(scl=Pin(OLED_SCL_PIN), sda=Pin(OLED_SDA_PIN))
            return ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
        except Exception as e:
            log(40, f"OLED initialization failed: {e}")
            return None

    def display_message(self, message, x=0, y=0, clear=True):
        if self.oled:
            try:
                if clear:
                    self.oled.fill(0)
                self.oled.text(message, x, y)
                self.oled.show()
            except Exception as e:
                log(40, f"OLED error: {e}")

    def button_pressed(self):
        return self.button.value() == 0

    def check_button(self):
        if self.button_pressed():
            if self.button_press_time == 0:
                self.button_press_time = utime.time()
            return utime.time() - self.button_press_time
        else:
            press_duration = utime.time() - self.button_press_time if self.button_press_time > 0 else 0
            self.button_press_time = 0
            return press_duration

# sensor.py
"""MQ3 sensor calculations and management."""
import math
from config import *
import utime
from logging import log

class MQ3Sensor:
    def __init__(self, hardware):
        self.hardware = hardware
        self.r0 = 1.0
        self.readings = []
        self.max_readings = 10  # Number of readings to average

    def warm_up(self):
        """Warm up the sensor and calculate initial R0."""
        log(20, "Warming up the sensor...")
        self.hardware.display_message("Warming up...")

        for i in range(WARM_UP_TIME):
            self.hardware.display_message("." * i, 0, 20, clear=False)
            utime.sleep(1)

        self.calibrate()

    def calibrate(self):
        """Calibrate the sensor by calculating R0."""
        log(20, "Calibrating sensor...")
        self.hardware.display_message("Calibrating...")
        r0_sum = 0
        for _ in range(NUM_CALIBRATION_READINGS):
            r0_sum += self._calculate_rs() / AIR_R0_RATIO
            utime.sleep(0.1)
        self.r0 = r0_sum / NUM_CALIBRATION_READINGS
        log(20, f"Calibration complete. New R0: {self.r0}")
        self.hardware.display_message("Calibration done")
        utime.sleep(2)

    def _calculate_rs(self):
        """Calculate the sensor resistance."""
        sensor_value = self.hardware.mq3_pin.read()
        sensor_volt = sensor_value * (3.3 / 4095.0)
        return (3.3 * 1000.0 / sensor_volt) - 1000.0  # Assuming R2 = 1000 ohms

    def read_raw_value_of_alcohol(self):
        """Calculate the concentration of alcohol in mg/L."""
        rs = self._calculate_rs()
        if self.r0 == 0:
            return 0
        return 0.4 * math.pow((rs / self.r0), -1.43068)

    def get_smoothed_reading(self):
        """Get a smoothed alcohol reading using moving average."""
        raw = self.read_raw_value_of_alcohol()
        self.readings.append(raw)
        if len(self.readings) > self.max_readings:
            self.readings.pop(0)
        return sum(self.readings) / len(self.readings)

    @staticmethod
    def convert_raw_to_bac(raw):
        """Convert raw alcohol value to BAC percentage."""
        return raw * 0.2

    @staticmethod
    def convert_raw_to_gram_per_millilitre(raw):
        """Convert raw alcohol value to g/mL."""
        return raw * 0.002

    @staticmethod
    def convert_raw_to_ppm(raw):
        """Convert raw alcohol value to PPM."""
        return raw * 500.0

# logging.py
"""Simple logging module for MicroPython."""
import utime
from config import LOG_LEVEL, LOG_FILE

def log(level, message):
    if level >= LOG_LEVEL:
        timestamp = utime.localtime()
        log_message = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d} - {message}"
        print(log_message)
        with open(LOG_FILE, "a") as f:
            f.write(log_message + "\n")

# main.py
"""Main script for MQ3 alcohol sensor with ESP32."""
import utime
from hardware import Hardware
from sensor import MQ3Sensor
from logging import log
from config import LONG_PRESS_TIME

class State:
    OFF = 0
    ON = 1
    CALIBRATING = 2

def main():
    hw = Hardware()
    sensor = MQ3Sensor(hw)
    state = State.OFF
    last_reading_time = 0
    reading_interval = 1  # seconds

    while True:
        button_press_duration = hw.check_button()
        
        if button_press_duration > 0:
            if button_press_duration >= LONG_PRESS_TIME:
                if state == State.OFF:
                    state = State.ON
                    sensor.warm_up()
                    log(20, "Device turned ON")
                else:
                    state = State.OFF
                    log(20, "Device turned OFF")
                hw.display_message("ON" if state == State.ON else "OFF")
                utime.sleep(1)
            elif state == State.ON and button_press_duration < LONG_PRESS_TIME:
                state = State.CALIBRATING
                sensor.calibrate()
                state = State.ON

        if state == State.ON:
            current_time = utime.time()
            if current_time - last_reading_time >= reading_interval:
                raw_alcohol = sensor.get_smoothed_reading()
                ppm = sensor.convert_raw_to_ppm(raw_alcohol)
                bac = sensor.convert_raw_to_bac(raw_alcohol)
                g_per_ml = sensor.convert_raw_to_gram_per_millilitre(raw_alcohol)
                
                log(20, f"Raw Alcohol: {raw_alcohol:.2f} mg/L, PPM: {ppm:.0f}, BAC: {bac:.2f}%, g/mL: {g_per_ml:.4f}")
                
                hw.display_message(f"Raw: {raw_alcohol:.2f} mg/L")
                hw.display_message(f"PPM: {ppm:.0f}", 0, 16, clear=False)
                hw.display_message(f"BAC: {bac:.2f} %", 0, 32, clear=False)
                hw.display_message(f"g/mL: {g_per_ml:.4f}", 0, 48, clear=False)
                
                last_reading_time = current_time

        utime.sleep(0.1)  # Small delay to prevent busy waiting

if __name__ == "__main__":
    main()
# test_sensor.py

import math
from sensor import MQ3Sensor
from config import *

class MockHardware:
    def __init__(self, mock_readings):
        self.mock_readings = mock_readings
        self.reading_index = 0
        self.displayed_messages = []

    def mq3_pin_read(self):
        value = self.mock_readings[self.reading_index]
        self.reading_index = (self.reading_index + 1) % len(self.mock_readings)
        return value

    def display_message(self, message, x=0, y=0, clear=True):
        self.displayed_messages.append(message)

# Helper function for approximate equality
def approx_equal(a, b, tolerance=1e-6):
    return abs(a - b) < tolerance

# Unit tests for static methods
def test_convert_raw_to_bac():
    assert approx_equal(MQ3Sensor.convert_raw_to_bac(1), 0.2)
    assert approx_equal(MQ3Sensor.convert_raw_to_bac(0), 0)
    assert approx_equal(MQ3Sensor.convert_raw_to_bac(5), 1)
    assert approx_equal(MQ3Sensor.convert_raw_to_bac(0.5), 0.1)
    print("test_convert_raw_to_bac passed")

def test_convert_raw_to_gram_per_millilitre():
    assert approx_equal(MQ3Sensor.convert_raw_to_gram_per_millilitre(1), 0.002)
    assert approx_equal(MQ3Sensor.convert_raw_to_gram_per_millilitre(0), 0)
    assert approx_equal(MQ3Sensor.convert_raw_to_gram_per_millilitre(5), 0.01)
    assert approx_equal(MQ3Sensor.convert_raw_to_gram_per_millilitre(0.5), 0.001)
    print("test_convert_raw_to_gram_per_millilitre passed")

def test_convert_raw_to_ppm():
    assert approx_equal(MQ3Sensor.convert_raw_to_ppm(1), 500)
    assert approx_equal(MQ3Sensor.convert_raw_to_ppm(0), 0)
    assert approx_equal(MQ3Sensor.convert_raw_to_ppm(2), 1000)
    assert approx_equal(MQ3Sensor.convert_raw_to_ppm(0.1), 50)
    print("test_convert_raw_to_ppm passed")

# Unit tests for MQ3Sensor methods
def test_calculate_rs():
    # Mock readings that simulate different voltage levels
    mock_readings = [1000, 2000, 3000, 4000]
    mock_hw = MockHardware(mock_readings)
    sensor = MQ3Sensor(mock_hw)
    
    # Replace the mq3_pin.read() method with our mock method
    sensor.hardware.mq3_pin.read = mock_hw.mq3_pin_read
    
    # Test RS calculations
    expected_rs_values = [9900.0, 3900.0, 1900.0, 900.0]
    for expected_rs in expected_rs_values:
        calculated_rs = sensor._calculate_rs()
        assert approx_equal(calculated_rs, expected_rs, tolerance=1.0)
    
    print("test_calculate_rs passed")

def test_read_raw_value_of_alcohol():
    # Mock readings that simulate different alcohol levels
    mock_readings = [1000, 2000, 3000, 4000]
    mock_hw = MockHardware(mock_readings)
    sensor = MQ3Sensor(mock_hw)
    sensor.hardware.mq3_pin.read = mock_hw.mq3_pin_read
    sensor.r0 = 1000  # Set a known R0 value for testing
    
    # Test alcohol raw value calculations
    expected_values = [3.4846, 0.8787, 0.3651, 0.1645]
    for expected_value in expected_values:
        raw_value = sensor.read_raw_value_of_alcohol()
        assert approx_equal(raw_value, expected_value, tolerance=0.001)
    
    print("test_read_raw_value_of_alcohol passed")

def test_get_smoothed_reading():
    mock_readings = [1000, 2000, 3000, 4000, 3000, 2000, 1000]
    mock_hw = MockHardware(mock_readings)
    sensor = MQ3Sensor(mock_hw)
    sensor.hardware.mq3_pin.read = mock_hw.mq3_pin_read
    sensor.r0 = 1000  # Set a known R0 value for testing
    
    # Test smoothed readings
    expected_values = [3.4846, 2.1816, 1.5761, 1.2232, 1.0375, 0.9247, 0.8787]
    for expected_value in expected_values:
        smoothed_value = sensor.get_smoothed_reading()
        assert approx_equal(smoothed_value, expected_value, tolerance=0.001)
    
    print("test_get_smoothed_reading passed")

# Integration tests
def test_sensor_calibration():
    mock_readings = [2000] * NUM_CALIBRATION_READINGS  # Constant reading for simplicity
    mock_hw = MockHardware(mock_readings)
    sensor = MQ3Sensor(mock_hw)
    sensor.hardware.mq3_pin.read = mock_hw.mq3_pin_read
    
    sensor.calibrate()
    
    expected_r0 = 3900.0 / AIR_R0_RATIO
    assert approx_equal(sensor.r0, expected_r0, tolerance=1.0)
    assert "Calibrating..." in mock_hw.displayed_messages
    assert "Calibration done" in mock_hw.displayed_messages
    
    print("test_sensor_calibration passed")

def test_full_reading_cycle():
    mock_readings = [2000, 3000, 4000]  # Simulating changing alcohol levels
    mock_hw = MockHardware(mock_readings)
    sensor = MQ3Sensor(mock_hw)
    sensor.hardware.mq3_pin.read = mock_hw.mq3_pin_read
    sensor.r0 = 1000  # Set a known R0 value for testing
    
    # Simulate a full reading cycle
    raw_alcohol = sensor.get_smoothed_reading()
    ppm = sensor.convert_raw_to_ppm(raw_alcohol)
    bac = sensor.convert_raw_to_bac(raw_alcohol)
    g_per_ml = sensor.convert_raw_to_gram_per_millilitre(raw_alcohol)
    
    # Check if the values are in expected ranges
    assert 0 < raw_alcohol < 5
    assert 0 < ppm < 2500
    assert 0 < bac < 1
    assert 0 < g_per_ml < 0.01
    
    print("test_full_reading_cycle passed")

def run_tests():
    test_convert_raw_to_bac()
    test_convert_raw_to_gram_per_millilitre()
    test_convert_raw_to_ppm()
    test_calculate_rs()
    test_read_raw_value_of_alcohol()
    test_get_smoothed_reading()
    test_sensor_calibration()
    test_full_reading_cycle()
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
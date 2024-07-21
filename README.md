# Bruh-thalyzer

Bruh-thalyzer is an ESP32-based breathalyzer project using the MQ3 alcohol sensor. This project provides a portable solution for measuring alcohol content in breath, with features such as OLED display output, data logging, and button-controlled operations.

## Contents

- `main.py`: The main script that runs the breathalyzer
- `config.py`: Configuration settings for the project
- `hardware.py`: Hardware interface for MQ3 sensor and OLED display
- `sensor.py`: MQ3 sensor calculations and management
- `logging.py`: Simple logging module for MicroPython
- `test_sensor.py`: Comprehensive test suite for the sensor functionality
- `ssd1306.py`: Library for interfacing with the SSD1306 OLED display

## Hardware Requirements

- ESP32 development board
- MQ3 alcohol sensor
- SSD1306 OLED display
- Pushbutton (for control)

## Setup

1. Connect the MQ3 sensor to the appropriate analog pin on the ESP32 (default is pin 34).
2. Connect the SSD1306 OLED display to the I2C pins (default SCL: 22, SDA: 21).
3. Connect a pushbutton to the designated pin (default is pin 0, which is often the BOOT button on ESP32 boards).
4. Upload all the Python files to your ESP32 board using your preferred method (e.g., Thonny IDE, ampy, etc.).

## Usage

1. Power on the ESP32 board.
2. Long press the button to turn on the device. The OLED display will show "ON".
3. Wait for the sensor to warm up and calibrate (this process takes about 20 seconds).
4. Once calibrated, the device will continuously display alcohol readings on the OLED screen.
5. To recalibrate the sensor, short press the button.
6. To turn off the device, long press the button again. The OLED display will show "OFF".

## Running Tests

To run the test suite:

1. Upload `test_sensor.py` to your ESP32 board.
2. Run `test_sensor.py` directly on the board.

Alternatively, you can modify `main.py` to include a test mode that runs when a specific condition is met (e.g., button pressed during startup).

## Customization

You can customize various parameters in the `config.py` file, such as pin assignments, calibration settings, and logging options.

## Contributing

Contributions to the Bruh-thalyzer project are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project is for educational and experimental purposes only. It should not be used as a reliable measure of intoxication or as a replacement for professional breathalyzer equipment. Always drink responsibly and do not drink and drive.
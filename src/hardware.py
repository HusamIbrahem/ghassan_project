import time

import gpiozero
from Adafruit_ADS1x15 import ADS1115
from Adafruit_HTU21D.HTU21D import HTU21D
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class Hardware:
    def __init__(self, ph4=1500.0, ph7=2000.0, ec1413=1413.0):
        try:
            # Calibration values
            self.ph4 = ph4
            self.ph7 = ph7
            self.ec1413 = ec1413

            # Actuators
            self.water_pump = gpiozero.DigitalOutputDevice(18)
            self.water_valve = gpiozero.DigitalOutputDevice(23)
            self.buzzer = gpiozero.DigitalOutputDevice(22)
            self.light = gpiozero.DigitalOutputDevice(0)
            self.vent = gpiozero.DigitalOutputDevice(24)
            self.green_led = gpiozero.DigitalOutputDevice(20)
            self.red_led = gpiozero.DigitalOutputDevice(7)
            self.blue_led = gpiozero.DigitalOutputDevice(8)
            self.water_led = gpiozero.DigitalOutputDevice(9)
            self.fertilization_pump = gpiozero.DigitalOutputDevice(5)
            self.ph_up_pump = gpiozero.DigitalOutputDevice(26)
            self.ph_down_pump = gpiozero.DigitalOutputDevice(19)

            # Sensors
            self.ph = ADS1115(address=0x49, busnum=1)
            self.ec = ADS1115(address=0x48, busnum=1)
            self.water_temperature = gpiozero.DigitalInputDevice(5)
            self.air_temperature_and_humidity = HTU21D()
            self.water_level_bottom = gpiozero.Button(27)
            self.water_level_top = gpiozero.Button(17)
            self.button = gpiozero.Button(21)
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise e

    # actuators --------------------

    def control_water_pump(self, state: bool):
        """Control the water pump."""
        try:
            if state:
                self.water_pump.on()
            else:
                self.water_pump.off()
        except Exception as e:
            logger.error(f"Error controlling water pump: {e}")

    def control_water_valve(self, state: bool):
        """Control the water valve."""
        try:
            if state:
                self.water_valve.on()
            else:
                self.water_valve.off()
        except Exception as e:
            logger.error(f"Error controlling water valve: {e}")

    def control_light(self, state: bool):
        """Control shelf lights."""
        try:
            if state:
                self.light.on()
            else:
                self.light.off()
        except Exception as e:
            logger.error(f"Error controlling lights: {e}")

    def control_vent(self, state: bool):
        """
        Control the vent's state.
        :param state: True to turn the vent on, False to turn it off.
        """
        try:
            if state:
                self.vent.on()
            else:
                self.vent.off()
        except Exception as e:
            logger.error(f"Error controlling vent: {e}")

    def control_red_led(self, state: bool):
        """Control the red LED state."""
        try:
            if state:
                self.red_led.on()
                logger.info("Red LED turned on.")
            else:
                self.red_led.off()
                logger.info("Red LED turned off.")
        except Exception as e:
            logger.error(f"Error controlling red LED: {e}")

    def control_blue_led(self, state: bool):
        """Control the blue LED state."""
        try:
            if state:
                self.blue_led.on()
                logger.info("Blue LED turned on.")
            else:
                self.blue_led.off()
                logger.info("Blue LED turned off.")
        except Exception as e:
            logger.error(f"Error controlling blue LED: {e}")

    def control_green_led(self, state: bool):
        """Control the green LED state."""
        try:
            if state:
                self.green_led.on()
                logger.info("Green LED turned on.")
            else:
                self.green_led.off()
                logger.info("Green LED turned off.")
        except Exception as e:
            logger.error(f"Error controlling green LED: {e}")

    def control_water_led(self, state: bool):
        """Control the water LED state."""
        try:
            if state:
                self.water_led.on()
                logger.info("Water LED turned on.")
            else:
                self.water_led.off()
                logger.info("Water LED turned off.")
        except Exception as e:
            logger.error(f"Error controlling water LED: {e}")

    def control_fertilization_pump(self, state: bool, duration: float = None):
        """Control the fertilization Pump state."""
        try:
            if state:
                self.fertilization_pump.on()
                logger.info("fertilization pump turned on.")
                if duration:
                    time.sleep(duration)  # Keep the pump on for the specified duration
                    self.fertilization_pump.off()
                    logger.info(f"fertilization pump turned off after {duration} seconds.")
            else:
                self.fertilization_pump.off()
                logger.info("fertilization pump turned off.")
        except Exception as e:
            logger.error(f"Error controlling fertilization pump: {e}")

    def control_ph_up_pump(self, state: bool, duration: float = None):
        """Control the ph up Pump state."""
        try:
            if state:
                self.ph_up_pump.on()
                logger.info("ph up pump turned on.")
                if duration:
                    time.sleep(duration)  # Keep the pump on for the specified duration
                    self.ph_up_pump.off()
                    logger.info(f"ph up pump turned off after {duration} seconds.")
            else:
                self.ph_up_pump.off()
                logger.info("ph up pump turned off.")
        except Exception as e:
            logger.error(f"Error controlling ph up pump: {e}")

    def control_ph_down_pump(self, state: bool, duration: float = None):
        """Control the ph down Pump state."""
        try:
            if state:
                self.ph_down_pump.on()
                logger.info("ph down pump turned on.")
                if duration:
                    time.sleep(duration)  # Keep the pump on for the specified duration
                    self.ph_down_pump.off()
                    logger.info(f"ph down pump turned off after {duration} seconds.")
            else:
                self.ph_down_pump.off()
                logger.info("ph down pump turned off.")
        except Exception as e:
            logger.error(f"Error controlling ph down pump: {e}")

    # sensors --------------------
    def read_ph_voltage(self):
        """Read the raw pH voltage."""
        try:
            readings = [self.ph.read_adc_difference(0, gain=1) * 4.096 / 32767 for _ in range(5)]
            return round(statistics.mean(readings), 3)
        except Exception as e:
            logger.error(f"Error reading pH voltage: {e}")
            return None

    def read_ph_value(self, ph4=None, ph7=None):
        """Read calibrated pH value."""
        try:
            ph4 = ph4 if ph4 is not None else self.ph4
            ph7 = ph7 if ph7 is not None else self.ph7
            voltage = self.read_ph_voltage()

            if voltage and ph4 and ph7:
                slope = (7.0 - 4.0) / ((ph7 - 1500.0) / 3.0 - (ph4 - 1500.0) / 3.0)
                intercept = 7.0 - slope * (ph7 - 1500.0) / 3.0
                value = slope * (voltage - 1500.0) / 3 + intercept
                return round(value, 2)
            else:
                raise ValueError("Missing calibration values or voltage for pH calculation.")
        except Exception as e:
            logger.error(f"Error reading pH value: {e}")
            return None

    def read_ec_voltage(self):
        """Read the raw EC voltage."""
        try:
            sensor_channel = self.ec
            voltage_samples = [
                (sensor_channel.read_adc_difference(0, gain=2) * 2.048 / 32767 if sensor_channel.read_adc_difference(0,
                                                                                                                     gain=2) * 2.048 / 32767 < 2.048
                 else (
                    sensor_channel.read_adc_difference(0, gain=1) * 4.096 / 32767 if sensor_channel.read_adc_difference(
                        0, gain=1) * 4.096 / 32767 < 4.096
                    else sensor_channel.read_adc_difference(0, gain=2 / 3) * 6.144 / 32767))
                for _ in range(5)]
            return round(statistics.mean(voltage_samples), 3)
        except Exception as e:
            logger.error(f"Error reading EC voltage: {e}")
            return None

    def read_ec_value(self, ec1413=None):
        """Read calibrated EC value."""
        try:
            ec1413 = ec1413 if ec1413 is not None else self.ec1413
            voltage = self.read_ec_voltage()
            temperature = self.read_water_temperature()

            if voltage and temperature and ec1413:
                voltage = float(voltage) * 1000.0
                temp_coefficient = 1.0 + 0.0185 * (float(temperature) - 25.0)
                ec_voltage = voltage / temp_coefficient
                k = ec1413 / ec_voltage
                value = ec_voltage * k
                value_ms = round(value / 1000.0, 3)
                return value_ms
            else:
                raise ValueError("Missing calibration values or voltage for EC calculation.")
        except Exception as e:
            logger.error(f"Error reading EC value: {e}")
            return None

    def read_water_temperature(self):
        """Simulated method to read water temperature."""
        try:
            return round(self.water_temperature.value, 3)
        except Exception as e:
            logger.error(f"Error reading water temperature: {e}")
            return None

    def read_water_level_bottom_status(self):
        """Check the status of the bottom water level sensor.
        Status True indicates the water is full at the bottom level."""
        try:
            return self.water_level_bottom.is_active
        except Exception as e:
            logger.error(f"Error reading bottom water level status: {e}")
            return None

    def read_water_level_top_status(self):
        """Check the status of the top water level sensor.
        Status True indicates the water is full at the top level."""
        try:
            return self.water_level_top.is_active
        except Exception as e:
            logger.error(f"Error reading top water level status: {e}")
            return None

    def read_air_temperature(self):
        """Read air temperature using the HTU21D sensor."""
        try:
            return round(self.air_temperature_and_humidity.read_temperature(), 3)
        except Exception as e:
            logger.error(f"Error reading air temperature: {e}")
            return None

    def read_air_humidity(self):
        """Read air humidity using the HTU21D sensor."""
        try:
            return round(self.air_temperature_and_humidity.read_humidity(), 3)
        except Exception as e:
            logger.error(f"Error reading air humidity: {e}")
            return None

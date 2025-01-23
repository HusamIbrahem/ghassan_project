# import gpiozero
# from Adafruit_ADS1x15 import ADS1115
from time import sleep
import statistics


class Hardware:
    def __init__(self):
        try:
            pass
            # Actuators
            # self.water_pump = gpiozero.DigitalOutputDevice(18)
            # self.water_valve = gpiozero.DigitalOutputDevice(23)
            # self.buzzer = gpiozero.DigitalOutputDevice(22)
            # self.light_top_shelf = gpiozero.DigitalOutputDevice(0)
            # self.light_middle_shelf = gpiozero.DigitalOutputDevice(1)
            # self.light_bottom_shelf = gpiozero.DigitalOutputDevice(12)
            # self.vent = gpiozero.DigitalOutputDevice(24)
            # self.green_led = gpiozero.DigitalOutputDevice(20)
            # self.red_led = gpiozero.DigitalOutputDevice(7)
            # self.blue_led = gpiozero.DigitalOutputDevice(8)
            # self.water_led = gpiozero.DigitalOutputDevice(9)
            #
            # # Sensors
            # self.ph = ADS1115(address=0x49, busnum=1)
            # self.ec = ADS1115(address=0x48, busnum=1)
            # self.water_temperature = gpiozero.DigitalInputDevice(5)
            # self.air_temperature = gpiozero.DigitalInputDevice(6)
            # self.air_humidity = gpiozero.DigitalInputDevice(13)
            # self.water_level_bottom = gpiozero.Button(27)
            # self.water_level_top = gpiozero.Button(17)
            # self.door = gpiozero.Button(11)
            # self.button = gpiozero.Button(21)
        except Exception as e:
            raise e

    def turn_on(self, actuator: str):
        """Turn on the specified actuator."""
        actuator_obj = getattr(self, actuator, None)
        pass
        # if actuator_obj and isinstance(actuator_obj, gpiozero.DigitalOutputDevice):
        #     actuator_obj.on()
        # else:
        #     raise ValueError(f"Actuator '{actuator}' not found or is not a valid actuator.")

    def turn_off(self, actuator: str):
        """Turn off the specified actuator."""
        actuator_obj = getattr(self, actuator, None)
        pass
        # if actuator_obj and isinstance(actuator_obj, gpiozero.DigitalOutputDevice):
        #     actuator_obj.off()
        # else:
        #     raise ValueError(f"Actuator '{actuator}' not found or is not a valid actuator.")

    def read_data(self, sensor: str):
        """Get data from the specified sensor."""
        return 1
        # if sensor == "ph":
        #     readings = [self.ph.read_adc_difference(0, gain=1) * 4.096 / 32767 for _ in range(5)]
        #     return round(statistics.mean(readings), 3)
        # elif sensor == "ec":
        #     sensor_channel = self.ec
        #     voltage_samples = [
        #         (sensor_channel.read_adc_difference(0, gain=2) * 2.048 / 32767 if sensor_channel.read_adc_difference(0, gain=2) * 2.048 / 32767 < 2.048
        #          else (sensor_channel.read_adc_difference(0, gain=1) * 4.096 / 32767 if sensor_channel.read_adc_difference(0, gain=1) * 4.096 / 32767 < 4.096
        #                else sensor_channel.read_adc_difference(0, gain=2 / 3) * 6.144 / 32767))
        #         for _ in range(5)]
        #     return round(statistics.mean(voltage_samples), 3)
        # elif sensor == "water_temperature":
        #     readings = [self.water_temperature.value for _ in range(5)]
        #     return round(statistics.mean(readings), 3)
        # elif sensor == "air_temperature":
        #     readings = [self.air_temperature.value for _ in range(5)]
        #     return round(statistics.mean(readings), 3)
        # elif sensor == "air_humidity":
        #     readings = [self.air_humidity.value for _ in range(5)]
        #     return round(statistics.mean(readings), 3)
        # elif sensor == "water_level_bottom":
        #     return self.water_level_bottom.is_active
        # elif sensor == "water_level_top":
        #     return self.water_level_top.is_active
        # elif sensor == "door":
        #     return "Closed" if self.door.is_active else "Opened"
        # elif sensor == "button":
        #     return "Pressed" if self.button.is_active else "Not Pressed"
        # else:
        #     raise ValueError(f"Sensor '{sensor}' not found.")

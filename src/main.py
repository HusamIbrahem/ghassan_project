import argparse
import logging
import time
from threading import Thread

from logging.handlers import RotatingFileHandler
import os
from os.path import join
from hardware import Hardware
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log", action="store",
                    dest="log_files_path", help="Path to write log files")
logger = logging.getLogger("schedule-water-pump")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Initialize Hardware
hd = Hardware()

# Configuration for temperature and humidity thresholds
HIGH_AIR_TEMPERATURE_THRESHOLD = 30  # High air temperature threshold (°C)
LOW_AIR_TEMPERATURE_THRESHOLD = 25  # Low air temperature threshold (°C)
HIGH_AIR_HUMIDITY_THRESHOLD = 80  # High air humidity threshold (%)
LOW_AIR_HUMIDITY_THRESHOLD = 40  # Low air humidity threshold (%)
air_temperature_readings = []  # Store the last 5 air temperature readings
air_humidity_readings = []  # Store the last 5 air humidity readings


def check_temperature_and_humidity():
    # Read the current air temperature and humidity from the sensors
    air_temperature = hd.read_air_temperature()
    air_humidity = hd.read_air_humidity()

    logger.info(f"Current Air Temperature: {air_temperature}°C, Current Air Humidity: {air_humidity}%")

    # Add the new readings to the respective lists
    air_temperature_readings.append(air_temperature)
    air_humidity_readings.append(air_humidity)

    # If we have at least 5 readings, calculate the averages
    if len(air_temperature_readings) >= 5:
        # Keep only the last 5 readings for both temperature and humidity
        air_temperature_readings.pop(0)
        air_humidity_readings.pop(0)

        # Calculate the average of the last 5 readings for temperature and humidity
        avg_air_temperature = sum(air_temperature_readings) / len(air_temperature_readings)
        avg_air_humidity = sum(air_humidity_readings) / len(air_humidity_readings)

        logger.info(f"Average Air Temperature of Last 5 Minutes: {avg_air_temperature}°C")
        logger.info(f"Average Air Humidity of Last 5 Minutes: {avg_air_humidity}%")

        # Control vent based on air temperature and humidity
        if avg_air_temperature > HIGH_AIR_TEMPERATURE_THRESHOLD or avg_air_humidity > HIGH_AIR_HUMIDITY_THRESHOLD:
            logger.info("Average air temperature or humidity is high. Turning vent ON.")
            hd.control_vent(True)
        elif avg_air_temperature < LOW_AIR_TEMPERATURE_THRESHOLD and avg_air_humidity < LOW_AIR_HUMIDITY_THRESHOLD:
            logger.info("Average air temperature and humidity are low. Turning vent OFF.")
            hd.control_vent(False)
        else:
            logger.info("Air temperature and humidity are in the normal range. Keeping vent OFF.")
    else:
        logger.info("Not enough data yet. Need 5 readings to calculate averages.")


PH_MAX = 7.5  # Maximum pH level
PH_MIN = 5.5  # Minimum pH level
EC_MAX = 2.5  # Maximum EC level (mS/cm)
EC_MIN = 1.0  # Minimum EC level (mS/cm)
ph_readings = []  # Store the last 5 pH readings
ec_readings = []  # Store the last 5 EC readings
last_injection_time = None  # Track the last time we performed F1 and F2 pump injections


def control_pump(pump_name, duration):
    hd.turn_on(pump_name)
    time.sleep(duration)
    hd.turn_off(pump_name)


def check_ph_and_ec():
    global last_injection_time
    # Read the current pH, EC, and water temperature from the sensors
    ph = hd.read_ph_value()
    ec = hd.read_ec_value()
    logger.info(f"Current pH: {ph}, Current EC: {ec} mS/cm")
    # Add the new readings to the respective lists
    ph_readings.append(ph)
    ec_readings.append(ec)
    # If we have at least 5 readings, calculate the averages
    if len(ph_readings) >= 5:
        # Keep only the last 5 readings for both pH and EC
        ph_readings.pop(0)
        ec_readings.pop(0)
        # Calculate the average of the last 5 readings for pH and EC
        avg_ph = sum(ph_readings) / len(ph_readings)
        avg_ec = sum(ec_readings) / len(ec_readings)
        logger.info(f"Average pH of Last 5 Minutes: {avg_ph}")
        logger.info(f"Average EC of Last 5 Minutes: {avg_ec} mS/cm")
        # Control pH Pumps
        if avg_ph > PH_MAX:
            logger.info("Average pH is high. Turning pH- pump ON for 10 seconds.")
            Thread(target=control_pump, args=("ph-", 10)).start()
        elif avg_ph < PH_MIN:
            logger.info("Average pH is low. Turning pH+ pump ON for 10 seconds.")
            Thread(target=control_pump, args=("ph+", 10)).start()
        # Control EC-based pump injections (F1 and F2)
        current_time = datetime.now()
        # Check if it's 15:00 and within the 5-minute window (15:00 - 15:05)
        if current_time.hour == 15 and 5 >= current_time.minute >= 0 == current_time.second:
            # Ensure we have not already injected today
            if avg_ec < EC_MIN and (
                    last_injection_time is None or current_time - last_injection_time > timedelta(days=1)):
                logger.info("EC is below the minimum threshold. Starting F1 and F2 pumps.")
                # Start F1 and F2 pumps sequentially
                Thread(target=control_pump, args=("f1", 20)).start()
                Thread(target=control_pump, args=("f2", 20)).start()
                # Update last injection time to the current time
                last_injection_time = current_time
            else:
                logger.info("EC is above the minimum threshold or F1/F2 pumps were already injected today.")
    else:
        logger.info("Not enough data yet. Need 5 readings to calculate averages.")


LIGHT_ON_TIME = "06:00"
LIGHT_OFF_TIME = "18:00"
GRACE_PERIOD = 5  # Grace period in minutes

# Global variable to track light state
is_light_on = False


def is_time_between(start_time, end_time):
    """Helper function to check if the current time is between start and end times."""
    now = datetime.now().time()
    return start_time <= now <= end_time


def check_light_schedule():
    global is_light_on

    # Get current time
    current_time = datetime.now()

    # Define the scheduled times (convert to datetime objects)
    light_on_time = datetime.strptime(LIGHT_ON_TIME, "%H:%M")
    light_off_time = datetime.strptime(LIGHT_OFF_TIME, "%H:%M")

    # Add grace period for turning on/off light
    light_on_time = light_on_time - timedelta(minutes=GRACE_PERIOD)
    light_off_time = light_off_time + timedelta(minutes=GRACE_PERIOD)

    # Check if the current time is within the grace period to turn the light on or off and If light is not already on
    if light_on_time <= current_time <= light_on_time + timedelta(minutes=GRACE_PERIOD) and not is_light_on:
        logger.info("Turning light ON.")
        hd.control_light(True)  # Assuming "light" is the ID for the light
        is_light_on = True  # Track light state
    # If light is currently on and light should be off
    elif light_off_time <= current_time <= light_off_time + timedelta(minutes=GRACE_PERIOD) and is_light_on:
        logger.info("Turning light OFF.")
        hd.control_light(False)  # Assuming "light" is the ID for the light
        is_light_on = False  # Track light state


# Constants for the hardware
WATER_LEVEL_BOTTOM_PIN = "water_level_bottom"  # Replace with actual sensor pin
WATER_LEVEL_TOP_PIN = "water_level_top"  # Replace with actual sensor pin
WATER_VALVE_PIN = "water_valve"  # Replace with actual pump pin

# Schedule and Grace Period Configuration
WATER_PUMP_ON_TIME = "06:00"
WATER_PUMP_OFF_TIME = "18:00"

# Global variables
bottom_sensor_readings = []  # Store last 5 readings of the bottom sensor
water_filling_started_at = None  # Track when water filling started
is_water_pump_on = False  # Flag to track whether the water pump is on

water_filling_duration = 180  # 3 minutes of water filling time


def control_water_filling_pump(duration):
    """Control the water filling pump (water valve)."""
    hd.control_water_valve(True)
    time.sleep(duration)
    hd.control_water_valve(False)


def check_water_tank_and_circulation():
    global bottom_sensor_readings, water_filling_started_at, is_water_pump_on

    # Read the bottom and top water level sensors
    bottom_sensor = hd.read_water_level_bottom_status()  # 1 = low water level, 0 = high water level
    top_sensor = hd.read_water_level_top_status()  # 1 = tank full, 0 = not full

    # Add the new reading to the bottom sensor readings list
    bottom_sensor_readings.append(bottom_sensor)
    if len(bottom_sensor_readings) > 5:
        bottom_sensor_readings.pop(0)  # Keep only the last 5 readings

    logger.info(f"Current Bottom Sensor: {bottom_sensor}, Current Top Sensor: {top_sensor}")

    # If bottom sensor shows low water level for last 5 readings, start water filling pump
    if all(sensor == 1 for sensor in bottom_sensor_readings) and water_filling_started_at is None:
        logger.info("Bottom sensor shows low water level. Starting water filling pump.")
        water_filling_started_at = datetime.now()
        Thread(target=control_water_filling_pump, args=(water_filling_duration,)).start()

    # If top sensor shows full water level, turn off water filling pump
    if top_sensor == 1 and water_filling_started_at is not None:
        logger.info("Top sensor shows full water level. Turning off water filling pump.")
        hd.control_water_valve(False)
        water_filling_started_at = None  # Reset the filling start time

    # Stop pump if filling duration has elapsed
    if water_filling_started_at is not None and (
            datetime.now() - water_filling_started_at).seconds >= water_filling_duration:
        if all(sensor == 1 for sensor in bottom_sensor_readings):
            logger.info("Filling duration complete. Turning off water filling pump.")
            hd.control_water_valve(False)
            water_filling_started_at = None  # Reset filling time
        else:
            logger.info("Filling stopped early due to water level change.")
            water_filling_started_at = None

    # Check if the bottom sensor shows sufficient water (0) and the pump should turn on based on a schedule
    if bottom_sensor == 0:  # Sufficient water level detected
        current_time = datetime.now().time()
        pump_on_time = datetime.strptime(WATER_PUMP_ON_TIME, "%H:%M").time()
        pump_off_time = datetime.strptime(WATER_PUMP_OFF_TIME, "%H:%M").time()

        # If water pump is off and within the schedule, turn it on
        if not is_water_pump_on and pump_on_time <= current_time <= pump_off_time:
            logger.info("It's time to turn on the water pump as per the schedule.")
            hd.control_water_valve(True)
            is_water_pump_on = True

        # If water pump is on and past the grace period, turn it off
        elif water_filling_started_at is not None:
            if is_water_pump_on and (datetime.now() - water_filling_started_at).seconds >= GRACE_PERIOD * 60:
                logger.info("Water pump has been on past grace period. Turning it off.")
                hd.control_water_valve(False)
                is_water_pump_on = False

    else:
        # If water level is low, track the start time and respect the grace period for shutdown
        if water_filling_started_at is None:
            water_filling_started_at = datetime.now()  # Start timer when water is low
        elif water_filling_started_at is not None and (
                datetime.now() - water_filling_started_at).seconds >= GRACE_PERIOD * 60:
            logger.info("Water level is low past grace period. Turning off water pump.")
            hd.control_water_valve(False)
            is_water_pump_on = False


def app():
    logger.info("Starting Hydroponics Ventilation System")
    # Main loop to check air temperature and humidity every minute
    try:
        while True:
            check_temperature_and_humidity()
            check_ph_and_ec()
            check_light_schedule()
            check_water_tank_and_circulation()
            time.sleep(5)  # Wait for 1 minute before checking again
    except KeyboardInterrupt:
        logger.info("Hydroponics Control System stopped manually.")


if __name__ == "__main__":
    try:
        # Set configurations of the script
        args = parser.parse_args()
        if args.log_files_path:
            os.makedirs(args.log_files_path, exist_ok=True)
            file_handler = RotatingFileHandler(join(args.log_files_path, "water-system.log"), mode='a',
                                               maxBytes=5 * 1024 * 1024, backupCount=2)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logging.getLogger('werkzeug').setLevel(logging.INFO)
            logging.getLogger('werkzeug').addHandler(file_handler)
            logger.info(f'Writing logs to file: {join(args.log_files_path, "water-system.log")}')
        # Start hardware
        # hd = Hardware()
        app()

    except Exception as e:
        logger.error(f"Error: {e}")

# with open("settings.json", "r") as jsonfile:
#     settings = json.load(jsonfile)
# while True:
#     schedule.run_pending()
#     sleep(1)
# every 5 minutes check water level bottom, if water level is down -> turn on water filling and when water level top is up -> turn off water filling
# turn water pump every dat at defined time and turn off att defined times
# water pump should start only if water level bottom is up, if it is down it will wait for the filling and then turn on again
# lights should work every dat at defined time and turn off att defined times
# we should make ph at defined value -> every minute check the value and it should turn on ph+ or ph- at defined mount until the value reach the defined ph, you can take the average of last 5 measurments always
# ec should be at defined values -> inject ec at defiend time daily only if it under the 80% under the defined value
# ph and ec should make the policy only if water pump is on
# vent should work every dat at defined time and turn off att defined times
# we have 4 leds status -> script working/ not working, ph good/basd, ec good/bad, tank level(empty/not empty)

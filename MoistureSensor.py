import secrets
import moisture

from machine import Pin, Timer, RTC

from umqtt.simple import MQTTClient # type: ignore
import network
import ujson
import ntptime

import time
from logs import log


class MoistureSensor:
  """
  Constructor
  """
  def __init__(self, mqtt_sensor_id, mqtt_topic_moisture):
    # Initialize LED pin
    self.pin = Pin("LED", Pin.OUT)
    
    # Initialize blink state
    self._blink_timer = Timer()
    self._blink_active = False

    # Initialize RTC
    self.rtc = RTC()

    # Initialize moisture sensor
    self.mqtt_sensor_id = mqtt_sensor_id
    self.mqtt_topic_moisture = mqtt_topic_moisture

    # Initialize connection
    self.connect_wifi()
    self.sync_time()  # Sync time after WiFi connection
    self.connect_mqtt()

  """
  Blinks the LED
  """
  def _blink_callback(self, _):
    """Timer callback function to handle LED blinking"""
    if self._blink_active:
      self.pin.toggle()

  """
  Start the LED blinking using a timer
  Args:
      rate: Time in seconds between blinks (default: 1.0)
  """
  def start_blinking(self, rate=1.0):
    self.stop_blinking()  # Stop any existing blinking
    self._blink_active = True
    # Convert rate to milliseconds and divide by 2 since we need two toggles per blink
    period_ms = int(rate * 1000 / 2)
    self._blink_timer.init(mode=Timer.PERIODIC, period=period_ms, callback=self._blink_callback)

  """Stop the LED blinking and ensure it's off"""
  def stop_blinking(self):
    self._blink_active = False
    self._blink_timer.deinit()
    self.pin.off()

  """
  Connects to wifi
  - Retries until wifi is connected
  - Blinks LED every 0.5 seconds to indicate connecting
  """
  def connect_wifi(self):
    self.pin.off()
    log.info(f'[WIFI] Connecting to network: {secrets.SSID}')

    # Initialize WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Start LED blinking at 0.5 second rate
    self.start_blinking(rate=0.5)

    # Attempt connection
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    # Wait until the device is connected to the WiFi network
    log.info(f'[WIFI] Waiting for connection...')
    while True:
      """
      WLAN status codes:
        0   STAT_IDLE -- no connection and no activity,
        1   STAT_CONNECTING -- connecting in progress,
        2   no ip found
        3   STAT_GOT_IP -- connection successful.
        -3  STAT_WRONG_PASSWORD -- failed due to incorrect password,
        -2  STAT_NO_AP_FOUND -- failed because no access point replied,
        -1  STAT_CONNECT_FAIL -- failed due to other problems,
      """

      # Check if connection is successful
      if wlan.status() == 3:
        network_info = wlan.ifconfig() # get IP address
        log.info(f'[WIFI] Connection successful: {network_info[0]}')
        self.stop_blinking()
        return True
      
      log.error('[WIFI] Connection failed! Trying again...')
      time.sleep(1)

  """
  Synchronize time with NTP server
  """
  def sync_time(self):
    log.info("[TIME] Synchronizing time with NTP server...")
    self.start_blinking(rate=0.1)  # Fast blink to indicate time sync
    
    try:
      ntptime.settime()  # Connect to NTP server and set the time
      current_time = self.rtc.datetime()
      log.info(f"[TIME] Synchronized. Current time: {current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[4]:02d}:{current_time[5]:02d}:{current_time[6]:02d}")
      self.stop_blinking()
      return True
    except Exception as e:
      log.error(f"[TIME] Failed to sync time: {e}")
      self.stop_blinking()
      return False

  """
  Connects to MQTT broker
  - Retries until connected to broker
  - Blinks LED every 1 second to indicate connecting
  """
  def connect_mqtt(self) -> MQTTClient:
    log.info('[MQTT] Connecting to MQTT broker...')
    self.start_blinking(rate=1.0)  # Start LED blinking with 1s rate
    
    while True:
      try:
        self.client = MQTTClient(secrets.mqtt_client_id,
                          secrets.mqtt_server,
                          port=secrets.mqtt_port)
        # Use a 5 second timeout for more reliable connection
        self.client.connect()
        log.info('[MQTT] Connected to MQTT broker')
        self.stop_blinking()  # Stop LED blinking and turn it off
        return
      except Exception as e:
        log.error(f'[MQTT] Error connecting to MQTT: {e}')
        time.sleep(1)  # Wait before retrying

  """
  Checks if WiFi is still connected
  Returns: True if connected, False if disconnected
  """
  def check_wifi_connection(self):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected() or wlan.status() != 3:  # 3 is STAT_GOT_IP
      log.error("[WIFI] Connection lost")
      return False
    return True

  """
  Gets the sensor readings
  """
  def get_sensor_readings(self):
      # Get moisture reading
      percent = moisture.get_sensor_readings()
      
      # Get current time from RTC
      current_time = self.rtc.datetime()
      timestamp = (
          current_time[0],  # year
          current_time[1],  # month
          current_time[2],  # day
          current_time[4],  # hour
          current_time[5],  # minute
          current_time[6],  # second
          current_time[3],  # weekday
          0                 # yearday (not provided by RTC)
      )
      
      # Format timestamp for logging
      formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
          timestamp[0],  # year
          timestamp[1],  # month
          timestamp[2],  # day
          timestamp[3],  # hour
          timestamp[4],  # minute
          timestamp[5]   # second
      )
      log.info(f'[SENSOR] Reading: [{formatted_time}] moisture: {percent}%')
      return timestamp, percent
  
  """
  Publishes a message to the MQTT broker
  Handles both WiFi and MQTT connection issues
  """
  def publish_mqtt(self, value, retries=5):
    try:
      self.client.publish(self.mqtt_topic_moisture, value)
    except Exception as e:
      log.error(f'[MQTT] Error publishing to MQTT: {e}')
      
      # First check if it's a WiFi issue
      if not self.check_wifi_connection():
        log.info("[WIFI] Attempting to reconnect to WiFi...")
        self.connect_wifi()
      
      # Now try to reconnect to MQTT
      log.info("[MQTT] Attempting to reconnect to broker...")
      self.connect_mqtt()
      
      # Try to publish again after reconnecting
      if retries > 0:
        log.info(f'[MQTT] Retrying publish... ({retries} attempts left)')
        self.publish_mqtt(value, retries=retries - 1)

  """
  Generates a message payload for the moisture sensor
  """
  def generate_reading_message(self, timestamp, percent):
      return ujson.dumps({
        'plant_reader_id': self.mqtt_sensor_id,
        'created_at': timestamp,
        'moisture_level': percent,
        'meta_data': {}
      })

  """
  Main loop
  - Gets sensor readings
  - Generates message payload
  - Publishes message to MQTT broker
  - Waits 10 seconds
  - No led blinking
  """
  def execute(self):

    # Main loop
    while True:
      # Get sensor readings
      timestamp, percent = self.get_sensor_readings()

      # Generate message payload
      payload = self.generate_reading_message(timestamp, percent)

      # Publish as MQTT payload
      self.publish_mqtt(payload)

      # Delay 10 seconds
      time.sleep(10)

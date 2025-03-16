import MoistureSensor
import secrets

def main():
  # Print header
  print("="*50)
  print("Running moisture sensor for sensor ID:", secrets.mqtt_sensor_id)
  print("="*50)

  # Initialize moisture sensor
  moisture_sensor = MoistureSensor.MoistureSensor(secrets.mqtt_sensor_id, secrets.mqtt_topic_moisture)

  # Read moisture levels
  moisture_sensor.execute()

if __name__ == "__main__":
  main()
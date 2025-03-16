# Plant Moisture Sensor

A MicroPython project for the Raspberry Pi Pico that monitors plant moisture levels and reports them to an MQTT broker. The device uses WiFi for connectivity and includes visual LED feedback for different states.

## Features

- Real-time moisture sensing
- WiFi connectivity with automatic reconnection
- MQTT integration for data reporting
- NTP time synchronization
- Visual LED status indicators:
  - Fast blinking (0.1s): Time sync in progress
  - Medium blinking (0.5s): WiFi connecting
  - Slow blinking (1.0s): MQTT connecting
  - LED off: Normal operation

## Hardware Requirements

- [Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
- [Capacitive Soil Moisture Sensor v2.0](https://www.amazon.com/Capacitive-Corrosion-Resistant-3-3V-5-5V-Detection/dp/B09XH5DRXV/ref=asc_df_B09XH5DRXV?mcid=30eea87fce0638beb23ebcdde31202ef&hvocijid=11877988887976499095-B09XH5DRXV-&hvexpln=73&tag=hyprod-20&linkCode=df0&hvadid=721245378154&hvpos=&hvnetw=g&hvrand=11877988887976499095&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9031950&hvtargid=pla-2281435177618&psc=1)
- LED (built-in on Pico)

## Software Dependencies

- MicroPython for Raspberry Pi Pico
- Required MicroPython libraries:
  - `machine`
  - `network`
  - `umqtt.simple`
  - `ntptime`

## Setup

1. Copy the following files to your Pico:

   - `main.py`
   - `MoistureSensor.py`
   - `moisture.py`
   - `logs.py`
   - `secrets.py`

2. Create a `secrets.py` file with your credentials:

```python
# WiFi credentials
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

# MQTT configuration
mqtt_client_id = "your_client_id"
mqtt_server = "your_mqtt_broker"
mqtt_port = 1883  # Default MQTT port
mqtt_sensor_id = "your_sensor_id"
mqtt_topic_moisture = "your/mqtt/topic"
```

---

## Project Stack

- Moisture Sensor - Responsible for measuring moisture levels
- MQTT Server - Interfaces between Moisture Sensor and Database
- Database - Postgres database for persiting readings
- Website - Next.js frontend for displaying readings

## LED Status Indicators

The onboard LED provides visual feedback about the device's status:

- Rapid blinking (0.1s intervals): Time synchronization in progress
- Medium blinking (0.5s intervals): Attempting WiFi connection
- Slow blinking (1.0s intervals): Attempting MQTT connection
- LED off: Normal operation mode

## MQTT Data Format

The sensor publishes JSON messages in the following format:

```json
{
  "plant_reader_id": "your_sensor_id",
  "created_at": [
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "weekday",
    0
  ],
  "moisture_level": "percentage",
  "meta_data": {}
}
```

## Error Handling

The system includes comprehensive error handling for:

- WiFi connection loss
- MQTT broker connection issues
- Time synchronization failures
- Sensor reading errors

All errors are logged with appropriate status messages.

## Operation

1. On startup, the device:

   - Connects to WiFi
   - Synchronizes time with NTP server
   - Establishes MQTT connection

2. Main loop:

   - Reads moisture sensor every 10 seconds
   - Formats data with current timestamp
   - Publishes to MQTT broker
   - Automatically handles connection issues

## Troubleshooting

If the device is not working as expected:

1. Check LED status:

   - If blinking rapidly: Time sync in progress
   - If blinking at medium speed: WiFi connection issue
   - If blinking slowly: MQTT connection issue

2. Common issues:

   - WiFi credentials incorrect
   - MQTT broker unreachable
   - Sensor connection problems

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

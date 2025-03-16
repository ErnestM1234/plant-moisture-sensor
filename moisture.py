from machine import ADC
import time

analog = ADC(26)

"""
Gets the sensor readings
"""
def get_sensor_readings():
    
    # discard first reading
    time.sleep(0.5)
    _ = analog.read_u16()

    # get reading
    time.sleep(0.5)
    voltage = analog.read_u16()
    voltage *= 3.3 / 65535

    # convert voltage to percentage
    percent = ((2.3 - voltage) / (2.3-1.4)) * 100
    if percent > 100:
        percent = 100
    elif percent < 0:
        percent = 0

    return percent
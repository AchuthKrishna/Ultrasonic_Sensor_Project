import board
import time
import digitalio
import pulseio
import simpleio
from adafruit_bus_device import adafruit_hcsr04


ON = 2 ** 15  # Duty cycle constants
OFF = 0

led = pulseio.PWMOut(board.D12)
led.duty_cycle = 20
light_level = led.duty_cycle

buzzer = pulseio.PWMOut(board.D3, variable_frequency=True)
buzzer.frequency = 50
freq = buzzer.frequency

distance_sensor = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)

button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN

#  Change LED light level when closer or farther from object
def light_change(prior_obstacle_distance, new_obstacle_distance):
    difference = new_obstacle_distance - prior_obstacle_distance
    if int(difference) == 0:
        global light_level
        led.duty_cycle = int(light_level)
    else:
        if new_obstacle_distance < 20:
            global light_level
            light_level = 65535
            led.duty_cycle = int(light_level)
        elif new_obstacle_distance <= 150 and new_obstacle_distance > 20 and difference < 0:
            difference = abs(difference)
            light_difference = simpleio.map_range(difference, 0, 149, 20, 55000)
            global light_level
            light_level += light_difference
            if light_level > 65535:
                light_level = 65535
            led.duty_cycle = int(light_level)
        elif new_obstacle_distance <= 150 and new_obstacle_distance > 20 and difference > 0:
            light_difference = simpleio.map_range(difference, 0, 149, 20, 55000)
            global light_level
            light_level -= light_difference
            if light_level < 20:
                light_level = 20
            led.duty_cycle = int(light_level)
        else:
            global light_level
            light_level = 20
            led.duty_cycle = light_level
    return

#  Change buzzer frequency depending on distance from object
def sound_change(prior_obstacle_distance, new_obstacle_distance):
    difference = new_obstacle_distance - prior_obstacle_distance
    if int(difference) == 0:
        global freq
        buzzer.frequency = int(freq)
    else:
        if new_obstacle_distance < 20:
            global freq
            freq = 1000
            buzzer.frequency = int(freq)
        elif new_obstacle_distance <= 150 and new_obstacle_distance > 20 and difference < 0:
            difference = abs(difference)
            sound_difference = simpleio.map_range(difference, 0, 149, 70, 500)
            global freq
            freq += sound_difference
            if freq > 1000:
                freq = 1000
            buzzer.frequency = int(freq)
        elif new_obstacle_distance <= 150 and new_obstacle_distance > 20 and difference > 0:
            sound_difference = simpleio.map_range(difference, 0, 150, 70, 500)
            global freq
            freq -= sound_difference
            if freq < 50:
                freq = 50
            buzzer.frequency = int(freq)
        else:
            global freq
            freq = 50
            buzzer.frequency = freq
    return

buttonState = False
print("Press the button to begin")
print("Press the button again to stop")
sensing = False

while True:
    buttonState = button.value
    time_val = 0  # in seconds
    if button.value == False and buttonState:
        sensing = True
        while sensing:
            buzzer.duty_cycle = ON
            buttonState = button.value
            try:
                dist1 = distance_sensor.distance
                time_val += time.monotonic()
                print(dist1)
                print(time_val)
                time.sleep(0.1)

                dist2 = distance_sensor.distance
                time_val += time.monotonic()
                print(dist2)
                print(time_val)

                sound_change(dist1, dist2)
                light_change(dist1, dist2)
            except RuntimeError:
                buzzer.frequency = 50
                print("Runtime error... retrying")

            if buttonState:
                sensing = False
                print("Stopped sensing.")
                print("Press the button to begin")
                light_level = 20
                freq = 50
                buzzer.duty_cycle = OFF



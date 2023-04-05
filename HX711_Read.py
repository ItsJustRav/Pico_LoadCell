##too do: Connect wifi and update rtc time, add timestamp, issue with file not being created on first run
#----------------------------------------------------------------------------#
# NU Wind Tunnel Pico W HX711 Code											 #
# Authors: Marshall Boden, Ravindu Ranaweera								 #
# HX711 Library: https://github.com/robert-hh/hx711/blob/master/hx711_pio.py #
# Library Instructions: https://github.com/robert-hh/hx711					 #
#----------------------------------------------------------------------------#

## imports
from HX711_gpio import HX711
from machine import Pin
import time

## User settings

# HX711 settings
zero_time = 2 # in seconds, Averages the readings over time at start to zero the load cell
read_raw_avg = 10 # number of readings to average from for 1 value of raw readings > for hx711.read() *Raw means: not scaled, no offset compensation
read_value_avg = 10 # number of readings to average from for 1 value of raw readings > for hx711.get_value()
scale_factor = 10 # scalling factor for hx711.get_units() 
offset_u = 0 # manual offset value in adition to zero-ing for hx711.get_units() 
gain_u = 128 # Gain for the hx711
lowpass_time = 0.1 #Set the time constant used by hx711.read_lowpass(). The range is 0-1.0. Smaller values means longer times to settle and better smoothing. If value is None, the actual value of the time constant is returned.
t_readings = 1 # Time between readings


# File settings
file_name = 'readings' # Data logging file name
f_format = 'txt' # Data logging file format
# heading name in header line (add more if required)
header1 = 'Raw_Value' # Heading for the actual raw value of the load cell. Raw means: not scaled, no offset compensation.
header2 = 'Raw_Value_Avg' # Heading for the raw value of the load cell as the average of times readings of The raw value.
header3 = 'Get_Value' # Heading for the difference of the filtered load cell value and the offset, as set by hx711.set_offset() or hx711.tare().
header4=  'Raw_Filter' # Heading for the actual value of the load cell fed through an one stage IIR lowpass filter. The properties of the filter can be set with set_time_constant().
header5=  'Get_Units' # Heading for the value delivered by hx711.get_value() divided by the scale set by hx711.set_scale().
#header6=  'Callibrated_Value' # Heading for the final value with zero-ing


## Initialising log file and user variables
fname = file_name + '.' + f_format
file = open (fname, 'a')
file.write('<<----------Recording new readings---------->>\n')
i = 0
old_offset = 0

led = Pin("LED", Pin.OUT)

## hx711 settings 7 initialising
pin_OUT = Pin(5, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(4, Pin.OUT)
hx711 = HX711(pin_SCK, pin_OUT)
hx711.power_up()
hx711.set_gain(gain_u)
hx711.tare(times=read_value_avg)
hx711.set_scale(scale_factor)
hx711.set_time_constant(lowpass_time)

## Write settings to log file
file.write('<--Settings-->\n zero_time: %f\n read_raw_ave: %f\n read_value_avg: %f\n scale_factor: %f\n offset_u: %f\n gain: %f\n lowpass_time: %f\n t_readings: %f\n' %(zero_time,read_raw_avg,read_value_avg,scale_factor,offset_u,gain_u,lowpass_time,t_readings))

## Zero-ing loop
print('Zero-ing for:', zero_time, 'seconds')
while i <= zero_time:
    led.on()
    f_read = hx711.get_units()
    offset = old_offset + f_read
    old_offset = offset
    i = i +1
    led.off()
    time.sleep(1)
zero_offset = ((old_offset)/zero_time) + offset_u # Zero offset average calculation from the Zero-ing while loop and manual offset
hx711.set_offset(zero_offset) # Setting the offset for hx711
print('Zero offset set at:', zero_offset)
file.write('Zero offset Value: %f\n<------------>\n' %zero_offset) # Write zero offset value

## Load cell reading loop
file.write((header1+','+header2+','+header3+','+header4+','+header5+'\n'))  # Writing headers to log file for reference
while True:
    try:
        led.on()
        raw_value = hx711.read() # Returns the actual raw value of the load cell. Raw means: not scaled, no offset compensation.
        raw_value_avg = hx711.read_average(times=read_raw_avg) # Returns the raw value of the load cell as the average of times readings of The raw value.
        getvalue = hx711.get_value() # Returns the difference of the filtered load cell value and the offset, as set by hx711.set_offset() or hx711.tare().
        raw_filter = hx711.read_lowpass() # Returns the actual value of the load cell fed through an one stage IIR lowpass filter. The properties of the filter can be set with set_time_constant().
        getunits = hx711.get_units() # Returns the value delivered by hx711.get_value() divided by the scale set by hx711.set_scale().
        print('%f,%f,%f,%f,%f\n' %(raw_value, raw_value_avg,getvalue,raw_filter,getunits))
        file.write('%f,%f,%f,%f,%f\n' %(raw_value, raw_value_avg,getvalue,raw_filter,getunits))
        led.off()
        time.sleep(t_readings)
    except KeyboardInterrupt:
        print('Interrupted (Keyboard)')
        break


## End Sequence
print('Closing...')
led.off()
hx711.power_down()
file.close()
print('Done')
# staging setup

testing hardware in different phases

## phase 1

Indoor testing hardware components for longjevity using standard power. Encountered issue with the wifi usb dongle that would periodically dropped. I was able to track it down to insufficient power. I added a usb power enhancer since there was additional USB ports that code be used. System ran unintrupted for weeks. there was some experimenting with the [ntp drivers](https://www.ntp.org/documentation/drivers/) and offsets to minimize drift. I was able to get the variance down to nanoseconds.

![indoor poc](img/indoor-poc.jpg?raw=true)

## phase 2

Environmental and solar verification started the begining of October. Monitoring the power consumption, the Pi was averaging less than 3 watts and about .25 amps. Early solar shows at peak it was generating 9 amps. The battery and PI storage containers need some ventilation and temprature monitoring. Wifi and GPS signal seems to be strong, can reliably connect via ssh. Rough calculations are that with the current setup the PI should run for about 72 hours on battery.

![staging](img/staging.jpg?raw=true)
![Pi Renogy wanderer 10a controller](img/pi-renogy.jpg?raw=true)
![batteries](img/batteries.jpg?raw=true)
![head, gps and wifi antennam solar panels](img/head.jpg?raw=true)

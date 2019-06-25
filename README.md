# robot arm
robot arm using hobby servos controlled by a Raspberry Pi with an [Adafruit PCA9685 servo controller board](https://www.adafruit.com/product/2327)

## make it run

```
python server.py # server to receive commands
python arm.py # arm control daemon
```


## troubleshooting
make sure i2c is working;
```
sudo watch -n0.2 i2cdetect -y 1
```

if everything is working, will print
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: 70 -- -- -- -- -- -- --
```

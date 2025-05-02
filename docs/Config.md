## Default config file

```json
{
    "f_low": 400.0E6,
    "f_high": 1600.0E6,
    "rbw": 600000.0,
    "points": 2000,
    "verbose": 1,
    "calibration_file": "./config/gain_cal.csv",
    "scan_dir": "scans",
    "pinout": "pi",
    "baudrate": 115200
}
```

### Params
(float) f_low: Start frequency (Hz) 0-12E9 *note anything above 5Ghz is uncalibrated and has a "reduced linearity" warning

(float) f_high: Stop frequency (Hz)  0-12E9 *note anything above 5Ghz is uncalibrated and has a "reduced linearity" warning

(float) rbw: Resolution bandwidth (Hz) (850, 600, 100, 30, 10, 3, 1, 0.2)*E3

(int) points: Number of points to sample, important the RBW and points can actually overlap or not cover the entire band if the 
bandwith and rbw don't cover the entire frequency span, this can be a bit confusing 

(int) verbose: Level of debug information printed to stdout

(str) scan_dir: Directory where scans are stored

(str) pinout: Specifies which type of pins to actuate for the warning systembase on a hardcode sequence called pinout, 
None actuates no pins (pi, None)

(int) baudrate: Baudrate between the raspberry pi and the TinySA, do not change (115200)

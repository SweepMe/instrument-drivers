# BK1785B Series Programmable DC Power Supplies
These files are for the BK1785B Series Programmable DC Power Supplies
  
### Models
Models: 1785B, 1786B, 1787B, 1788


### Documentation
Manual: [Series Manual](https://bkpmedia.s3.amazonaws.com/downloads/manuals/en-us/178xB_manual.pdf)

Data Sheet: [Series Data Sheet](https://bkpmedia.s3.amazonaws.com/downloads/datasheets/en-us/178xB_datasheet.pdf)

### lib1785b basic usage
```python
import serial
import lib1785b
ser = serial.Serial("serial port") # "/dev/ttyUSB0", "com2" etc...
lib1785b.remoteMode(True, ser)
```

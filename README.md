# FreeBSD I2C wrapper for Python

The ```pyfbsdi2c-tspspi``` project contains a very thin wrapper for the ```ioctl``` requests for the ```iic``` device on FreeBSD
to test various hardware devices from Python. It allows direct access to the I2C bus on devices like the RaspberryPi when running
under FreeBSD.

## Installation

```
pip install pyfbsdi2c-tspspi
```

## Usage

The bus can be instantiated using context management of it's constructor. One can select the bus via it's first constructor
argument:

```
from fbsdi2c import FbsdI2C
```

To instantiate via context management one can use:

```
with FbsdI2C() as i2c:
    # Use i2c.
```

To instantiate using the constructor:

```
i2c = FbsdI2C()
# Use i2c.
```

To use multiple busses:

```
i2c0 = FbsdI2C("/dev/iic0")
i2c1 = FbsdI2C("/dev/iic1")
```

## Supported methods

This module exposes the ```pylabdevs``` ```I2CBus``` interface:

### Scanning for bus devices

To print a list with all device addresses that respond:

```
with FbsdI2C() as i2c:
    print(i2c.scan())
```

### Reading and writing from a buffer

```
with FbsdI2C() as i2c:
    i2c.write(0x33, bytearray(1,2,3))
    data = i2c.read(0x33, 5)
```

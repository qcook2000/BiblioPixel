from .. import gamma
from . channel_order import ChannelOrder
from . spi_driver_base import DriverSPIBase


class LPD8806(DriverSPIBase):
    """Main driver for LPD8806 based LED strips on devices like the Raspberry Pi
       and BeagleBone."""

    def __init__(self, num,
                 c_order=ChannelOrder.RGB,
                 spi_speed=2, gamma=gamma.LPD8806, **kwargs):
        super().__init__(num, c_order=c_order, spi_speed=spi_speed, gamma=gamma, **kwargs)

        # LPD8806 requires latch bytes at the end
        self._latchBytes = (self.numLEDs + 31) // 32
        for i in range(0, self._latchBytes):
            self._buf.append(0)

    # LPD8806 requires gamma correction and only supports 7-bits per channel
    # running each value through gamma will fix all of this.


# This is DEPRECATED.
DriverLPD8806 = LPD8806

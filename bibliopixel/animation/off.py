from . animation import BaseAnimation


class OffAnim(BaseAnimation):
    """A trivial animation that turns all pixels in a layout off."""

    def __init__(self, layout, timeout=1, **kwds):
        super().__init__(layout, **kwds)
        self.internal_delay = timeout

    def step(self, amt=1):
        self.layout.all_off()

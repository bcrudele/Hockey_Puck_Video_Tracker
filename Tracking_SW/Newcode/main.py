from trackHSV import trackHSV
from switchtest import *

tracker = trackHSV(1, (5, 150, 150), (15, 255, 255))
tracker.run(0,0)

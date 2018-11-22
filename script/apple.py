# -*- coding: utf-8 -*-
#!/usr/bin/python

import numpy as np
import math
from lathe import Lathe

def apple_cross_section():
    points = []
    divide = 20
    center_radius_upper = 15
    center_radius_lower = 10
    arc_radius = 25
    ellipsoid_short = 30
    ellipsoid_long = 50
    for i in range(divide):
        theta = math.pi / 2 * i / divide
        points.append(np.array([center_radius_upper + arc_radius * math.sin(theta),
                                arc_radius * math.cos(theta)]))
    for i in range(divide + 1):
        theta = math.pi / 2 * i / divide + math.pi / 2
        points.append(np.array([center_radius_lower + ellipsoid_short * math.sin(theta),
                                ellipsoid_long * math.cos(theta)]))


    return points

if __name__ == '__main__':
    lathe = Lathe(apple_cross_section(), 15)
    lathe.run("apple.svg")

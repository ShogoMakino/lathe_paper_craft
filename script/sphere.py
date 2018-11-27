#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import math
from lathe import Lathe

def sphere_cross_section(r, divide = 20):
    points = []
    for i in range(divide + 1):
        theta = math.pi * i / divide
        points.append(r * np.array([math.sin(theta), math.cos(theta)]))
    return points

if __name__ == '__main__':
    lathe = Lathe("sphere.svg")
    lathe.spiral(sphere_cross_section(20), 10)

# -*- coding: utf-8 -*-
#!/usr/bin/python

import svgwrite
import numpy as np
import math

class Lathe:
    def __init__(self):
        pass

    def __init__(self, cross_section, width):
        self.set_width(width)
        self.set_cross_section(cross_section)


    def run(self, filename, step = 2.0 * math.pi / 100, split = []):
        split_start_list = [0.0] + split
        split_end_list = split + [1.0]
        self.open_svg(filename)
        for start, end in zip(split_start_list, split_end_list):
            points = self.expand(step, start, end)
            self.draw_path(points)

    def set_width(self, width):
        self.width = width

    def get_third_point(self, p1, p2, l13, l23, direction=1):
        vec12 = np.array(p2) - np.array(p1)
        l12 = np.linalg.norm(vec12)
        cos = (l13 ** 2 + l12 ** 2 - l23 ** 2) / (2.0 * l13 * l12)
        theta = math.acos(cos) * np.sign(direction)
        vec13 = np.dot(self.rot_matrix(theta), vec12 / l12) * l13
        return p1 + vec13

    def rot_matrix(self, rad):
        return np.array([[math.cos(rad), -math.sin(rad)],
                         [math.sin(rad), math.cos(rad)]]);

    def inner_divide(self, p1, p2, ratio1, ratio2):
        return 1.0 * (p1 * ratio2 + p2 * ratio1) / (ratio1 + ratio2)

    def get_point_2d(self, theta):
        l = self.width * theta / (2.0 * math.pi)
        if l <= 0:
            return self.cross_section[0][0:2]
        elif l >= self.cross_section[-1][2]:
            return self.cross_section[-1][0:2]

        for i in range(len(self.cross_section) - 1):
            if l == self.cross_section[i][2]:
                return self.cross_section[i][0:2]
            elif (self.cross_section[i][2] < l and
                  l < self.cross_section[i + 1][2]):
                return self.inner_divide(self.cross_section[i][0:2],
                                         self.cross_section[i + 1][0:2],
                                         l - self.cross_section[i][2],
                                         self.cross_section[i + 1][2] - l)

    def get_point_3d(self, theta):
        point_2d = self.get_point_2d(theta)
        return np.array([point_2d[0] * math.cos(theta),
                         point_2d[0] * math.sin(theta),
                         point_2d[1]])

    def set_cross_section(self, points):
        self.cross_section = []
        for p in points:
            if len(self.cross_section) == 0:
                l = 0
            else:
                dl = np.linalg.norm(p - self.cross_section[-1][0:2])
                if dl == 0:
                    continue
                l = self.cross_section[-1][2] + dl
            self.cross_section.append(np.array([p[0], p[1], l]))

    def add_next(self, upper_2d_list, lower_2d_list,
                 upper_base, lower_base, upper_next, lower_next):
        thre = 1e-5
        base_dist = np.linalg.norm(upper_base - lower_base)
        next_dist = np.linalg.norm(upper_next - lower_next)
        upper_dist = np.linalg.norm(upper_next - upper_base)
        lower_dist = np.linalg.norm(lower_next - lower_base)
        diagonal_dist = np.linalg.norm(upper_next - lower_base)
        if len(upper_2d_list) == 0:
            upper_2d_list.append(np.array([0, 0]))
        if len(lower_2d_list) == 0:
            lower_2d_list.append(np.array([0, -base_dist]))

        if upper_dist >= thre:
            if base_dist >= thre:
                upper_2d_list.append(
                    self.get_third_point(upper_2d_list[-1],
                                         lower_2d_list[-1],
                                         upper_dist, diagonal_dist))
            else:
                upper_2d_list.append(np.array([upper_dist, 0]))
        if lower_dist >= thre:
            if diagonal_dist >= thre:
                if next_dist >= thre:
                    lower_2d_list.append(
                        self.get_third_point(upper_2d_list[-1],
                                             lower_2d_list[-1],
                                             next_dist, lower_dist))
            else:
                lower_2d_list.append(np.array([0, -next_dist]))

    def expand(self, step = 2.0 * math.pi / 100, start=0.0, end=1.0):
        upper_2d_list = [];
        lower_2d_list = [];

        theta_max = (2 * math.pi *
                     (1.0 * self.cross_section[-1][2] / self.width + 1))
        for i in np.arange(theta_max * start, theta_max * end, step):
            upper_base = self.get_point_3d(i - 2 * math.pi)
            lower_base = self.get_point_3d(i)
            upper_next = self.get_point_3d(i - 2 * math.pi + step)
            lower_next = self.get_point_3d(i + step)
            self.add_next(upper_2d_list, lower_2d_list,
                          upper_base, lower_base, upper_next, lower_next)
        return upper_2d_list + lower_2d_list[::-1]

    def open_svg(self, filename):
        self.dwg = svgwrite.Drawing(filename, size=('210mm', '297mm'),
                                    viewBox=('0 0 210 297'))


    def draw_path(self, points, loop = True):
        d = [(['M'] if i == 0 else ['L']) + list(l)
             for i, l in enumerate(points)]
        if loop:
            d.append('z')
        self.dwg.add(self.dwg.path(d, stroke = 'black', fill = 'none'))
        self.dwg.save()

#!/usr/bin/python
# -*- coding: utf-8 -*-

import svgwrite
import numpy as np
import math

class Lathe:
    def __init__(self, filename, step = 2.0 * math.pi / 100):
        self.set_step(step)
        self.dwg = svgwrite.Drawing(filename, size=('210mm', '297mm'),
                                    viewBox=('0 0 210 297'))

    def set_step(self, step):
        self.step = step

    def spiral(self, cross_section_points, width, split = []):
        cross_model = self.__get_cross_model(cross_section_points)
        split_start_list = [0.0] + split
        split_end_list = split + [1.0]
        for start, end in zip(split_start_list, split_end_list):
            points = self.__expand_spiral(cross_model, width, start, end)
            self.__draw_path(points)

    def cone(self, bottom_radius, top_radius, height, split = []):
        split_start_list = [0.0] + split
        split_end_list = split + [1.0]
        for start, end in zip(split_start_list, split_end_list):
            points = self.__expand_cone(bottom_radius, top_radius, height, start, end)
            self.__draw_path(points)

    def __expand_spiral(self, cross_model, width, start = 0.0, end = 1.0):
        upper_2d_list = [];
        lower_2d_list = [];
        theta_max = 2 * math.pi * (1.0 * cross_model[-1][2] / width + 1)
        for i in np.arange(theta_max * start, theta_max * end, self.step):
            upper_base = self.__get_point_3d(i - 2 * math.pi, cross_model, width)
            lower_base = self.__get_point_3d(i, cross_model, width)
            upper_next = self.__get_point_3d(i - 2 * math.pi + self.step, cross_model, width)
            lower_next = self.__get_point_3d(i + self.step, cross_model, width)
            self.__add_next(upper_2d_list, lower_2d_list,
                            upper_base, lower_base, upper_next, lower_next)
        return upper_2d_list + lower_2d_list[::-1]

    def __expand_cone(self, bottom_radius, top_radius, height, start = 0.0, end = 1.0):
        upper_2d_list = [];
        lower_2d_list = [];
        theta_max = 2 * math.pi
        for i in np.arange(theta_max * start, theta_max * end, self.step):
            upper_base = np.array([top_radius * math.cos(i),
                                   top_radius * math.sin(i),
                                   height])
            upper_next = np.array([top_radius * math.cos(i + self.step),
                                   top_radius * math.sin(i + self.step),
                                   height])
            lower_base = np.array([bottom_radius * math.cos(i),
                                   bottom_radius * math.sin(i),
                                   0])
            lower_next = np.array([bottom_radius * math.cos(i + self.step),
                                   bottom_radius * math.sin(i + self.step),
                                   0])
            self.__add_next(upper_2d_list, lower_2d_list,
                            upper_base, lower_base,
                            upper_next, lower_next)
        return upper_2d_list + lower_2d_list[::-1]


    def __get_third_point(self, p1, p2, l13, l23, direction=1):
        vec12 = np.array(p2) - np.array(p1)
        l12 = np.linalg.norm(vec12)
        cos = (l13 ** 2 + l12 ** 2 - l23 ** 2) / (2.0 * l13 * l12)
        theta = math.acos(cos) * np.sign(direction)
        vec13 = np.dot(self.__rot_matrix(theta), vec12 / l12) * l13
        return p1 + vec13

    def __rot_matrix(self, rad):
        return np.array([[math.cos(rad), -math.sin(rad)],
                         [math.sin(rad), math.cos(rad)]]);

    def __inner_divide(self, p1, p2, ratio1, ratio2):
        return 1.0 * (p1 * ratio2 + p2 * ratio1) / (ratio1 + ratio2)

    def __get_point_2d(self, theta, cross_model, width):
        l = width * theta / (2.0 * math.pi)
        if l <= 0:
            return cross_model[0][0:2]
        elif l >= cross_model[-1][2]:
            return cross_model[-1][0:2]

        for i in range(len(cross_model) - 1):
            if l == cross_model[i][2]:
                return cross_model[i][0:2]
            elif cross_model[i][2] < l and l < cross_model[i + 1][2]:
                return self.__inner_divide(cross_model[i][0:2],
                                           cross_model[i + 1][0:2],
                                           l - cross_model[i][2],
                                           cross_model[i + 1][2] - l)

    def __get_point_3d(self, theta, cross_model, width):
        point_2d = self.__get_point_2d(theta, cross_model, width)
        return np.array([point_2d[0] * math.cos(theta),
                         point_2d[0] * math.sin(theta),
                         point_2d[1]])

    def __get_cross_model(self, points):
        cross_model = []
        for p in points:
            if len(cross_model) == 0:
                l = 0
            else:
                dl = np.linalg.norm(p - cross_model[-1][0:2])
                if dl == 0:
                    continue
                l = cross_model[-1][2] + dl
            cross_model.append(np.array([p[0], p[1], l]))
        return cross_model

    def __add_next(self, upper_2d_list, lower_2d_list,
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
                    self.__get_third_point(upper_2d_list[-1], lower_2d_list[-1],
                                           upper_dist, diagonal_dist))
            else:
                upper_2d_list.append(np.array([upper_dist, 0]))
        if lower_dist >= thre and next_dist >= thre:
            if diagonal_dist >= thre:
                lower_2d_list.append(
                    self.__get_third_point(upper_2d_list[-1], lower_2d_list[-1],
                                           next_dist, lower_dist))
            else:
                lower_2d_list.append(np.array([0, -next_dist]))

    def __draw_path(self, points, loop = True):
        d = [(['M'] if i == 0 else ['L']) + list(l)
             for i, l in enumerate(points)]
        if loop:
            d.append('z')
        self.dwg.add(self.dwg.path(d, stroke = 'black', fill = 'none'))
        self.dwg.save()

# -*- coding: utf-8 -*-
#!/usr/bin/python

import svgwrite
import numpy as np
import math

def get_third_point(p1, p2, l13, l23, direction=1):
    vec12 = np.array(p2) - np.array(p1)
    l12 = np.linalg.norm(vec12)
    cos = (l13 ** 2 + l12 ** 2 - l23 ** 2) / (2.0 * l13 * l12)
    theta = math.acos(cos) * np.sign(direction)
    vec13 = np.dot(rot_matrix(theta), vec12 / l12) * l13
    return p1 + vec13

def rot_matrix(rad):
    return np.array([[math.cos(rad), -math.sin(rad)],
                     [math.sin(rad), math.cos(rad)]]);

def get_point_3d(theta, n, r=1.0):
    phi = theta / (2.0 * n)
    return r * np.array([math.sin(phi) * math.cos(theta),
                         math.sin(phi) * math.sin(theta),
                         math.cos(phi)])

def expand_sphere(r, n, divide=100):
    #divide: 1周あたりの分割数
    #最初の1周は始点から結ぶ
    #最後の1周は終点まで結ぶ

    upper_2d_list = [];
    lower_2d_list = [];
    dtheta = 2.0 * math.pi / divide

    for i in range(1, divide):
        theta = 2.0 * math.pi * i / divide
        upper_base = get_point_3d(0, n, r)
        lower_base = get_point_3d(theta, n, r)
        lower_next = get_point_3d(theta + dtheta, n, r)
        lower_dist = np.linalg.norm(lower_next - lower_base)
        base_dist = np.linalg.norm(upper_base - lower_base)
        next_dist = np.linalg.norm(upper_base - lower_next)
        if len(upper_2d_list) == 0:
            upper_2d_list.append(np.array([0, 0]))
        if len(lower_2d_list) == 0:
            lower_2d_list.append(np.array([0, -base_dist]))
        lower_2d_list.append(get_third_point(upper_2d_list[-1],
                                             lower_2d_list[-1],
                                             next_dist,
                                             lower_dist))

    for i in range(divide * (n - 1)):
        theta = 2.0 * math.pi * i / divide
        upper_base = get_point_3d(theta, n, r)
        lower_base = get_point_3d(theta + 2 * math.pi, n, r)
        upper_next = get_point_3d(theta + dtheta, n, r)
        lower_next = get_point_3d(theta + dtheta + 2 * math.pi, n, r)
        base_dist = np.linalg.norm(upper_base - lower_base)
        next_dist = np.linalg.norm(upper_next - lower_next)
        upper_dist = np.linalg.norm(upper_next - upper_base)
        lower_dist = np.linalg.norm(lower_next - lower_base)
        diagonal_dist = np.linalg.norm(upper_next - lower_base)
        if len(upper_2d_list) == 0:
            upper_2d_list.append(np.array([0, 0]))
        if len(lower_2d_list) == 0:
            lower_2d_list.append(np.array([0, -base_dist]))
        upper_2d_list.append(get_third_point(upper_2d_list[-1],
                                             lower_2d_list[-1],
                                             upper_dist,
                                             diagonal_dist))
        lower_2d_list.append(get_third_point(upper_2d_list[-1],
                                             lower_2d_list[-1],
                                             next_dist,
                                             lower_dist))

    for i in range(divide):
        theta = 2.0 * math.pi * ((n - 1) + 1.0 * i / divide)
        upper_base = get_point_3d(theta, n, r)
        lower_base = get_point_3d(2 * math.pi * n, n, r)
        upper_next = get_point_3d(theta + dtheta, n, r)
        upper_dist = np.linalg.norm(upper_next - upper_base)
        base_dist = np.linalg.norm(upper_base - lower_base)
        next_dist = np.linalg.norm(upper_next - lower_base)
        if len(upper_2d_list) == 0:
            upper_2d_list.append(np.array([0, 0]))
        if len(lower_2d_list) == 0:
            lower_2d_list.append(np.array([0, -base_dist]))
        upper_2d_list.append(get_third_point(upper_2d_list[-1],
                                             lower_2d_list[-1],
                                             upper_dist,
                                             next_dist))

    return [upper_2d_list, lower_2d_list]

def write_svg(points, filename, close_first=True, close_last=True):
    dwg = svgwrite.Drawing(filename, size=('210mm', '297mm'), viewBox=('0 0 210 297'))
    draw_path(dwg, points[0])
    draw_path(dwg, points[1])
    if close_first:
        draw_path(dwg, [points[0][0], points[1][0]])
    if close_last:
        draw_path(dwg, [points[0][-1], points[1][-1]])
    dwg.save()


def draw_path(dwg, points):
    d = [(['M'] if i == 0 else ['L']) + list(l)
         for i, l in enumerate(points)]
    dwg.add(dwg.path(d, stroke = 'black', fill = 'none'))

if __name__ == '__main__':
    point_list = expand_sphere(20, 8, 100)
    write_svg(point_list, "sphere_tmp.svg")

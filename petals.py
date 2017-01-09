from random import choice, random, randrange
from functools import reduce

import svgwrite as svg
import time
import numpy as np
from itertools import product
from copy import copy
from random import random
from math import acos, sqrt, pi, cos, sin
import shapely.geometry as geom
import shapely.affinity as aff
import bezier as bez
from copy import deepcopy


class Petal(dict):
    DEFAULT_PARMS = {
        'length': 0, # distance from base to tip
        'width': 0,  # width at base
        'lft_bot' : 0, # controls the fatness at the bottom left
        'lft_top' : 0, # controls the pointiness at the top left
        'rgt_top' : 0, # controls the pointiness at the top right
        'rgt_bot' : 0, # controls the fatness at the bottom right
        }
    LIMIT = 6.

    def __init__(self, length=0, width=0):
        #super().__init__(self.DEFAULT_PARMS)
        super().__init__()
        self['length'] = length
        self['width'] = width
        self.cache = None
        self.points = []

    def __repr__(self):
        res = ''
        for k in self:
            res += '%s\t\t%s\n'%(k, self[k])
        return res

    def check(self):
        return self['lft_bot'] < self['lft_top'] < self['rgt_top'] < self['rgt_bot']

    def _limit_(self):
        '''Do not allow taper control points to cross. 
        The right control point must always be on the right or the line will self intersect
        '''
        tmp = [self['lft_bot'], self['lft_top'], self['rgt_top'], self['rgt_bot']]
        tmp.sort()
        self['lft_bot'], self['lft_top'], self['rgt_top'], self['rgt_bot'] = tmp

    def randomize(self):
        self['lft_bot'] = - self['width'] + random() * self['width'] * 2
        self['rgt_bot'] = self['lft_bot'] + random() * (self['width'] * 2 - abs(self['lft_bot']))
        self['lft_top'] = - self['width'] + random() * self['width'] * 2
        self['rgt_top'] = self['lft_top'] + random() * (self['width'] * 2 - abs(self['lft_top'])) + 0.2
        return self

            
    def random_split(self):
        p1 = copy(self)
        p2 = copy(self)
        for k in self:
            if k not in ('width', 'length'):
                split = random()
                p1[k] *= split
                p2[k] *= 1-split
        #print(p1, '\n', p2)
        return p1,p2

    def mag(self):
        return sqrt(self.dot(self))

    def dot(self, p):
        return sum(self[k]*p[k] for k in p if k not in ('width', 'length'))

    def angle_between(self, p):
        return acos(self.dot())

    def __add__(self, p):
        pr = copy(self)
        for k in self:
            if k not in ('width', 'length'):
                pr[k] += p[k]
        return pr
    def __sub__(self, p):
        pr = copy(self)
        for k in self:
            if k not in ('width', 'length'):
                pr[k] -= p[k]
        return pr
    def __mul__(self, f):
        pr = copy(self)
        for k in self:
            if k not in ('width', 'length'):
                pr[k] *= f
        return pr
    def __truediv__(self, f):
        pr = copy(self)
        for k in self:
            if k not in ('width', 'length'):
                pr[k] /= f
        return pr
    
    def _points(self):
        return [
                (-self['width']/2., 0), # Curve start point
                # curve control point - curve starts-off pointing towards this
                (self['lft_bot'], self['length']/2.), 
                # curve control point - curve ends pointing away from this
                (self['lft_top'], self['length']/2.), 
                # end point
                (0, self['length']),
                (self['rgt_top'], self['length']/2.),
                (self['rgt_bot'], self['length']/2.),
                (self['width']/2., 0),
                ]

    def to_svg(self):
        points = self._points()
        return ['M', points[0],
                'C', points[1], points[2], points[3],
                'C', points[4], points[5], points[6],
               ]

    def to_LineString(self, use_cache=True):
        flat = 0.1
        points = self._points()

        # if we're not using the cache or it hasn't been created yet or it's
        # out of date: regenerate it
        if not use_cache or self.cache is None or points != self.points:
            self.points = points
            side1 = points[:4]
            side2 = points[3:]
            self.cache = geom.LineString(side1[0:1] + [bz[3] for bz in bez.subdiv([side1], flat)] +
                                   #side2[0:1] +
                                   [bz[3] for bz in bez.subdiv([side2], 0.1)])

            p1 = self.cache.coords[0]
#            for p2 in self.cache.coords[1:]:
#                print('d: ' + str(sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)))
#                p1 = p2

        return self.cache


class PetalExtra(Petal):
    def randomize(self):
        '''Generates a curve with very few constraints and but only allows it to pass if it doesn't
        self intersect'''
        ok = False
        while not ok:
            a = random() * 2 * pi
            d = self['width'] * random()
            self['lft_bot_x'] = d * cos(a) - self['width'] / 2
            self['lft_bot_y'] = d * sin(a)

            a = random() * 2 * pi
            d = self['width'] * random()
            self['lft_top_x'] = d * cos(a)
            self['lft_top_y'] = d * sin(a) + self['length']

            a = random() * 2 * pi
            d = self['width'] * random()
            self['rgt_bot_x'] = d * cos(a) + self['width'] / 2
            self['rgt_bot_y'] = d * sin(a)

            a = random() * 2 * pi
            d = self['width'] * random()
            self['rgt_top_x'] = d * cos(a)
            self['rgt_top_y'] = d * sin(a) + self['length']

            ok = geom.Polygon(self.to_LineString()).is_valid
            print('.', end='')
        print('')
        return self

    def _points(self):
        return [
                (-self['width']/2., 0), # Curve start point
                # curve control point - curve starts-off pointing towards this
                (self['lft_bot_x'], self['lft_bot_y']),
                # curve control point - curve ends pointing away from this
                (self['lft_top_x'], self['lft_top_y']),
                # end point
                (0, self['length']),
                (self['rgt_top_x'], self['rgt_top_y']),
                (self['rgt_bot_x'], self['rgt_bot_y']),
                (self['width']/2., 0),
                ]

    def dist(self, p):
        return (p - self).mag()

    def too_big(self):
        return \
        self['lft_bot_x'] + self['width'] / 2 > self['width'] or \
        self['lft_bot_y'] > self['width'] or \
        self['lft_top_x'] > self['width'] or \
        self['lft_top_y'] - self['length'] > self['width'] or \
        self['rgt_bot_x'] - self['width'] / 2 > self['width'] or \
        self['rgt_bot_y'] > self['width'] or \
        self['rgt_top_x'] > self['width'] or \
        self['rgt_top_y'] - self['length'] > self['width'] 

    def find_nearby(self, min_dist=5, max_dist=10):
        new = deepcopy(self)

        ok = False
        while not ok or not min_dist < self.dist(new) < max_dist or new.too_big():
            a = random() * 2 * pi
            d = max_dist * random()
            new['lft_bot_x'] = self['lft_bot_x'] + d * cos(a)
            new['lft_bot_y'] = self['lft_bot_y'] + d * sin(a)

            a = random() * 2 * pi
            d = max_dist * random()
            new['lft_top_x'] = self['lft_top_x'] + d * cos(a)
            new['lft_top_y'] = self['lft_top_y'] + d * sin(a)

            a = random() * 2 * pi
            d = max_dist * random()
            new['rgt_bot_x'] = self['rgt_bot_x'] + d * cos(a)
            new['rgt_bot_y'] = self['rgt_bot_y'] + d * sin(a)

            a = random() * 2 * pi
            d = max_dist * random()
            new['rgt_top_x'] = self['rgt_top_x'] + d * cos(a)
            new['rgt_top_y'] = self['rgt_top_y'] + d * sin(a)

            ok = geom.Polygon(new.to_LineString()).is_valid
            print('.', end='')
        print('')
        return new

def occlude_petals(petals):
    polys = [geom.Polygon(p) for p in petals]

    occluded_petals = []
    for i, p in enumerate(petals[:-1]):
        for poly in polys[i+1:]:
            try:
                p = p.difference(poly)
            except:
                print('Error')
        occluded_petals.append(p)
    occluded_petals.append(petals[-1])

    polylines = []
    for p in occluded_petals:
        if type(p) not in (geom.linestring.LineString, geom.multilinestring.MultiLineString):
            print(type(p))
            continue
        if type(p) is geom.multilinestring.MultiLineString:
            for p2 in p:
                polylines.append(p2.coords)
        else:
            polylines.append(p.coords)

    polylines = [svg.shapes.Polyline(pts) for pts in polylines]

    return polylines

def variflower(x,y, npetals, petal):
    petal_scale = 0.2**(1./npetals)
    petal_angle = 137.5
    petals = [petal]
    for i in range(int(npetals)):
        petals.append(petals[-1].find_nearby(min_dist=5, max_dist=10))
    petals = [aff.translate(
                            aff.scale(
                                      aff.rotate(p.to_LineString(), 
                                                 petal_angle*i, origin=(0,0)),
                                      petal_scale**i, petal_scale**i, origin=(0,0)), 
                            x,y)
             for i, p in enumerate(petals)]
    return occlude_petals(petals)

def geom_flower_phi(x,y, npetals, petal):
    petal_scale = 0.2**(1./npetals)
    petal_angle = 137.5
    petals = [aff.translate(
                            aff.scale(
                                      aff.rotate(petal.to_LineString(), 
                                                 petal_angle*i, origin=(0,0)),
                                      petal_scale**i, petal_scale**i, origin=(0,0)), 
                            x,y)
             for i in range(int(npetals))]
    return occlude_petals(petals)

def flower(x,y, npetals, petal):
    petal_angle = 360 / npetals 
    angle = 0
    ps = []
    for p in range(int(npetals)):
        angle += petal_angle
        path = svg.path.Path()
        path.push(petal.to_svg())
        path.rotate(angle, (x,y))
        path.translate(x,y)
        ps.append(path)
    return ps

def flower_sheet(npetals, x,y, radius, spacing=10):
    width = radius / 2

    petal = PetalExtra(length = radius / 2., width = width).randomize()
    #flower_fn = geom_flower_phi
    flower_fn = variflower

    ps = []
    for x,y in product(range(x), range(y)):
        petal = petal.find_nearby(min_dist=4, max_dist=7)
        ps += flower_fn((radius+spacing)*(x+1),
                         (radius+spacing)*(y+1),
                         npetals,
                         #PetalExtra(length = (radius - spacing) / 2., width = width).randomize())
                         #Petal(length = (radius - spacing) / 2., width = width).randomize())
                         #start + xv*x + yv*y)
                         petal)
    return ps

def draw(flower, drawing, color='black', line_width=1.):
    for petal in flower:
        petal.fill('none')
        drawing.add(petal)
        petal.stroke(color, width=line_width)

def draw_cnc(flowers, scale=1.):
    header = ['%',
            'G21 (All units in mm)',
            'G90 (All absolute moves)',
            ]
    footer = ['G00 X0.0 Y 0.0 Z0.0',
            'M2',
            '%',
            ]

    body = []
    for path in flowers:
        body.append('G01 Z15 F10000')
        first = True
        for pt in path.points:
            xy = ' X ' + format((pt[0]) * scale, '.4f') + \
                 ' Y ' + format((pt[1]) * scale, '.4f')
            if first:
                body.append('G01' + xy + ' F10000') # should be G00 but firware ignores F
                body.append('G01 Z34 F10000')
                first = False
            else:
                body.append('G01' + xy + ' F10000')

    return '\n'.join(header + body + footer)


def main():
    npetals = 10
    x,y = 10, 10
    radius = 60
    spacing = 10

    flowers = flower_sheet(npetals, x,y, radius, spacing)
    #flowers = variflower(0,0, npetals, PetalExtra(length = 200, width = 50).randomize())
    #flowers = geom_flower_phi(0,0, npetals)
    dwg = svg.Drawing('test.svg')
    draw(flowers, dwg, color='black', line_width=1.)
    #dwg.viewbox(minx=0, miny=0, 
    dwg.viewbox(minx=-300, miny=-300, 
                width=300+(radius+spacing)*(x+1), height=300+(radius+spacing)*(y+1))
    dwg.save()

    with open('test.cnc', 'w') as cnc:
        cnc.write(draw_cnc(flowers))

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)



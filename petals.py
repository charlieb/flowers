from random import choice, random, randrange
import svgwrite as svg
import time
import numpy as np
from itertools import product
from copy import copy
from random import random
from math import acos, sqrt
import shapely.geometry as geom
import shapely.affinity as aff
import bezier as bez



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
        super().__init__(self.DEFAULT_PARMS)
        self['length'] = length
        self['width'] = width
    def __repr__(self):
        res = ''
        for k in ['lft_bot', 'lft_top', 'rgt_top', 'rgt_bot']:
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
        self['rgt_bot'] = self['lft_bot'] + random() * (self['width'] * 1 - self['lft_bot'])
        self['lft_top'] = - self['width'] + random() * self['width'] * 2
        self['rgt_top'] = self['lft_top'] + random() * (self['width'] * 1 - self['lft_top']) + 0.2
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

    def to_LineString(self):
        flat = 0.1
        points = self._points()
        side1 = points[:4]
        side2 = points[3:]
        return geom.LineString(side1[0:1] + [bz[3] for bz in bez.subdiv([side1], flat)] +
                               #side2[0:1] +
                               [bz[3] for bz in bez.subdiv([side2], 0.1)])


def variflower(x,y, npetals, width, height):
    start = Petal(length = radius / 2., width = width).randomize()
    left = Petal(length = (radius - spacing) / 2., width = width).randomize()
    right = Petal(length = (radius - spacing) / 2., width = width).randomize()

    xv = left / max(x,y)
    yv = right / max(x,y)

    petal_scale = 0.2**(1./npetals)
    petal_angle = 137.5
    if petal is None:
        petal = Petal(width=100, length=200).randomize()
    petals = [aff.translate(
                            aff.scale(
                                      aff.rotate(petal.to_LineString(), 
                                                 petal_angle*i, origin=(0,0)),
                                      petal_scale**i, petal_scale**i, origin=(0,0)), 
                            x,y)
             for i in range(int(npetals))]
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

    # multilinestring.lines
    polylines = []
    for p in occluded_petals:
        if type(p) not in (geom.linestring.LineString, geom.multilinestring.MultiLineString):
            print(type(p))
            continue
        if type(p) is geom.multilinestring.MultiLineString:
            for p2 in p:
                polylines.append(svg.shapes.Polyline(p2.coords))
        else:
            polylines.append(svg.shapes.Polyline(p.coords))

    return polylines

def geom_flower_phi(x,y, npetals, petal=None):
    petal_scale = 0.2**(1./npetals)
    petal_angle = 137.5
    if petal is None:
        petal = Petal(width=100, length=200).randomize()
    petals = [aff.translate(
                            aff.scale(
                                      aff.rotate(petal.to_LineString(), 
                                                 petal_angle*i, origin=(0,0)),
                                      petal_scale**i, petal_scale**i, origin=(0,0)), 
                            x,y)
             for i in range(int(npetals))]
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

    # multilinestring.lines
    polylines = []
    for p in occluded_petals:
        if type(p) not in (geom.linestring.LineString, geom.multilinestring.MultiLineString):
            print(type(p))
            continue
        if type(p) is geom.multilinestring.MultiLineString:
            for p2 in p:
                polylines.append(svg.shapes.Polyline(p2.coords))
        else:
            polylines.append(svg.shapes.Polyline(p.coords))

    return polylines

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
    min_dist = sqrt(4*(width*2)**2) / 2

    start = Petal(length = radius / 2., width = width).randomize()
    mid = start
    while (mid - start).mag() < min_dist:
        mid = Petal(length = (radius - spacing) / 2., width = width).randomize()
    end = mid
    while (end - mid).mag() < min_dist:
        end = Petal(length = (radius - spacing) / 2., width = width).randomize()

    xv = (mid - start) / max(x,y)
    yv = (end - mid) / max(x,y)

    print(start, mid, end)

    ps = []
    for x,y in product(range(10), range(10)):
        ps += geom_flower_phi((radius+spacing)*(x+1),
                             (radius+spacing)*(y+1),
                             npetals,
                             #Petal(length = (radius - spacing) / 2., width = width*2).randomize())
                             start + xv*x + yv*y)

    return ps

def draw(flower, drawing, color='black', line_width=1.):
    for petal in flower:
        petal.fill('none')
        drawing.add(petal)
        petal.stroke(color, width=line_width)

def main():
    npetals = 10
    x,y = 10, 10
    radius = 60
    spacing = 10

    flowers = flower_sheet(npetals, x,y, radius, spacing)
    #flowers = geom_flower_phi(0,0, npetals)
    dwg = svg.Drawing('test.svg')
    draw(flowers, dwg, color='black', line_width=1.)
    #dwg.viewbox(minx=0, miny=0, 
    dwg.viewbox(minx=-300, miny=-300, 
                width=300+(radius+spacing)*(x+1), height=300+(radius+spacing)*(y+1))
    dwg.save()

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)



from math import sqrt, sin, cos, radians, pi, isnan
from random import choice, random, randrange
import numpy as np
from numba import jit, int64, float64, boolean
import svgwrite
import time
from functools import reduce

def circle_points(cx,cy,r,point_separation=None,npoints=None, close=True):
    if npoints is None:
        npoints = int(2*pi*r / point_separation) 
    elif point_separation is None:
        pass
    else:
        print("circle_points: you must either specify point_separation or npoints")
        return

    points = []
    for i in range(npoints + (1 if close else 0)): # + 1 to add a duplicate point to close the loop
        a = i * 2*pi / npoints
        points.append([cx + r*cos(a), cy + r*sin(a)])
    return points

class PetalLayer:
    def __init__(self, pistil_radius=1., petal_length=1., num_petals=6):
        self.pistil_radius = pistil_radius
        self.petal_length = petal_length
        self.num_petals = num_petals
        self.paths = []
        self.petal_centers = []

        self.calc_paths()
        self.remove_occluded()

    def calc_paths(self):
        self.petal_centers = circle_points(0.,0.,
                                    self.pistil_radius + self.petal_length / 2.,
                                    npoints=self.num_petals,
                                    close=False)
        petal_radius = self.petal_length / 2.
        self.paths = [circle_points(pc[0],pc[1], petal_radius, point_separation=2.) for pc in self.petal_centers]

    def remove_occluded(self):
        petal_radius = self.petal_length / 2.
        # petal point and center, and the petal it's overlapping.
        for ci, pc in enumerate(self.petal_centers):
            # ignore up to current path (ci+1)
            # and go round twice but make sure updates to the first instance of
            # paths are reflected in the second (shallow copy)
            for move_overlaps in self.paths[ci+1:]+self.paths[1:ci+1]:
                overlap_points = [] # contains data about all the overlapping points
                for i, p in enumerate(move_overlaps):
                    dx = p[0] - pc[0]
                    dy = p[1] - pc[1]
                    if (dx**2 + dy**2) <= petal_radius**2: # length=2*radius
                        overlap_points.append((p, (dx,dy), i))
                        
                # We can have two overlapping segments if point 0 is an overlap
                for oi, (p,d,pi) in enumerate(overlap_points):
                    if pi != oi:
                        overlap_points = overlap_points[oi:] + overlap_points[:oi]
                        break

                if len(overlap_points) >= 2:
                    # Adjust the first and last overlap points
                    for p, (dx,dy), _ in [overlap_points[0], overlap_points[-1]]:
                        dx = p[0] - pc[0]
                        dy = p[1] - pc[1]
                        dmag = sqrt(dx**2 + dy**2)
                        p[0] = pc[0] + petal_radius * dx / dmag
                        p[1] = pc[1] + petal_radius * dy / dmag
                    # Delete the rest
                    for p, _, _ in overlap_points[1:-1]:
                        move_overlaps.remove(p)

                if len(overlap_points) >= 1:
                    # rotate the original list so that the line segment that's left
                    # is continuous
                    start = move_overlaps.index(overlap_points[-1][0])
                    idx = self.paths.index(move_overlaps)
                    self.paths[idx] = move_overlaps[start:] + move_overlaps[:start]
                else: # the first time one doesn't overlap stop looking
                    break 

class Flower:
    def __init__(self, pistil_radius=1.):
        self.pistil_radius = pistil_radius
        self.petal_layers = []
        self.pistil = circle_points(0.,0., self.pistil_radius, point_separation=2.)

    def add_petal_layer(self, petal_length, num_petals):
        self.petal_layers.append(PetalLayer(self.pistil_radius, petal_length, num_petals))

    def draw(self):

        dwg = svgwrite.Drawing('test%05i.svg'%0, profile='tiny')
        line_width = 1
        minx = miny =  9999999
        maxx = maxy = -9999999
        paths = [self.pistil]
        for p in self.petal_layers:
            paths += p.paths

        cols = ['red','green','blue'] * len(paths)

        for p, col in zip(paths, cols):
            for (x,y) in p:
                minx = x if x < minx else minx
                maxx = x if x > maxx else maxx
                miny = y if y < miny else miny
                maxy = y if y > maxy else maxy

            if len(p) > 0:
              pline = svgwrite.shapes.Polyline(p, fill='none')
              dwg.add(pline)
              #svgpath.stroke('black', width=line_width)
              pline.stroke(col, width=line_width)
        dwg.viewbox(minx=minx-line_width, miny=miny-line_width, 
                    width=maxx-minx+2*line_width, height=maxy-miny+2*line_width)
        dwg.save()

class PhiFlower:
    def __init__(self, pistil_radius=1.):
        self.pistil_radius = pistil_radius
        self.petals = []
        self.angle = 0
        self.point_separation = 2.
        self.pistil = circle_points(0.,0., self.pistil_radius, self.point_separation)
        self.phi = (1 + sqrt(5)) / 2

    def add_petals(self, n, petal_radius):
        for _ in range(n):
            cx = (self.pistil_radius + petal_radius) * cos(self.angle)
            cy = (self.pistil_radius + petal_radius) * sin(self.angle)
            self.petals.append(circle_points(cx,cy, petal_radius, self.point_separation))
            self.angle += self.phi

    def draw(self):
        dwg = svgwrite.Drawing('test%05i.svg'%0, profile='tiny')
        line_width = 0.1
        minx = miny =  9999999
        maxx = maxy = -9999999

        paths = self.petals + [self.pistil]
        cols = ['red','green','blue'] * len(paths)
        cols = ['black'] * len(paths)

        for p, col in zip(paths, cols):
            for (x,y) in p:
                minx = x if x < minx else minx
                maxx = x if x > maxx else maxx
                miny = y if y < miny else miny
                maxy = y if y > maxy else maxy

            if len(p) > 0:
              pline = svgwrite.shapes.Polyline(p, fill='white')
              dwg.add(pline)
              #svgpath.stroke('black', width=line_width)
              pline.stroke(col, width=line_width)
        dwg.viewbox(minx=minx-line_width, miny=miny-line_width, 
                    width=maxx-minx+2*line_width, height=maxy-miny+2*line_width)
        dwg.save()



def main():
    #f = Flower(pistil_radius=10)
    #f.add_petal_layer(petal_length=20, num_petals=6)
#    f.add_petal_layer(petal_length=15, num_petals=15)
#    f.add_petal_layer(petal_length=10, num_petals=25)
    f = PhiFlower(10)
    for i in range(30):
        f.add_petals(5, 20 - 15*i / 30)
    f.draw()

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)


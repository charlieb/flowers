from math import sqrt, sin, cos, radians, pi, isnan
from random import choice, random, randrange
import numpy as np
from numba import jit, int64, float64, boolean
import svgwrite
import time
from functools import reduce

def circle_points(cx,cy,r,point_separation=None,npoints=None):
    if npoints is None:
        npoints = int(2*pi*r / point_separation)
    elif point_separation is None:
        pass
    else:
        print("circle_points: you must either specify point_separation or npoints")
        return

    points = []
    for i in range(npoints):
        a = i * 2*pi / npoints
        points.append([cx + r*cos(a), cy + r*sin(a)])
    return points

def path(points):
  return ((('M',) if i == 0 else ()) + tuple(p) for i,p in enumerate(points))

class Flower:
    def __init__(self, pistil_radius=1., petal_length=1., num_petals=6):
        self.pistil_radius = pistil_radius
        self.petal_length = petal_length
        self.num_petals = num_petals

    def draw(self):
        paths=[circle_points(0.,0., self.pistil_radius, point_separation=2.)]
        petal_centers = circle_points(0.,0.,
                                    self.pistil_radius + self.petal_length / 2.,
                                    npoints=self.num_petals)
        petal_radius = self.petal_length / 2.
        for pc in petal_centers:
            paths.append(circle_points(pc[0],pc[1], petal_radius, point_separation=2.))

# TODO if the move_point is within the petal move it towards it's own petal's
# center i.e. solve circle-line intersection for the vector between move's
# petal point and center, and the petal it's overlapping.
#        for i, pc in enumerate(petal_centers):
#            for j, move_overlaps in enumerate(paths[i+2:]): #ignore current path and pistil path 
#                move_center = petal_centers[i+j]
#                for p in move_overlaps:
#                    dx = p[0] - pc[0]
#                    dy = p[1] - pc[1]
#                    if (dx**2 + dy**2) <= petal_radius**2: # length=2*radius
#                        #Adjust position relative to move_center not pc
#                        new_radius = petal_radius - sqrt(dx**2 + dy**2)
#                        dx = p[0] - pc[0]
#                        dy = p[1] - pc[1]
#                        dmag = sqrt(dx**2 + dy**2)
#                        p[0] = pc[0] + petal_radius * dx / dmag
#                        p[1] = pc[1] + petal_radius * dy / dmag

        dwg = svgwrite.Drawing('test%05i.svg'%0, profile='tiny')
        line_width = 1
        minx = miny =  9999999
        maxx = maxy = -9999999
        cols = ['red','green','blue'] * len(paths)
        for p, col in zip(paths, cols):
            for (x,y) in p:
                minx = x if x < minx else minx
                maxx = x if x > maxx else maxx
                miny = y if y < miny else miny
                maxy = y if y > maxy else maxy

            svgpath = svgwrite.path.Path(path(p), fill='none')
            svgpath.push('Z')
            dwg.add(svgpath)
            #svgpath.stroke('black', width=line_width)
            svgpath.stroke(col, width=line_width)
        dwg.viewbox(minx=minx-line_width, miny=miny-line_width, 
                    width=maxx-minx+2*line_width, height=maxy-miny+2*line_width)
        dwg.save()


def draw(starting_points, npoints, points, connections, frame):
    dwg = svgwrite.Drawing('test%05i.svg'%frame, profile='tiny')
    minx = miny =  9999999
    maxx = maxy = -9999999
    line_width = 1
    for i in range(npoints):
        minx = points[i][0] if points[i][0] < minx else minx
        maxx = points[i][0] if points[i][0] > maxx else maxx
        miny = points[i][1] if points[i][1] < miny else miny
        maxy = points[i][1] if points[i][1] > maxy else maxy
    dwg.viewbox(minx=minx-line_width, miny=miny-line_width, 
                width=maxx-minx+2*line_width, height=maxy-miny+2*line_width)
    # reverse starting points so that if concentric the largest one
    # will be first so that when they're drawn with fill they'll all be 
    # visible
    rev_starts = starting_points.copy()
    rev_starts.reverse()
    #fills = ['green', 'blue', 'red'] * len(starting_points) # far too long but meh
    fills = ['none'] * len(starting_points)
    for start, fill in zip(rev_starts, fills):
        svgpath = svgwrite.path.Path(path(start, points, connections), fill=fill)
        svgpath.push('Z')
        svgpath.stroke('black', width=1)
        dwg.add(svgpath)
    dwg.save()

def main():
    f = Flower(pistil_radius=10, petal_length=20, num_petals=10)
    f.draw()

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)


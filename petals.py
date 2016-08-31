from random import choice, random, randrange
from numba import jit
import svgwrite
import time

def draw(paths, viewbox):
    dwg = svgwrite.Drawing('test%05i.svg'%0, profile='tiny')
    line_width = 1.

    cols = ['red','green','blue'] * len(paths)
    cols = ['black'] * len(paths)
    fills = ['red', 'green', 'blue'] * len(paths)
    fills = ['none'] * len(paths)
    for p, col, fill in zip(paths, cols, fills):
        p.fill(fill)
        dwg.add(p)
        p.stroke(col, width=line_width)
    dwg.viewbox(*viewbox)
    dwg.save()

petal_params = {
        'length': 0, # distance from base to tip
        'width': 0,  # width at base
        'taper' : 1, # how quickly the petal tapers to it's point, 1 gives a straight line
        'fatness': 1 # controls the waist of the petal, 1 gives a straight waist
        }

@jit
def petal(x,y, angle, length, width, taper=1., fatness=1.):
    side1 = ['M', (-width/2., 0), 'C', (fatness*(-width/2.), length/2.), (taper*(-width/2.), length/2.), (0, length)]
    side2 = ['M',  (width/2., 0), 'C', (fatness*( width/2.), length/2.), (taper*( width/2.), length/2.), (0, length)]

    path = svgwrite.path.Path()
    path.push(side1)
    path.push(side2)
    path.rotate(angle, (x,y))
    path.translate(x,y)
    return path

def main():
    np = 10
    ps = []
    for x in range(10):
        for y in range(10):
            ps += [petal(70*(x+1), 70*(y+1), a*360/np, 30, 20, x/5., y/5) for a in range(np)]

    draw(ps, (0,0,800,800))

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)


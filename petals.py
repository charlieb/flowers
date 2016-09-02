from random import choice, random, randrange
import svgwrite
import time
import numpy as np

def draw(flower, drawing, color='black', line_width=1.):
    for petal in flower:
        petal.fill('none')
        drawing.add(petal)
        petal.stroke(color, width=line_width)

petal_params = {
        'length': 0, # distance from base to tip
        'width': 0,  # width at base
        'taper' : 1, # how quickly the petal tapers to it's point, 1 gives a straight line
        'fatness': 1 # controls the waist of the petal, 1 gives a straight waist
        }

def petal(x,y, angle, length, width, taper=1., fatness=1.):
    side1 = ['M', (-width/2., 0), 'C', (fatness*(-width/2.), length/2.), (taper*(-width/2.), length/2.), (0, length)]
    side2 = ['M',  (width/2., 0), 'C', (fatness*( width/2.), length/2.), (taper*( width/2.), length/2.), (0, length)]

    path = svgwrite.path.Path()
    path.push(side1)
    path.push(side2)
    path.rotate(angle, (x,y))
    path.translate(x,y)
    return path

def pack(x,y, npetals, petal_length, petal_width, petal_taper=1., petal_fatness=1., petal_angle=None):
    if petal_angle is None: # if not specified make an even distribution
        petal_angle = 360 / npetals 
    return np.array([x,y, npetals, petal_length, petal_width, petal_taper, petal_fatness, petal_angle])

def unpack(array):
    return {
            'x' : array[0],
            'y' : array[1],
            'npetals' : array[2],
            'petal_length' : array[3],
            'petal_width' : array[4],
            'petal_taper' : array[5],
            'petal_fatness' : array[6],
            'petal_angle' : array[7],
            }

def unpack_to_svg(array):
    data = unpack(array)
    return flower(**data)

def flower(x,y, npetals, petal_length, petal_width, petal_taper=1., petal_fatness=1., petal_angle=None):
    if petal_angle is None: # if not specified make an even distribution
        petal_angle = 360 / npetals 
    return [petal(x,y, petal_angle*i, petal_length, petal_width, petal_taper, petal_fatness)
            for i in range(int(npetals))]

def main():
    npetals = 10
    flowers = np.zeros((100,8))
    for x in range(10):
        for y in range(10):
            flowers[x+10*y] = pack(70*(x+1), 70*(y+1), npetals, 30, 20, x/5., y/5)

    ps = []
    for f in flowers:
        ps += unpack_to_svg(f)
#    for x in range(10):
#        for y in range(10):
#            ps += flower(70*(x+1), 70*(y+1), npetals, 30, 20, x/5., y/5)

    draw(ps, (0,0,800,800))

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Elapsed:", t1-t0)


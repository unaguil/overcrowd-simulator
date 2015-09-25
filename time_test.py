import shapely.affinity as affinity
import shapely.geometry as geometry
import random
import time
import numpy
import cProfile
import pstats

def __create_circle(position, radius):
    p = geometry.point.Point(position)
    c = p.buffer(radius)
    return c

def create_circles():
    circles = []
    for i in range(CIRCLES):
        position = (
            random.random() * DIMENSIONS[0],
            random.random() * DIMENSIONS[1]
        )

        radius = random.random() * (RADIUS[1] - RADIUS[0]) + RADIUS[0]

        circle = __create_circle(position, radius)
        circles.append(circle)

    return circles

def create_boxes():
    box = geometry.box(0, 0, CELL_SIZE[0], CELL_SIZE[1])

    boxes = []
    for row in range(CELLS[0]):
        for column in range(CELLS[1]):
            #new_box = affinity.translate(box, row * CELL_SIZE[0], column * CELL_SIZE[1])
            new_box = geometry.box(0, 0, CELL_SIZE[0], CELL_SIZE[1])
            boxes.append(new_box)

    return boxes

def profile():
    check_times = []
    checked_intersections = 0
    for i in range(UPDATES):
        circles = create_circles()
        for circle in circles:
            for box in boxes:
                start = time.time()
                checked_intersections += 1
                if circle.intersects(box):
                    common = circle.intersection(box)
                diff = time.time() - start
                check_times.append(diff)

    print ("Checked intersections %d" % checked_intersections)

if __name__ == '__main__':
    CELLS = (128, 128)
    DIMENSIONS = (100, 100)
    CELL_SIZE = (DIMENSIONS[0] / float(CELLS[0]), DIMENSIONS[1] / float(CELLS[1]))
    CIRCLES = 20
    RADIUS = (0.0, 3.0)
    UPDATES = 10

    area = DIMENSIONS[0] * DIMENSIONS[1]
    cell_area = CELL_SIZE[0] * CELL_SIZE[1]

    print("Avg. density %.5f devices/m^2" % (CIRCLES / float(area)))
    print("Cell area: %.3f m^2" % cell_area)

    start = time.time()
    boxes = create_boxes()
    print("Box creation time %.4f" % (time.time() - start))

    cProfile.run('profile()', 'stats')

    p = pstats.Stats('stats')
    p.strip_dirs().sort_stats('cumulative').print_stats()

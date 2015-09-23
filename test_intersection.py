import shapely.geometry as geometry
from shapely.geometry.point import Point

def create_circle(x, y, radius):
    p = Point(x, y)
    c = p.buffer(radius)
    return c

circle1 = create_circle(0, 0, 1)
box1 = geometry.box(0, 0, 1, 1)

common = circle1.intersection(box1)
print "Circle 1 area: %.2f" % circle1.area
print "Box 1 area: %.2f" % box1.area

if common.is_empty:
    print "No intersection"
else:
    print "Intersection area: %.2f" % common.area

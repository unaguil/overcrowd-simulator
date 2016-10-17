import shapely.geometry as geometry
import numpy
from rtree import index
import os

class Cell(object):

    def __init__(self, position, cell_dimensions):
        self.position = position

        self.box = geometry.box(
            self.position[0],
            self.position[1],
            self.position[0] + cell_dimensions[0],
            self.position[1] + cell_dimensions[1]
        )

class GridManager(object):

    RTREE_PATH = '/tmp/rtree'
    RTREE_FILES = ['.idx', '.dat']

    def __init__(self, spark_context, dimensions, n_cells=(12, 12)):
        self.sc = spark_context
        self.dimensions = dimensions
        self.n_cells = n_cells

        self.area = float(self.dimensions[0] * self.dimensions[1])

        self.cell_dimensions = (
            dimensions[0] / float(n_cells[0]),
            dimensions[1] / float(n_cells[1])
        )

        self.cell_area = self.cell_dimensions[0] * self.cell_dimensions[1]
        self.__create_cells()

    def remove_rtree_files(self):
        for extension in GridManager.RTREE_FILES:
            if os.path.isfile(GridManager.RTREE_PATH + extension):
                os.remove(GridManager.RTREE_PATH + extension)

    def __create_cells(self):
        self.remove_rtree_files()

        p = index.Property()
        p.overwrite = True
        self.idx = index.Index('/tmp/rtree', properties=p)

        self.cells = []
        for row_index in range(self.n_cells[0]):
            row = []
            for column_index in range(self.n_cells[1]):
                position = (
                    row_index * self.cell_dimensions[0],
                    column_index * self.cell_dimensions[1]
                )

                cell = Cell(position, self.cell_dimensions)
                pos = row_index * self.n_cells[0] + column_index
                self.idx.insert(pos, cell.box.bounds)
                row.append(cell)

            self.cells.append(row)
        self.idx.close()

    def update(self, devices):

        def update_device(device):
            circle = create_circle(device)
            idx = index.Index('/tmp/rtree')
            cell_indices = idx.intersection(circle.bounds)

            total_common = 0
            common_cells = []

            for pos in cell_indices:
                cell_index = (pos // columnsBroadcast.value,  pos % columnsBroadcast.value)
                cell = cellsBroadcast.value[cell_index[0]][cell_index[1]]
                common = cell.box.intersection(circle)
                common_cells.append((cell_index, common.area))
                total_common += common.area

            missing = (circle.area - total_common) / circle.area
            current_matrix = numpy.zeros((rowsBroadcast.value, columnsBroadcast.value))

            for cell_index, common_area in common_cells:
                cell_ratio = common_area / float(total_common)
                current_matrix[cell_index[0]][cell_index[1]] += common_area / circle.area + cell_ratio * missing

            return ('matrix', current_matrix)

        def sum_matrix(accum, n):
            return accum + n

        self.avg_density = len(devices) / self.area

        columnsBroadcast = self.sc.broadcast(self.columns)
        rowsBroadcast = self.sc.broadcast(self.rows)
        cellsBroadcast = self.sc.broadcast(self.cells)

        devicesRDD = self.sc.parallelize(devices)
        devicesRDD = devicesRDD.map(update_device)

        sumRDD = devicesRDD.reduceByKey(sum_matrix)

        self.occupation_matrix = sumRDD.collect()[0][1]
        self.density_matrix = self.occupation_matrix / self.cell_area

    def __get_row_column(self, num):
        if num == 0:
            return (0, 0)
        elif num == 1:
            return (0, 1)
        elif num == 2:
            return (1, 0)
        elif num == 3:
            return (1, 1)

    def __adjust_row_column(self, current, index, factor):
        adjusted = (
            (current[0] * factor + index[0][0], current[1] * factor + index[0][1]),
            index[1]
        )

        return adjusted

    def __total_cells_area(self, cells):
        total_area = 0.0
        for cell in cells:
            total_area += cell[1]

        return total_area

    def __getitem__(self, index):
        return self.cells[index[0]][index[1]]

    def __setitem__(self, index, value):
        self.cells[index[0]][index[1]] = value

    @property
    def rows(self):
        return len(self.cells)

    @property
    def columns(self):
        return len(self.cells[0])

    @property
    def shape(self):
        return (self.rows, self.columns)

    def check_density(self, f):
        indices = []
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                if f(self.density_matrix[row_index, column_index]):
                    indices.append((row_index, column_index))

        return indices

    def check_occupation(self, f):
        indices = []
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                if f(self.occupation_matrix[row_index, column_index]):
                    indices.append((row_index, column_index))

        return indices

def create_circle(device):
    p = geometry.point.Point(device.position)
    c = p.buffer(device.accuracy)
    return c

import shapely.geometry as geometry
from io import StringIO
import numpy
import time
import math

def timeit(method):

    def timed(*args, **kw):
        start = time.time()
        result = method(*args, **kw)
        end = time.time()

        print '\'%s\' %.2f sec' % (method.__name__, end - start)
        return result

    return timed

class Cell(object):

    def __init__(self, manager, position):
        self.manager = manager
        self.position = position

        self.occupation = 0.0

        coords = (
            self.position[0],
            self.position[1],
            self.position[0] + self.manager.cell_dimensions[0],
            self.position[1] + self.manager.cell_dimensions[1]
        )

        self.box = geometry.box(*coords)

    @property
    def density(self):
        return self.occupation / self.manager.cell_area

class InvalidCellDivisionException(Exception):

    def __init__(self, message):
        super(InvalidCellDivisionException, self).__init__(message)

class GridManager(object):

    def __init__(self, dimensions, n_cells=(12, 12)):
        self.dimensions = dimensions
        self.n_cells = n_cells

        if not self.__is_pow(n_cells):
            raise InvalidCellDivisionException('Error. (%d, %d) is not a power of two.' % n_cells)
        elif not self.__is_symmetric(n_cells):
            raise InvalidCellDivisionException('Error. (%d, %d) is not symmetric.' % n_cells)

        self.area = float(self.dimensions[0] * self.dimensions[1])

        self.max_deep = int(math.log(self.n_cells[0], 2)) - 1

        self.cell_dimensions = (
            dimensions[0] / float(n_cells[0]),
            dimensions[1] / float(n_cells[1])
        )

        self.cell_area = self.cell_dimensions[0] * self.cell_dimensions[1]

        self.__clear_cells()

    def __is_pow(self, index):
        return math.log(index[0], 2).is_integer() and math.log(index[1], 2).is_integer()

    def __is_symmetric(self, index):
        return index[0] == index[1]

    def __clear_cells(self):
        self.cells = []
        for row_index in range(self.n_cells[0]):
            row = []
            for column_index in range(self.n_cells[1]):
                position = (
                    row_index * self.cell_dimensions[0],
                    column_index * self.cell_dimensions[1]
                )
                row.append(Cell(self, position))
            self.cells.append(row)

    @timeit
    def update(self, devices):
        self.__clear_cells()

        self.avg_density = len(devices) / self.area

        for device in devices:
            circle = self.__create_circle(device)
            common_cells = self.__tree_intersection(circle, self.max_deep, self.dimensions)
            total_common = self.__total_cells_area(common_cells)

            missing = (circle.area - total_common) / circle.area
            for cell_index, common_area in common_cells:
                cell_ratio = common_area / float(total_common)
                self[cell_index].occupation += common_area / circle.area + cell_ratio * missing

    def __split(self, dimensions, origin=(0, 0)):
        cell_size = dimensions[0] / 2.0, dimensions[1] / 2.0

        cells = (
            (origin[0], origin[1], origin[0] + cell_size[0], origin[1] + cell_size[1]),
            (origin[0] + cell_size[0], origin[1], origin[0] + cell_size[0] * 2, origin[1] + cell_size[1]),
            (origin[0], origin[1] + cell_size[1], origin[0] + cell_size[0], origin[1] + cell_size[1] * 2),
            (origin[0] + cell_size[1], origin[1] + cell_size[1], origin[0] + cell_size[0] * 2, origin[1] + cell_size[1] * 2)
        )

        return cells, cell_size

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

    def __tree_intersection(self, shape, max_deep, dimensions, origin=(0, 0), n=0):
        cells, cell_size = self.__split(dimensions, origin)

        common_cells = []
        for index, cell in enumerate(cells):
            box = geometry.box(*cell)
            common =  box.intersection(shape)
            if not common.is_empty:
                current_index = self.__get_row_column(index)
                if n < max_deep:
                    cell_origin = (cell[0], cell[1])
                    for common_cell in self.__tree_intersection(shape, max_deep, cell_size, cell_origin, n + 1):
                        factor = max_deep - n
                        common_cell = self.__adjust_row_column(current_index, common_cell, 2**factor)
                        common_cells.append(common_cell)
                else:
                    common_cells.append((current_index, common.area))

        return common_cells

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
    def occupation_matrix(self):
        matrix = []
        for row_index in range(self.rows):
            row = []
            for column_index in range(self.columns):
                row.append(self[row_index, column_index].occupation)
            matrix.append(row)

        return numpy.array(matrix)

    @property
    def density_matrix(self):
        return self.occupation_matrix / self.cell_area

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
                if f(self[row_index, column_index].density):
                    indices.append((row_index, column_index))

        return indices

    def check_occupation(self, f):
        indices = []
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                if f(self[row_index, column_index].occupation):
                    indices.append((row_index, column_index))

        return indices

    def __create_circle(self, device):
        p = geometry.point.Point(device.position)
        c = p.buffer(device.accuracy)
        return c

import shapely.geometry as geometry
from io import StringIO
import numpy

class Cell(object):

    def __init__(self, manager, position):
        self.manager = manager
        self.position = position

        self.occupation = 0.0

    @property
    def density(self):
        return self.occupation / self.manager.cell_area

    @property
    def box(self):
        coords = (
            self.position[0],
            self.position[1],
            self.position[0] + self.manager.cell_dimensions[0],
            self.position[1] + self.manager.cell_dimensions[1]
        )

        return coords

class GridManager(object):

    def __init__(self, dimensions, n_cells=(10, 10)):
        self.dimensions = dimensions
        self.n_cells = n_cells
        self.area = float(self.dimensions[0] * self.dimensions[1])

        self.cell_dimensions = (
            dimensions[0] / float(n_cells[0]),
            dimensions[1] / float(n_cells[1])
        )

        self.cell_area = self.cell_dimensions[0] * self.cell_dimensions[1]

        self.__clear_cells()

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

    def update(self, devices):
        self.__clear_cells()

        self.avg_density = len(devices) / self.area

        for device in devices:
            circle = self.__create_circle(device)

            common_cells = []
            total_common = 0.0
            for row_index in range(self.rows):
                for column_index in range(self.columns):
                    cell = self[row_index, column_index]
                    box = self.__create_box(cell.box)
                    common = circle.intersection(box)

                    if not common.is_empty:
                        common_cells.append((cell, common.area ))
                        total_common += common.area

            missing = (circle.area - total_common) / circle.area
            for cell, common_area in common_cells:
                cell_ratio = common_area / float(total_common)
                cell.occupation += common_area / circle.area + cell_ratio * missing

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

    def __create_box(self, box_coords):
        box = geometry.box(*box_coords)
        return box

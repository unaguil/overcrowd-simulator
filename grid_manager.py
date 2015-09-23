
class Cell(object):

    def __init__(self):
        self.density = 0.0

class GridManager(object):

    def __init__(self, dimensions, n_cells=(10, 10)):
        self.dimensions = dimensions
        self.n_cells = n_cells

        self.cell_dimensions = (
            dimensions[0] / float(n_cells[0]),
            dimensions[1] / float(n_cells[1])
        )

        self.cells = []
        for row_index in range(self.n_cells[0]):
            row = []
            for column_index in range(self.n_cells[1]):
                row.append(Cell())
            self.cells.append(row)

    def update(devices):
        pass

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

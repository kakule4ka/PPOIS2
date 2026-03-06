import pickle
import os
from garden.garden_plot import GardenPlot


class Storage:
    def __init__(self, filename: str = "garden_state.pkl"):
        self.filename = filename

    def save(self, plot: GardenPlot):
        with open(self.filename, 'wb') as f:
            pickle.dump(plot, f)

    def load(self) -> GardenPlot:
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                return pickle.load(f)
        return GardenPlot()
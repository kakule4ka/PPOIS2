import unittest
import os
from garden.storage import Storage
from garden.garden_plot import GardenPlot

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_filename = "test_garden_state.pkl"
        self.storage = Storage(self.test_filename)
        self.plot = GardenPlot()

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_save_and_load(self):
        self.plot.plant_seed("Тыква")
        self.plot.water_garden()
        self.plot.develop_recreation_zone()
        
        self.storage.save(self.plot)
        loaded_plot = self.storage.load()

        self.assertEqual(len(loaded_plot.plants), 1)
        self.assertEqual(loaded_plot.plants[0].species, "Тыква")
        self.assertTrue(loaded_plot.soil.is_hydrated)
        self.assertEqual(loaded_plot.recreation_zone.build_progress, 25)
        self.assertEqual(loaded_plot.tools[0].durability, 90)
        self.assertEqual(loaded_plot.tools[2].durability, 75)

    def test_load_nonexistent_file(self):
        new_plot = self.storage.load()
        self.assertIsInstance(new_plot, GardenPlot)
        self.assertEqual(len(new_plot.plants), 0)
        self.assertEqual(new_plot.watering_system.current_water, 200)
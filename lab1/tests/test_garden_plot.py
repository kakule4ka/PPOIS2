import unittest
from garden.garden_plot import GardenPlot
from garden.entities import PlantState

class TestGardenPlot(unittest.TestCase):
    def setUp(self):
        self.plot = GardenPlot()

    def test_plant_seed_consumes_tool(self):
        self.plot.plant_seed("Томат")
        self.assertEqual(len(self.plot.plants), 1)
        self.assertEqual(self.plot.tools[0].durability, 90)

    def test_water_garden_consumes_correct_water(self):
        self.plot.plant_seed("Томат")
        self.plot.plant_seed("Огурец")
        self.plot.water_garden()
        self.assertTrue(self.plot.soil.is_hydrated)
        self.assertEqual(self.plot.watering_system.current_water, 180)

    def test_process_growth_resets_soil(self):
        self.plot.plant_seed("Морковь")
        self.plot.water_garden()
        self.plot.process_growth()
        
        self.assertEqual(self.plot.plants[0].state, PlantState.SPROUT)
        self.assertFalse(self.plot.soil.is_hydrated)
        self.assertFalse(self.plot.soil.is_fertilized)

    def test_develop_recreation_zone(self):
        self.plot.develop_recreation_zone()
        self.assertEqual(self.plot.recreation_zone.build_progress, 25)
        self.assertEqual(self.plot.tools[2].durability, 75)
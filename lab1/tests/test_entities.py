import unittest
from garden.entities import Tool, Plant, PlantState, Soil, WateringSystem, RecreationZone
from garden.exceptions import ResourceExhaustedError, InvalidStateTransitionError

class TestTool(unittest.TestCase):
    def setUp(self):
        self.tool = Tool("Лопата")

    def test_tool_use_and_durability(self):
        self.assertEqual(self.tool.durability, 100)
        self.tool.use(15)
        self.assertEqual(self.tool.durability, 85)

    def test_tool_exhaustion(self):
        self.tool.use(100)
        with self.assertRaises(ResourceExhaustedError):
            self.tool.use(10)

    def test_tool_repair(self):
        self.tool.use(90)
        self.tool.repair()
        self.assertEqual(self.tool.durability, 100)

class TestPlant(unittest.TestCase):
    def setUp(self):
        self.plant = Plant("Огурец")
        self.soil = Soil()

    def test_growth_requires_water(self):
        with self.assertRaises(InvalidStateTransitionError):
            self.plant.grow(self.soil)

    def test_successful_growth_cycle(self):
        self.soil.is_hydrated = True
        self.plant.grow(self.soil)
        self.assertEqual(self.plant.state, PlantState.SPROUT)
        
        self.soil.is_hydrated = True
        self.soil.is_fertilized = True
        self.plant.grow(self.soil)
        self.assertEqual(self.plant.state, PlantState.MATURE)

    def test_weed_infestation_and_death(self):
        self.soil.is_hydrated = True
        self.plant.grow(self.soil)
        
        self.soil.is_hydrated = True
        self.plant.grow(self.soil)
        self.assertEqual(self.plant.state, PlantState.WEED_INFESTED)
        
        self.plant.grow(self.soil)
        self.assertEqual(self.plant.state, PlantState.DEAD)

class TestWateringSystem(unittest.TestCase):
    def setUp(self):
        self.system = WateringSystem(200)
        self.soil = Soil()

    def test_water_consumption_based_on_plants(self):
        self.system.water(self.soil, 3)
        self.assertEqual(self.system.current_water, 170)
        self.assertTrue(self.soil.is_hydrated)

    def test_insufficient_water(self):
        self.system.current_water = 20
        with self.assertRaises(ResourceExhaustedError):
            self.system.water(self.soil, 5)

    def test_refill(self):
        self.system.water(self.soil, 5)
        self.system.refill()
        self.assertEqual(self.system.current_water, 200)

class TestRecreationZone(unittest.TestCase):
    def setUp(self):
        self.zone = RecreationZone()
        self.hammer = Tool("Молоток")

    def test_build_progress(self):
        self.assertEqual(self.zone.build_progress, 0)
        self.zone.build(self.hammer)
        self.assertEqual(self.zone.build_progress, 25)
        self.assertEqual(self.hammer.durability, 75)

    def test_decoration_limits(self):
        for _ in range(4):
            self.zone.build(self.hammer)
            
        self.assertTrue(self.zone.is_built)
        
        self.zone.add_decoration("Стул")
        self.zone.add_decoration("Стол")
        self.zone.add_decoration("Мангал")
        
        with self.assertRaises(ResourceExhaustedError):
            self.zone.add_decoration("Гном")

    def test_premature_decoration(self):
        self.zone.build(self.hammer)
        with self.assertRaises(InvalidStateTransitionError):
            self.zone.add_decoration("Стул")
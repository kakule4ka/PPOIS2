from typing import List
from garden.entities import Soil, Tool, Plant, WateringSystem, RecreationZone
from garden.exceptions import GardenLogicError

class GardenPlot:
    def __init__(self):
        self.soil: Soil = Soil()
        self.watering_system: WateringSystem = WateringSystem(200)
        self.recreation_zone: RecreationZone = RecreationZone()
        self.tools: List[Tool] = [
            Tool("Лопата"),
            Tool("Грабли"),
            Tool("Молоток")
        ]
        self.plants: List[Plant] = []

    def plant_seed(self, species: str):
        self.tools[0].use(10)
        self.plants.append(Plant(species))

    def water_garden(self):
        self.watering_system.water(self.soil, len(self.plants))

    def refill_water(self):
        self.watering_system.refill()

    def fertilize_soil(self):
        self.tools[1].use(15)
        self.soil.is_fertilized = True

    def weed_plants(self):
        self.tools[1].use(10)
        for plant in self.plants:
            if plant.state.name == "WEED_INFESTED":
                plant.weed()

    def process_growth(self) -> List[str]:
        messages = []
        for plant in self.plants:
            try:
                plant.grow(self.soil)
                messages.append(f"{plant.species} -> {plant.state.value}")
            except GardenLogicError as e:
                messages.append(f"{plant.species}: {e}")
        
        self.soil.is_hydrated = False
        self.soil.is_fertilized = False
        
        return messages

    def maintain_tool(self, tool_index: int):
        self.tools[tool_index].repair()

    def develop_recreation_zone(self):
        self.recreation_zone.build(self.tools[2])

    def decorate_zone(self, item: str):
        self.recreation_zone.add_decoration(item)
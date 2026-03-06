from enum import Enum
from typing import List
from garden.exceptions import InvalidStateTransitionError, ResourceExhaustedError


class PlantState(Enum):
    SEED = "Семечко"
    SPROUT = "Росток"
    WEED_INFESTED = "В сорняках"
    MATURE = "Созрело"
    HARVESTED = "Собрано"
    DEAD = "Мертвое"


class Soil:
    def __init__(self):
        self.is_hydrated: bool = False
        self.is_fertilized: bool = False


class Tool:
    def __init__(self, name: str):
        self.name: str = name
        self.durability: int = 100

    def use(self, wear_amount: int):
        if self.durability <= 0:
            raise ResourceExhaustedError(f"Инструмент '{self.name}' сломан (0%).")
        self.durability -= wear_amount
        if self.durability < 0:
            self.durability = 0

    def repair(self):
        self.durability = 100


class Plant:
    def __init__(self, species: str):
        self.species: str = species
        self.state: PlantState = PlantState.SEED

    def grow(self, soil: Soil):
        if self.state in (PlantState.HARVESTED, PlantState.DEAD):
            raise InvalidStateTransitionError("Растение мертво или уже собрано.")
        
        if self.state == PlantState.WEED_INFESTED:
            self.state = PlantState.DEAD
            return

        if self.state == PlantState.SEED and soil.is_hydrated:
            self.state = PlantState.SPROUT
        elif self.state == PlantState.SPROUT:
            if not soil.is_fertilized:
                self.state = PlantState.WEED_INFESTED
            elif soil.is_hydrated:
                self.state = PlantState.MATURE
            else:
                raise InvalidStateTransitionError("Нужна вода для роста.")
        else:
            raise InvalidStateTransitionError("Условия для роста не выполнены.")

    def weed(self):
        if self.state != PlantState.WEED_INFESTED:
            raise InvalidStateTransitionError("Растение не нуждается в прополке.")
        self.state = PlantState.SPROUT


class WateringSystem:
    def __init__(self, max_capacity: int):
        self.max_capacity: int = max_capacity
        self.current_water: int = max_capacity

    def water(self, soil: Soil, plants_count: int):
        cost = 10 if plants_count == 0 else plants_count * 10
        if self.current_water < cost:
            raise ResourceExhaustedError(f"Недостаточно воды. Требуется {cost}.")
        soil.is_hydrated = True
        self.current_water -= cost

    def refill(self):
        self.current_water = self.max_capacity

class RecreationZone:
    def __init__(self):
        self.build_progress: int = 0
        self.decorations: List[str] = []
        self.max_decorations: int = 3

    @property
    def is_built(self) -> bool:
        return self.build_progress >= 100

    def build(self, hammer: Tool):
        if self.is_built:
            raise InvalidStateTransitionError("Зона отдыха уже полностью построена.")
        hammer.use(25)
        self.build_progress += 25

    def add_decoration(self, item: str):
        if not self.is_built:
            raise InvalidStateTransitionError("Сначала достройте зону отдыха на 100%.")
        if len(self.decorations) >= self.max_decorations:
            raise ResourceExhaustedError("Превышен лимит декораций (максимум 3).")
        self.decorations.append(item)
class GardenLogicError(Exception):
    pass

class ResourceExhaustedError(GardenLogicError):
    pass

class InvalidStateTransitionError(GardenLogicError):
    pass

class ToolAlreadyPristineError(GardenLogicError):
    pass

class TankAlreadyFullError(GardenLogicError):
    pass

class PlotCapacityError(GardenLogicError):
    pass
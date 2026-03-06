class GardenLogicError(Exception):
    pass

class ResourceExhaustedError(GardenLogicError):
    pass

class InvalidStateTransitionError(GardenLogicError):
    pass
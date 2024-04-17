class KeyViolationException(Exception):

    def __init__(self, message: str, detailed_message: str = None):
        self.message = message
        self.detailed_message= detailed_message
        super().__init__(message)

class EntityDoesNotExistException(Exception):
    pass
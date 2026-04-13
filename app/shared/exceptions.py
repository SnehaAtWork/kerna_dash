class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} not found: {entity_id}")


class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
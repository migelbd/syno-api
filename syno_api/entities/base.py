class Entity:

    def __init__(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def to_dict(self):
        return {k: v.to_dict() if isinstance(v, Entity) else v for k, v in self.__dict__.items()}

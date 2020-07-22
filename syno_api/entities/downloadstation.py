from typing import List

from syno_api.entities.base import Entity


class Additional(Entity):
    pass


class Task(Entity):
    id: str
    type: str
    username: str
    title: str
    size: int
    status: str

    status_extra: str
    additional: Additional

    def __init__(self, data: dict):
        data['additional'] = Additional(data.get('additional', {}))
        super().__init__(data)

    def __repr__(self):
        return f'Task: {self.id} {self.title}'

    @property
    def is_bit_torrent(self):
        return self.type == 'bt'


class TaskInfo(Entity):
    tasks: List[Task]

    def __init__(self, data: dict):
        data['tasks'] = [Task(t) for t in data['tasks']]
        super().__init__(data)

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)


class TaskList(TaskInfo):
    offset: int
    total: int

    def __len__(self):
        return self.total

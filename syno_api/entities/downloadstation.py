from typing import List

from syno_api.entities.base import Entity


class TaskDetail(Entity):
    destination: str
    uri: str
    create_time: str
    priority: str
    total_peers: int
    connected_seeders: int
    connected_leechers: int


class TaskTransfer(Entity):
    size_downloaded: str
    size_uploaded: str
    speed_download: str
    speed_upload: str


class TaskFile(Entity):
    filename: str
    size: str
    size_downloaded: str
    priority: str


class TaskTracker(Entity):
    url: str
    status: str
    update_timer: int
    seeds: int
    peers: int


class TaskPeer(Entity):
    address: str
    agent: str
    progress: float
    speed_download: int
    speed_upload: int


class StatusExtra(Entity):
    error_detail: str
    unzip_progress: int


class Additional(Entity):
    detail: TaskDetail
    transfer: TaskTransfer
    file: List[TaskFile]
    tracker: List[TaskTracker]
    peer: List[TaskPeer]

    def __init__(self, data: dict):
        data['detail'] = TaskDetail(data.get('detail', {}))
        data['transfer'] = TaskTransfer(data.get('transfer', {}))
        data['file'] = [TaskFile(f) for f in data.get('file', [])]
        data['tracker'] = [TaskTransfer(tr) for tr in data.get('tracker', [])]
        data['peer'] = [TaskPeer(p) for p in data.get('peer', [])]

        super().__init__(data)


class Task(Entity):
    id: str
    type: str
    username: str
    title: str
    size: int
    status: str

    status_extra: StatusExtra
    additional: Additional

    def __init__(self, data: dict):
        data['additional'] = Additional(data.get('additional', {}))
        data['status_extra'] = StatusExtra(data.get('status_extra', {}))
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

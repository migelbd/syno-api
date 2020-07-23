# Synology Web Api Wrapper


### Installation
```shell script
pip install syno-api
```

### Features
API | Status
--- | ---
Download Station | partially implemented
File Station | planned


### Example

```python
from syno_api import DownloadStation

ds = DownloadStation('user', 'pass', 'ip_host', port=5000)

for task in ds.task_list():
    print(task.title)

ds.task_create('magnet://qwe')
```
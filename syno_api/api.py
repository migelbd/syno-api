from typing import Union, List, Tuple

from .base import BaseApiInterface
from .entities.downloadstation import TaskList, Task, TaskInfo
from .exceptions import SynoApiError


class DownloadStation(BaseApiInterface):

    def task_list(self, offset=0, limit=-1, additional=None) -> TaskList:
        """
        List of tasks
        :param offset:
        :param limit:
        :param additional:
        :return:
        """
        if additional:
            additional = ','.join(additional)
        response = self.request_get('Task', 'list', additional=additional, offset=offset, limit=limit)

        return TaskList(response.data)

    def task_create(self, uri_or_file, destination=None, username=None, password=None, unzip_password=None) -> bool:
        """
            Create task

        :param uri_or_file: Accepts HTTP/FTP/magnet/ED2K links or the file path starting with a shared folder
        :param destination: Download destination path starting with a shared folder
        :param username: Login username
        :param password: Login password
        :param unzip_password: Password for unzipping download tasks
        :raise DestinationDenied:
        :raise DestinationDoesNotExists:
        :raise NoDefaultDestination:
        :raise SetDestinationFailed:
        :rtype bool:
        :return True if success:
        """
        uri = None
        file = None

        if isinstance(uri_or_file, str):
            uri = uri_or_file
        else:
            file = uri_or_file
        request_params = dict(
            uri=uri,
            file=file,
            destination=destination,
            username=username,
            password=password,
            unzip_password=unzip_password
        )
        if file:
            response = self.request_post('Task', 'create', **request_params)
        else:
            response = self.request_get('Task', 'create', **request_params)

        return response.is_success

    def task_pause(self, task_id: Union[str, List[str], Tuple[str], Task]):
        if isinstance(task_id, (list, tuple,)):
            task_id = ','.join(task_id)
        elif isinstance(task_id, Task):
            task_id = task_id.id

        return self.request_get('Task', 'pause', id=task_id)

    def task_resume(self, task_id: Union[str, List[str], Tuple[str], Task]):
        if isinstance(task_id, (list, tuple,)):
            task_id = ','.join(task_id)
        elif isinstance(task_id, Task):
            task_id = task_id.id

        return self.request_get('Task', 'resume', id=task_id)

    def task_delete(self, task_id: Union[str, List[str], Tuple[str], Task], force_complete: bool = False):
        if isinstance(task_id, (list, tuple,)):
            task_id = ','.join(task_id)
        elif isinstance(task_id, Task):
            task_id = task_id.id

        return self.request_get('Task', 'delete', id=task_id, force_complete=force_complete)

    def task_info(self, task_id: Union[str, List[str], Tuple[str], Task], additional=None) -> TaskInfo:
        """

        :param task_id:
        :param additional:
        :return:
        """
        if isinstance(task_id, (list, tuple,)):
            task_id = ','.join(task_id)
        elif isinstance(task_id, Task):
            task_id = task_id.id

        if additional:
            additional = ','.join(additional)
        response = self.request_get('Task', 'getinfo', id=task_id, additional=additional)

        return TaskInfo(response.data)

    class FileUploadFailed(SynoApiError):
        code = 400
        message = 'File upload failed'

    class MaxNumberTaskReached(SynoApiError):
        code = 401
        message = 'Max number of tasks reached'

    class DestinationDenied(SynoApiError):
        code = 402
        message = 'Destination denied'

    class DestinationDoesNotExists(SynoApiError):
        code = 403
        message = 'Destination does not exist'

    class TaskNotFound(SynoApiError):
        code = 404
        message = 'Invalid task id'

    class InvalidTaskAction(SynoApiError):
        code = 405
        message = 'Invalid task action'

    class NoDefaultDestination(SynoApiError):
        code = 406
        message = 'No default destination'

    class SetDestinationFailed(SynoApiError):
        code = 407
        message = 'Set destination failed'

    class FileDoesNotExists(SynoApiError):
        code = 408
        message = 'File does not exist'

from typing import Union, List, Tuple

from .auth import Auth
from .base_request import BaseApiInterface, get_error_code
from .entities.downloadstation import TaskList, Task, TaskInfo
from .exceptions import SynoApiError


class DownloadStation(BaseApiInterface):

    def get_exception_map(self, code):
        exc_map = {
            400: DownloadStation.FileUploadFailed,
            401: DownloadStation.MaxNumberTaskReached,
            402: DownloadStation.DestinationDenied,
            403: DownloadStation.DestinationDoesNotExists,
            404: DownloadStation.TaskNotFound,
            405: DownloadStation.InvalidTaskAction,
            406: DownloadStation.NoDefaultDestination,
            407: DownloadStation.SetDestinationFailed,
            408: DownloadStation.FileDoesNotExists
        }
        return exc_map.get(code, SynoApiError)

    def __init__(self, username, password, host, port=5000, secure=False):
        super().__init__(username, password, host, port, secure)
        self.auth = Auth(username, password, host, port, secure)
        self.auth.login(self.api_name)
        self._sid = self.auth.sid()

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
        response, error_code = self.request_get('Task', 'list', additional=additional, offset=offset, limit=limit)

        if error_code:
            raise self.get_exception_map(error_code)(response_data=response)
        return TaskList(response)

    def task_create(self, uri):
        pass

    def task_pause(self, task_id: Union[str, list, tuple]):
        if isinstance(task_id, (list, tuple,)):
            task_id = ','.join(task_id)

        response, error_code = self.request_get('Task', 'pause', id=task_id)

        if error_code:
            raise self.get_exception_map(error_code)(response_data=response)
        return response

    def task_resume(self):
        pass

    def task_delete(self):
        pass

    def task_info(self, task_id: Union[str, List[str], Tuple[str], Task], additional=None):
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
        response, error_code = self.request_get('Task', 'getinfo', id=task_id, additional=additional)

        if error_code:
            raise self.get_exception_map(error_code)(response_data=response)
        return TaskInfo(response)

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

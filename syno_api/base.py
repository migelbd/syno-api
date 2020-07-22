from typing import Optional

import requests

from syno_api.exceptions import SynoApiError
import logging

logger = logging.getLogger(__name__)

from importlib import import_module

COMMON_EXCEPTIONS = {
    100: 'exceptions.UnknownError',
    101: 'exceptions.InvalidParameter',
    102: 'exceptions.InvalidRequestAPI',
    103: 'exceptions.MethodNotExists',
    104: 'exceptions.NotSupportVersion',
    105: 'exceptions.ForbiddenRequest',
    106: 'exceptions.SessionTimeout',
    107: 'exceptions.SessionInterrupted'
}

AUTH_EXCEPTIONS = {
    400: 'exceptions.NoSuchAccountOrIncorrectPassword',
    401: 'exceptions.AccountDisabled',
    402: 'exceptions.PermissionDenied',
    403: 'exceptions.VerificationCode2StepRequired',
    404: 'exceptions.FailedAuthenticate2StepVerificationCode'
}
DOWNLOAD_STATION_EXCEPTIONS = {
    400: 'api.DownloadStation.FileUploadFailed',
    401: 'api.DownloadStation.MaxNumberTaskReached',
    402: 'api.DownloadStation.DestinationDenied',
    403: 'api.DownloadStation.DestinationDoesNotExists',
    404: 'api.DownloadStation.TaskNotFound',
    405: 'api.DownloadStation.InvalidTaskAction',
    406: 'api.DownloadStation.NoDefaultDestination',
    407: 'api.DownloadStation.SetDestinationFailed',
    408: 'api.DownloadStation.FileDoesNotExists'
}

API_EXC_MAP = {
    'Common': COMMON_EXCEPTIONS,
    'DownloadStation': DOWNLOAD_STATION_EXCEPTIONS,
    'Auth': AUTH_EXCEPTIONS
}


def _error_handler(response):
    if response.error_code:
        exc_name = API_EXC_MAP.get(response.api_namespace, {}).get(response.error_code)
        if not exc_name:
            exc_name = API_EXC_MAP.get('Common').get(response.error_code, 'exceptions.UnknownError')
        exc = import_module(exc_name)
        raise exc(response_obj=response)
    return response


def _prepare_params(params):
    result_params = {}
    for k, v in params.items():
        if isinstance(v, bool):
            result_params[k] = str(v).lower()
        elif v is None:
            continue
        else:
            result_params[k] = v
    return result_params


class ApiResponse(object):

    def __init__(self, response, api_namespace):
        self.status_code = response.status_code
        response_json_data = response.json()
        self.api_namespace = api_namespace

        self._data = response_json_data.get('data', {})
        self._success = response_json_data.get('success', False)
        self._error_code = response_json_data.get('error', {}).get('code')

    @property
    def is_success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict:
        return self._data

    @property
    def error_code(self) -> int:
        return self._error_code

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value


class BaseApiInterface:
    __API_PREFIX = 'SYNO'

    _QUERY_API_LIST = [
        'SYNO.API.Info',
        'SYNO.API.Auth',
        'SYNO.DownloadStation.Task',
        'SYNO.DownloadStation.Schedule',
        'SYNO.DownloadStation.Info',
    ]

    def __init__(self, username, password, host, port=5000, secure=False, auto_login=True):
        self.schema = 'https' if secure else 'http'
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._base_url = '%s://%s:%s/webapi/' % (self.schema, self._host, self._port)
        self._sid = None
        self._session_expired = True
        self._api_list = dict()
        self._app_api_list = dict()
        if auto_login:
            self.login()

    def login(self):
        if not self._session_expired and self._sid:
            self._session_expired = False
            logger.info('User already logged')
            return True
        params = dict(
            account=self._username, passwd=self._password,
            session=self.api_name,
            format='cookie',
            method='login'
        )

        response = self._request('SYNO.API.Auth', params, 'get', response_namespace='Auth')
        self._sid = response.data.get('sid')
        self._session_expired = False

    def sid(self):
        return self._sid

    @property
    def api_name(self):
        return type(self).__name__

    def load_api_list(self):
        params = {
            'path': 'query.cgi',
            'version': 1,
            'method': 'query',
            'query': ','.join(self._QUERY_API_LIST)
        }
        response = self._request('SYNO.API.Info', params, method='get', skip_prepare_params=True)
        self._api_list = response.data

    def api_url(self, api_name, path):
        return '%s%s?api=%s' % (self._base_url, path, api_name)

    @property
    def api_list(self) -> dict:
        if not len(self._api_list):
            self.load_api_list()
        return self._api_list

    def get_api_path(self, api_name, params=None) -> dict:
        result_params = {}
        if api_name in self.api_list:
            api_params: dict = self.api_list[api_name]
            result_params = dict(
                path=api_params.get('path'),
                version=api_params.get('maxVersion'),
                _sid=self.sid()
            )

        if params:
            result_params.update(params)
        return result_params

    def _request(self, api_name, params, method=None, **kwargs) -> ApiResponse:
        if not kwargs.get('skip_prepare_params'):
            api_params = _prepare_params(self.get_api_path(api_name, params))
        else:
            api_params = params
        path = api_params.pop('path')
        request_url = self.api_url(api_name, path)

        if method == 'get':
            response = requests.get(request_url, api_params)
        elif method == 'post':
            response = requests.post(request_url, api_params)
        else:
            response = None

        if response.status_code != 200:
            raise Exception('HTPP Error')

        return _error_handler(ApiResponse(response, kwargs.get('response_namespace', self.api_name)))

    def _get_application_api(self, api_name):
        req_api_name = None
        if not api_name:
            req_api_name = self.api_name

        if not str(api_name).startswith(self.__API_PREFIX):
            req_api_name = f'{self.__API_PREFIX}.{self.api_name}.{api_name}'
        return req_api_name

    def request_get(self, sub_api_name, method, **params) -> ApiResponse:
        params['method'] = method
        return self._request(self._get_application_api(sub_api_name), params, method='get')

    def request_post(self, sub_api_name, method, **params) -> ApiResponse:
        params['method'] = method
        return self._request(self._get_application_api(sub_api_name), params, method='post')

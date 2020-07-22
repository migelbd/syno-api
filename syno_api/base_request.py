from typing import Optional

import requests

from syno_api.exceptions import SynoApiError
import logging

logger = logging.getLogger(__name__)

def raise_common_exception(code, response_data):
    from . import exceptions
    exceptions_map = {
        100: exceptions.UnknownError,
        101: exceptions.InvalidParameter,
        102: exceptions.InvalidRequestAPI,
        103: exceptions.MethodNotExists,
        104: exceptions.NotSupportVersion,
        105: exceptions.ForbiddenRequest,
        106: exceptions.SessionTimeout,
        107: exceptions.SessionInterrupted,
    }
    exc = exceptions_map.get(code)
    if exc:
        raise exc(response_data=response_data)


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


def get_error_code(response_data: dict) -> Optional[int]:
    if 'error' in response_data:
        return response_data['error']['code']
    return False


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
        response = self.request_get('SYNO.API.Auth', 'login', account=self._username, passwd=self._password,
                                    session=self.api_name,
                                    format='cookie')
        self._sid = response.get('sid')
        self._session_expired = False
        logger.info('User logging... New session started!')
        return bool(self._sid)

    def sid(self):
        return self._sid

    def get_exception_map(self, code):
        from . import exceptions
        exc_map = {
            100: exceptions.UnknownError,
            101: exceptions.InvalidParameter,
            102: exceptions.InvalidRequestAPI,
            103: exceptions.MethodNotExists,
            104: exceptions.NotSupportVersion,
            105: exceptions.ForbiddenRequest,
            106: exceptions.SessionTimeout,
            107: exceptions.SessionInterrupted,
        }
        return exc_map.get(code)

    @property
    def api_name(self):
        return type(self).__name__

    def load_api_list(self):
        url = '%s%s' % (self._base_url, 'query.cgi')
        response = requests.get(url, {'api': 'SYNO.API.Info', 'version': 1, 'method': 'query',
                                      'query': ','.join(self._QUERY_API_LIST)})
        if response.status_code == 200:
            response_data = response.json()
            if not response_data.get('success', False):
                raise Exception('Request not success')
            self._api_list = response_data.get('data', {})
        else:
            raise Exception('HTTP Status code' + str(response.status_code))

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

    def _request(self, api_name, params, method=None):
        api_params = _prepare_params(self.get_api_path(api_name, params))
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
        response_json = response.json()
        response_data = response_json.get('data') or response_json.get('success', False)
        error_code = get_error_code(response_json)
        error = self.get_exception_map(error_code)
        if error:
            raise error(response_data=response_data)
        return response_data

    def request_get(self, sub_api_name, method, **params):
        params['method'] = method
        req_api_name = None
        if not sub_api_name:
            req_api_name = self.api_name

        if not str(req_api_name).startswith(self.__API_PREFIX):
            req_api_name = f'{self.__API_PREFIX}.{self.api_name}.{sub_api_name}'
        return self._request(req_api_name, params, method='get')

    def request_post(self, sub_api_name, method, **params):
        params['method'] = method
        req_api_name = None
        if not sub_api_name:
            req_api_name = self.api_name

        if not str(req_api_name).startswith(self.__API_PREFIX):
            req_api_name = f'{self.__API_PREFIX}.{self.api_name}.{sub_api_name}'
        return self._request(req_api_name, params, method='post')


import requests
import logging

from syno_api.base_request import BaseApiInterface

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
        400: exceptions.NoSuchAccountOrIncorrectPassword,
        401: exceptions.AccountDisabled,
        402: exceptions.PermissionDenied,
        403: exceptions.VerificationCode2StepRequired,
        404: exceptions.FailedAuthenticate2StepVerificationCode,

    }
    exc = exceptions_map.get(code, exceptions.UnknownError)
    raise exc(response_data=response_data)


class Auth(BaseApiInterface):

    @property
    def api_name(self):
        return 'SYNO.API.Auth'

    def login(self, api_name):
        if not self._session_expired and self._sid:
            self._session_expired = False
            logger.info('User already logged')
            return True
        response, error_code = self.request_get(None, 'login', account=self._username, passwd=self._password,
                                                session=api_name,
                                                format='cookie')
        if error_code:
            raise_common_exception(error_code, response)
        self._sid = response.get('sid')
        self._session_expired = False
        logger.info('User logging... New session started!')
        return bool(self._sid)

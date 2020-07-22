import requests
import logging

from syno_api.base_request import BaseApiInterface
from syno_api.exceptions import SynoApiError

logger = logging.getLogger(__name__)


class Auth(BaseApiInterface):

    def get_exception_map(self, code):
        from . import exceptions
        exc_map = {
            400: exceptions.NoSuchAccountOrIncorrectPassword,
            401: exceptions.AccountDisabled,
            402: exceptions.PermissionDenied,
            403: exceptions.VerificationCode2StepRequired,
            404: exceptions.FailedAuthenticate2StepVerificationCode,
        }
        return exc_map.get(code, super(Auth, self).get_exception_map(code))




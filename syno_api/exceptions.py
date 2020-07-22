class SynoApiError(Exception):
    code = 0
    message = 'SynoApiError'
    response_data = None

    def __init__(self, message=None, response_obj=None, *args):
        self.response_obj = response_obj
        super().__init__(message or self.message, *args)


class UnknownError(SynoApiError):
    code = 100
    message = 'Unknown error'


class InvalidParameter(SynoApiError):
    code = 101
    message = 'Invalid parameter'


class InvalidRequestAPI(SynoApiError):
    code = 102
    message = 'The requested API does not exist'


class MethodNotExists(SynoApiError):
    code = 103
    message = 'The requested method does not exist'


class NotSupportVersion(SynoApiError):
    code = 104
    message = 'The requested version does not support the functionality'


class ForbiddenRequest(SynoApiError):
    code = 105
    message = 'The logged in session does not have permission'


class SessionTimeout(SynoApiError):
    code = 106
    message = 'Session timeout'


class SessionInterrupted(SynoApiError):
    code = 107
    message = 'Session interrupted by duplicate login'


class NoSuchAccountOrIncorrectPassword(SynoApiError):
    code = 400
    message = 'No such account or incorrect password'


class AccountDisabled(SynoApiError):
    code = 401
    message = 'Account disabled'


class PermissionDenied(SynoApiError):
    code = 402
    message = 'Permission denied'


class VerificationCode2StepRequired(SynoApiError):
    code = 403
    message = '2-step verification code required'


class FailedAuthenticate2StepVerificationCode(SynoApiError):
    code = 404
    message = 'Failed to authenticate 2-step verification code'

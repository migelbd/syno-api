from functools import wraps


# def validate_response(func):
#
#     @wraps(func)
#     def wrrapper(*args, **kwargs):
#
#         response = func(*args, **kwargs)
#         if 'error' in response
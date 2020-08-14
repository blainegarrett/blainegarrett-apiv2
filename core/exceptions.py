# Common Exceptions


class PermissionException(Exception):
    """
    Internal Exception when permission to an object cannot be granted
    Any HTTP Handler catching this error should set a 403 response code
    """


class AuthenticationException(Exception):
    """
    Internal Exception when an authentication attempt fails
    Any HTTP Handler catching this error should set a 401 response code
    """


class DoesNotExistException(Exception):
    """
    Internal exception when an object cannot be found
    Any HTTP Handler catching this error should set a 404 response code
    """


class ConflictException(Exception):
    """
    Internal Exception when an obect could not be created or mutated due to a conflict, such
    as when the object already existsself.
    Any HTTP handler catching this error should set a 409 response code
    """

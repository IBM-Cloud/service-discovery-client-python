"""
 Global exception registry
"""


class APIException(Exception):
    """
    Generic Exception wrapper
    """

    status_code = 500

    def __init__(self, message, user_details=None, internal_details=None):
        """
        Create a new APIException

        :param message:             General exception message
        :param user_details:        Message to be shown to user
        :param internal_details:    Additional details provided by the system
        """
        self.message = message
        self.internal_details = internal_details
        if user_details is not None:
            self.user_details = user_details
        else:
            self.user_details = self.message

        super(APIException, self).__init__(self, message)

    def __str__(self):
        exception_str = super(APIException, self).__str__()
        dict_str = str(self.__dict__)
        return '{0} {1}'.format(exception_str, dict_str)

    def __unicode__(self):
        exception_str = super(APIException, self).__unicode__()
        dict_str = unicode(self.__dict__)
        return u'{0} {1}'.format(exception_str, dict_str)

    def to_dict(self):
        """
        Convert this exception to a dict for serialization.
        """
        return {
            'error': self.user_details
        }


class ValidationException(APIException):
    """
    Indicates an exception when Service Discovery validates input data.
    """

    status_code = 400

    def __init__(self, message, user_details=None, internal_details=None):
        super(ValidationException, self).__init__(
            message, user_details=user_details, internal_details=internal_details)


class AuthenticationException(APIException):
    """
    Raised when authentication with Service Discovery fails.
    """

    status_code = 401

    def __init__(self, message, user_details=None, internal_details=None):
        super(AuthenticationException, self).__init__(
            message, user_details=user_details,
            internal_details=internal_details)


class NotFoundException(APIException):
    """
    Raised when the given Service Discovery URL is not found.
    """

    status_code = 404

    def __init__(self, user_details=None, internal_details=None, *args):
        if len(args) > 0:
            message = args[0]
        else:
            message = 'Resource does not exist.'
        super(NotFoundException, self).__init__(
            message, user_details=user_details,
            internal_details=internal_details)


class ResourceGoneException(APIException):
    """
    Raised when the referenced service may have once existed, but currently does not.
    """

    status_code = 410

    def __init__(self, message, user_details=None, internal_details=None):
        super(ResourceGoneException, self).__init__(
            message, user_details=user_details, internal_details=internal_details)

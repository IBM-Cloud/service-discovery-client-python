import json
from requests import request
from bluemix_service_discovery.utils import load_credentials, add_query_string
from bluemix_service_discovery import exceptions


class ServiceLocator:
    """Search for service instances"""

    def __init__(self, url=None, auth_token=None):
        """
        Initializes the service instance with all its parameters.

        :param url:         Service Discovery API endpoint.
        :param auth_token:  Authorization token for Service Discovery.
        """

        # Get credentials
        credentials = load_credentials(url, auth_token)
        self.url = credentials['url']
        self.token = credentials['auth_token']

    def get_services(self, fields=None, tags=None, service_name=None, status=None):
        """
        Returns all the currently registered services and their parameters.

        :param fields       Comma separated list of fields to include in response.
        :param tags         Comma separated list of tags that returned instances must have.
        :param service_name Name of instances to return.
        :param status       State of instances to be return.

        :return response
        """

        # Add filters to query
        status_query = add_query_string(('fields', fields), ('tags', tags),
                                        ('service_name', service_name), ('status', status))

        retrieve_services_url = '%s/api/v1/instances%s' % (self.url, status_query)
        headers = {'Authorization': 'Bearer %s' % self.token}

        try:
            response = request("GET", retrieve_services_url, headers=headers)
        except Exception as e:
            raise exceptions.APIException('Error on service lookup', str(e))

        # Check for possible errors in response
        if response.status_code == 400:
            raise exceptions.ValidationException('Bad request to service registry',
                                                 internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 401:
            raise exceptions.AuthenticationException('Unauthorized service lookup: token is not valid',
                                                     internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 404:
            raise exceptions.NotFoundException('Bad Service Discovery URL',
                                               internal_details=response.text)

        return response.text

import json
from os import environ as env


def load_credentials(url=None, auth_token=None):
    """
    Returns the Service Discovery credentials, if available

    :param url:         Service Discovery API URL
    :param auth_token:  Access token for Service Discovery
    :return:            The URL and Auth credentials
    """
    if env.get('VCAP_SERVICES') is not None:
        return {
            'url': json.loads(env['VCAP_SERVICES'])['service_discovery'][0]['credentials']['url'],
            'auth_token': json.loads(env['VCAP_SERVICES'])['service_discovery'][0]['credentials']['auth_token']
        }
    else:
        if auth_token is None:
            raise Exception("An auth token is required for Service Discovery")
        return {
            'url': url if url is not None else "https://servicediscovery.ng.bluemix.net",
            'auth_token': auth_token
        }


def add_query_string(*filters):
    """
    Compose a query string from input filters

    :param filters: List of (filter, value) tuples

    :return:        Query string
    """
    status_query = ''
    for fil in filters:
        if fil[1] is not None and fil[1] != '':
            status_query = '?' if status_query == '' else status_query + '&'
            status_query += '%s=%s' % (fil[0], fil[1])

    return status_query

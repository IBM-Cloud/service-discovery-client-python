import json
import time
from requests import request
from threading import Thread
from bluemix_service_discovery.utils import load_credentials
from bluemix_service_discovery import exceptions


class ServicePublisher:
    """Register and heartbeat a new service instance"""

    def __init__(self, name, ttl, status, endpoint, protocol, tags=None, url=None, auth_token=None):
        """
        Initializes the service instance with all its parameters.

        :param name:        Name of the service.
        :param ttl:         Time (sec) in which the service must register a heartbeat.
        :param status:      Starting status of the service.
        :param endpoint:    Endpoint of the service.
        :param protocol:    Desired protocol of the service endpoint.
        :param tags:        Tags to associate with the service.
        :param url:         Service Discovery API endpoint.
        :param auth_token:  Authorization token for Service Discovery.
        """
        self.name = name
        self.ttl = ttl
        self.status = status
        self.endpoint = {
            'value': endpoint,
            'type': protocol
        }
        self.tags = [] if tags is None else tags

        # Get credentials
        credentials = load_credentials(url, auth_token)
        self.url = credentials['url']
        self.token = credentials['auth_token']

        # Uninitialized vars
        self.heartbeats = []
        self.heartbeat_thread = None
        self.heartbeat_url = None
        self.id = None

        # Flags
        self.beating = False
        self.registered = False

    def register_service(self, heartbeat=True):
        """
        Registers the service with Service Discovery.

        :param heartbeat:   Indicates whether or not to spawn a heartbeat thread.
        :return:            Successful service registration object
        """

        # Create the API request payload and headers
        registration_payload = {
            'tags': self.tags,
            'status': self.status,
            'service_name': self.name,
            'ttl': self.ttl,
            'endpoint': self.endpoint
        }
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }

        # Call Service Discovery /instances to register the service
        try:
            response = request("POST",
                               '%s/api/v1/instances' % self.url,
                               data=json.dumps(registration_payload),
                               headers=headers)
        except Exception as e:
            raise exceptions.APIException('Error registering controller service', internal_details=str(e))

        # Check for possible errors in response
        if response.status_code == 400:
            raise exceptions.ValidationException('Bad request to service registry',
                                                 internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 401:
            raise exceptions.AuthenticationException('Unauthorized service registration: token is not valid',
                                                     internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 404:
            raise exceptions.NotFoundException('Bad Service Discovery URL',
                                               internal_details=response.text)

        # Set instance values based on returned object
        self.registered = True
        self.id = json.loads(response.text)['id']
        self.heartbeat_url = json.loads(response.text)['links']['heartbeat']

        # Spawn thread responsible for sending heartbeat
        if heartbeat:
            self.heartbeat_thread = Thread(target=self._heartbeater,
                                           kwargs={'interval': round(self.ttl*.5)})
            self.heartbeat_thread.start()

        return response.text

    def heartbeat_service(self):
        """
        Heartbeats the service with Service Discovery.
        """

        # First make sure service has been registered
        if not self.registered:
            raise Exception('Service instance is not registered')

        # Call Service Discovery /instances/XXX/heartbeat to heartbeat the service
        try:
            response = request("PUT",
                               self.heartbeat_url,
                               headers={'Authorization': 'Bearer %s' % self.token})
        except Exception as e:
            raise exceptions.APIException('Error heartbeating service', internal_details=str(e))

        # Check for possible errors in response
        if response.status_code == 400:
            raise exceptions.ValidationException('Bad request to service registry',
                                                 internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 401:
            raise exceptions.AuthenticationException('Unauthorized service heartbeat: token is not valid',
                                                     internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 404:
            raise exceptions.NotFoundException('Bad Service Discovery URL',
                                               internal_details=response.text)
        elif response.status_code == 410:
            raise exceptions.ResourceGoneException('Service instance not found',
                                                   internal_details=json.loads(response.text).get('Error'))

        # Add heartbeat to list
        heartbeat_time = time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime())
        self.heartbeats.append(heartbeat_time)
        return heartbeat_time

    def _heartbeater(self, interval):
        """
        Handles the service heartbeat

        :param: interval    Time lapse (sec) between heartbeats
        """
        self.beating = True
        while self.beating:
            time.sleep(interval)
            self.heartbeat_service()

    def get_last_heartbeat(self):
        """
        Returns the datetime of the last heartbeat

        :return:    Datetime string of the last service heartbeat
        """
        if len(self.heartbeats) > 0:
            return self.heartbeats[-1]
        else:
            return ''

    def deregister_service(self):
        """
        De-register the service with Service Discovery
        """

        # Stop the heartbeats
        if self.beating:
            self.beating = False
            self.heartbeat_thread.join()
            self.heartbeats = []

        # Call Service Discovery /instances/XXX to re-register the service
        try:
            response = request("DELETE",
                               '%s/api/v1/instances/%s' % (self.url, self.id),
                               headers={'Authorization': 'Bearer %s' % self.token})
        except Exception as e:
            raise exceptions.APIException('Error de-registering service', internal_details=str(e))

        # Check for possible errors in response
        if response.status_code == 400:
            raise exceptions.ValidationException('Bad request to service registry',
                                                 internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 401:
            raise exceptions.AuthenticationException('Unauthorized service de-registration: token is not valid',
                                                     internal_details=json.loads(response.text).get('Error'))
        elif response.status_code == 404:
            raise exceptions.NotFoundException('Bad Service Discovery URL',
                                               internal_details=response.text)
        elif response.status_code == 410:
            raise exceptions.ResourceGoneException('Service instance not found',
                                                   internal_details=json.loads(response.text).get('Error'))

        self.registered = False

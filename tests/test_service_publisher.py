import unittest
from types import StringType
from json import loads
from os import environ as env
from bluemix_service_discovery.service_publisher import ServicePublisher, exceptions


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(RegisterServiceTestCase('test_register_service_success'))
    test_suite.addTest(RegisterServiceTestCase('test_register_service_invalid_input'))
    test_suite.addTest(HeartbeatServiceTestCase('test_heartbeat_service_success'))
    test_suite.addTest(HeartbeatServiceTestCase('test_heartbeating_success'))
    test_suite.addTest(HeartbeatServiceTestCase('test_heartbeat_service_unregistered_publisher'))
    test_suite.addTest(HeartbeatServiceTestCase('test_get_last_heartbeat_success'))
    test_suite.addTest(DeregisterServiceTestCase('test_deregister_service_success'))
    return test_suite


###########################
#        Unit Tests       #
###########################

class RegisterServiceTestCase(unittest.TestCase):
    """Tests for `ServicePublisher.register_service()."""

    def setUp(self):
        self.service_name = 'lw-test'
        self.endpoint = 'https://logistics-wizard-test.mybluemix.net'

    def test_register_service_success(self):
        """With correct values, is the service registered?"""

        # Register service
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        service = publisher.register_service(False)

        # Check that the service was successfully registered
        self.assertTrue(publisher.registered)
        service_json = loads(service)
        self.assertTrue(service_json.get('id'))
        self.assertEqual(service_json.get('ttl'), 300)
        if service_json.get('links'):
            self.assertTrue(service_json.get('links').get('self'))
            self.assertTrue(service_json.get('links').get('heartbeat'))

        # De-register service
        publisher.deregister_service()

    def test_register_service_invalid_input(self):
        """With invalid inputs, is correct error thrown?"""

        # No auth token
        self.assertRaises(Exception, ServicePublisher,
                          self.service_name, 300, 'UP', self.endpoint, 'http')

        # Invalid status
        publisher = ServicePublisher(self.service_name, 300, 'UPPER', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.assertRaises(exceptions.ValidationException, publisher.register_service, False)
        self.assertFalse(publisher.registered)

        # Invalid protocol
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'odb',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.assertRaises(exceptions.ValidationException, publisher.register_service, False)
        self.assertFalse(publisher.registered)

        # Invalid Service Discover URL
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'odb',
                                     url='https://invalid-sd-url.ng.bluemix.net', auth_token='ABC123')
        self.assertRaises(exceptions.NotFoundException, publisher.register_service, False)
        self.assertFalse(publisher.registered)

        # Invalid Service Discover auth token
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'odb',
                                     url=env['SD_URL'], auth_token='ABC123')
        self.assertRaises(exceptions.AuthenticationException, publisher.register_service, False)
        self.assertFalse(publisher.registered)


class HeartbeatServiceTestCase(unittest.TestCase):
    """Tests for ServicePublisher.heartbeat_service()."""

    def setUp(self):
        self.service_name = 'lw-test'
        self.endpoint = 'https://logistics-wizard-test.mybluemix.net'

    def test_heartbeat_service_success(self):
        """With correct values, is the service heartbeated?"""
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        publisher.register_service(False)
        self.assertIsInstance(publisher.heartbeat_service(), StringType)
        publisher.deregister_service()

    def test_heartbeating_success(self):
        """With correct values, does the heartbeating process complete?"""
        import time
        publisher = ServicePublisher(self.service_name, 30, 'UP', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        publisher.register_service(True)
        time.sleep(2)
        publisher.deregister_service()

    def test_heartbeat_service_unregistered_publisher(self):
        """With invalid inputs, is correct error thrown?"""

        # Attempt to heartbeat a non-registered publisher
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.assertRaises(Exception, publisher.heartbeat_service)

    def test_get_last_heartbeat_success(self):
        """With invalid inputs, is correct error thrown?"""

        # Attempt to heartbeat a non-registered publisher
        publisher = ServicePublisher(self.service_name, 300, 'UP', self.endpoint, 'http',
                                     url=env['SD_URL'], auth_token=env['SD_AUTH'])
        publisher.register_service(False)
        self.assertEqual(publisher.get_last_heartbeat(), '')
        heartbeat_time = publisher.heartbeat_service()
        self.assertEqual(publisher.get_last_heartbeat(), heartbeat_time)
        publisher.deregister_service()


class DeregisterServiceTestCase(unittest.TestCase):
    """Tests for ServicePublisher.deregister_service()."""

    def setUp(self):
        self.publisher = ServicePublisher('lw-test', 300, 'UP', 'https://logistics-wizard-test.mybluemix.net', 'http',
                                          url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.publisher.register_service(False)

    def test_deregister_service_success(self):
        """With correct values, is the service deregistered?"""
        self.assertTrue(self.publisher.deregister_service() is None)

if __name__ == '__main__':
    unittest.main()

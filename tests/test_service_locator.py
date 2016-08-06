import unittest
from json import loads
from os import environ as env
from bluemix_service_discovery import exceptions
from bluemix_service_discovery.service_publisher import ServicePublisher
from bluemix_service_discovery.service_locator import ServiceLocator


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(GetServicesTestCase('test_get_services_success'))
    test_suite.addTest(GetServicesTestCase('test_get_services_filter_success'))
    test_suite.addTest(GetServicesTestCase('test_get_services_invalid_input'))
    return test_suite


###########################
#        Unit Tests       #
###########################

class GetServicesTestCase(unittest.TestCase):
    """Tests for ServiceLocator.get_services()."""

    def setUp(self):
        # Register two services
        self.publisher_1 = ServicePublisher('lw-test1', 300, 'UP',
                                            'https://logistics-wizard-test1.mybluemix.net', 'http',
                                            tags=['lw-test'], url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.publisher_1.register_service(False)
        self.publisher_2 = ServicePublisher('lw-test2', 300, 'UP',
                                            'https://logistics-wizard-test2.mybluemix.net', 'http',
                                            tags=['lw-test', 'db'], url=env['SD_URL'], auth_token=env['SD_AUTH'])
        self.publisher_2.register_service(False)

    def test_get_services_success(self):
        """With correct values, is the service deregistered?"""
        locator = ServiceLocator(env['SD_URL'], env['SD_AUTH'])
        services = loads(locator.get_services()).get('instances')

        for instance in services:
            self.assertTrue(instance.get('id'))
            self.assertTrue(instance.get('service_name'))
            self.assertTrue(instance.get('ttl'))
            self.assertTrue(instance.get('status'))
            self.assertTrue(instance.get('endpoint').get('type'))
            self.assertTrue(instance.get('endpoint').get('value'))

    def test_get_services_filter_success(self):
        """Are correct services returned?"""

        # Test the 'fields' filter
        locator = ServiceLocator(env['SD_URL'], env['SD_AUTH'])
        services = loads(locator.get_services(fields='id,service_name')).get('instances')
        for instance in services:
            self.assertTrue(instance.get('id'))
            self.assertTrue(instance.get('service_name'))
            self.assertTrue(instance.get('status') is None)

        # Test the 'tags' filter
        services = loads(locator.get_services(tags='lw-test')).get('instances')
        service_ids = [self.publisher_1.id, self.publisher_2.id]
        for instance in services:
            self.assertIn(instance.get('id'), service_ids)

        # Test the 'service_name' filter
        services = loads(locator.get_services(service_name='lw-test1')).get('instances')
        for instance in services:
            self.assertEqual(instance.get('id'), self.publisher_1.id)

        # Test the 'status' filter
        services = loads(locator.get_services(status='UP')).get('instances')
        for instance in services:
            self.assertEqual(instance.get('status'), 'UP')

    def test_get_services_invalid_input(self):
        """With invalid filters, is correct error thrown?"""

        # Attempt to retrieve services with invalid 'fields' filter
        locator = ServiceLocator(env['SD_URL'], env['SD_AUTH'])
        self.assertRaises(exceptions.ValidationException, locator.get_services, fields='dummy')

        # Attempt to retrieve services with invalid URL
        locator = ServiceLocator('https://invalid-sd-url.ng.bluemix.net', env['SD_AUTH'])
        self.assertRaises(exceptions.NotFoundException, locator.get_services)

        # Attempt to retrieve services with invalid auth
        locator = ServiceLocator(env['SD_URL'], 'ABC123')
        self.assertRaises(exceptions.AuthenticationException, locator.get_services)

    def tearDown(self):
        # De-register service
        self.publisher_1.deregister_service()
        self.publisher_2.deregister_service()

if __name__ == '__main__':
    unittest.main()

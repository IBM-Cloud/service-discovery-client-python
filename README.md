# Overview

[![Build Status](https://travis-ci.org/IBM-Bluemix/service-discovery-client-python.svg?branch=master)](https://travis-ci.org/IBM-Bluemix/service-discovery-client-python)

This is the source code for bluemix-service-discovery, a pip package that serves as a client to Python apps attempting to interact with the Bluemix Service Discovery service.

## How To Use

1. Open a terminal and run

   ```bash
   pip install bluemix-service-discovery
   ```
2. Import the package wherever you want to register your service or lookup a service in the registry.

    ```python
    from bluemix_service_discovery.service_publisher import ServicePublisher
    publisher = ServicePublisher('test-service', 300, 'UP',
                                 'https://test-service.mybluemix.net', 'http',
                                 tags=['test'])
	```

    ```python
    import json
    from bluemix_service_discovery.service_locator import ServiceLocator
    services = json.loads(locator.get_services()).get('instances')
    ```
	
	

## Example app

To see how to use this client in your app please check out the [Logistics Wizard](https://github.com/IBM-Bluemix/logistics-wizard) demo. You will want to pay attention to [server/web/\_\_init\_\_.py](https://github.com/IBM-Bluemix/logistics-wizard/blob/master/server/web/__init__.py) for a service registration and [server/utils.py](https://github.com/IBM-Bluemix/logistics-wizard/blob/master/server/utils.py) for a service lookup example.

## More Info
[Service Discovery](https://console.ng.bluemix.net/catalog/services/service-discovery/)  
[Documentation](https://console.ng.bluemix.net/docs/services/ServiceDiscovery/index.html)


## License

See [License.txt](License.txt) for license information.

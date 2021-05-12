# Authentication
The python-sdk-core project supports the following types of authentication:
- Basic Authentication
- Bearer Token
- Identity and Access Management (IAM)
- Cloud Pak for Data
- No Authentication

The SDK user configures the appropriate type of authentication for use with service instances.
The authentication types that are appropriate for a particular service may vary from service to service, so it is important for the SDK user to consult with the appropriate service documentation to understand which authenticators are supported for that service.

The python-sdk-core allows an authenticator to be specified in one of two ways:
1. programmatically - the SDK user invokes the appropriate constructor to create an instance of the desired authenticator and then passes the authenticator instance when constructing an instance of the service.
2. configuration - the SDK user provides external configuration information (in the form of environment variables or a credentials file) to indicate the type of authenticator along with the configuration of the necessary properties for that authenticator.  The SDK user then invokes the configuration-based authenticator factory to construct an instance of the authenticator that is described in the external configuration information.

The sections below will provide detailed information for each authenticator
which will include the following:
- A description of the authenticator
- The properties associated with the authenticator
- An example of how to construct the authenticator programmatically
- An example of how to configure the authenticator through the use of external
configuration information.  The configuration examples below will use
environment variables, although the same properties could be specified in a
credentials file instead.

## Basic Authentication
The `BasicAuthenticator` is used to add Basic Authentication information to
each outbound request in the `Authorization` header in the form:
```
   Authorization: Basic <encoded username and password>
```
### Properties
- username: (required) the basic auth username
- password: (required) the basic auth password
### Programming example
```python
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator

authenticator = BasicAuthenticator(<your_username>, <your_password>)
service = ExampleService(authenticator=authenticator)
```
### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=basic
export EXAMPLE_SERVICE_USERNAME=myuser
export EXAMPLE_SERVICE_PASSWORD=mypassword
```
Application code:
```python
from ibm_cloud_sdk_core import get_authenticator_from_environment

authenticator = get_authenticator_from_environment('example_service')
service = ExampleService(authenticator=authenticator)
```

## Bearer Token Authentication
The `BearerTokenAuthenticator` will add a user-supplied bearer token to
each outbound request in the `Authorization` header in the form:
```
    Authorization: Bearer <bearer-token>
```
### Properties
- bearerToken: (required) the bearer token value
### Programming example
```python
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator

authenticator = BearerTokenAuthenticator(<your_bearer_token>)
service = ExampleService(authenticator=authenticator)

# after getting a new access token...
service.get_authenticator().set_bearer_token('54321');
```
### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=bearertoken
export EXAMPLE_SERVICE_BEARER_TOKEN=<the bearer token value>
```
Application code:
```python
from ibm_cloud_sdk_core import get_authenticator_from_environment

authenticator = get_authenticator_from_environment('example_service')
service = ExampleService(authenticator=authenticator)

# after getting a new access token...
service.get_authenticator().set_bearer_token('54321');
```
Note that the use of external configuration is not as useful with the `BearerTokenAuthenticator` as it
is for other authenticator types because bearer tokens typically need to be obtained and refreshed
programmatically since they normally have a relatively short lifespan before they expire.  This
authenticator type is intended for situations in which the application will be managing the bearer
token itself in terms of initial acquisition and refreshing as needed.

## Identity and Access Management Authentication (IAM)
The `IamAuthenticator` will accept a user-supplied api key and will perform
the necessary interactions with the IAM token service to obtain a suitable
bearer token for the specified api key.  The authenticator will also obtain
a new bearer token when the current token expires.  The bearer token is
then added to each outbound request in the `Authorization` header in the
form:
```
   Authorization: Bearer <bearer-token>
```
### Properties
- apikey: (required) the IAM api key.
- url: (optional) The URL representing the IAM token service endpoint.  If not specified, a suitable
default value is used.
- client_id/client_secret: (optional) The `clientId` and `clientSecret` fields are used to form a
"basic auth" Authorization header for interactions with the IAM token server. If neither field
is specified, then no Authorization header will be sent with token server requests.  These fields
are optional, but must be specified together.
- disable_ssl_verification: (optional) A flag that indicates whether verification of the server's SSL
certificate should be disabled or not. The default value is `false`.
- headers: (optional) A set of key/value pairs that will be sent as HTTP headers in requests made to the IAM token service.
### Programming example
```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('my_apikey')
authenticator.set_client_id_and_secret('my-client-id', 'my-client-secret');
service = ExampleService(authenticator=authenticator)

service.get_authenticator.set_disable_ssl_verification(true);
```
### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=iam
export EXAMPLE_SERVICE_APIKEY=myapikey
```
Application code:
```python
from ibm_cloud_sdk_core import get_authenticator_from_environment

authenticator = get_authenticator_from_environment('example_service')
service = ExampleService(authenticator=authenticator)
```

##  Cloud Pak for Data
The `CloudPakForDataAuthenticator` will accept a user-supplied username and either a password or an apikey value, and will
perform the necessary interactions with the Cloud Pak for Data token service to obtain a suitable
bearer token.  The authenticator will also obtain a new bearer token when the current token expires.
The bearer token is then added to each outbound request in the `Authorization` header in the
form:
```
   Authorization: Bearer <bearer-token>
```
### Properties
- username: (required) the username used to obtain a bearer token.
- password: (required if apikey is not specified) the password used to obtain a bearer token.
- url: (required) The URL representing the Cloud Pak for Data token service endpoint.
- apikey: (required if password is not specified) the apikey used to obtain a bearer token.
- disableSSLVerification: (optional) A flag that indicates whether verificaton of the server's SSL
certificate should be disabled or not. The default value is `false`.
- headers: (optional) A set of key/value pairs that will be sent as HTTP headers in requests
made to the IAM token service.
### Programming example
```python
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator

# Username / password authentication
authenticator = CloudPakForDataAuthenticator(
                 username='my_username',
                 password='my_password',
                 url='https://my-cp4d-url',
                 disable_ssl_verification=True)

# Username / apikey authentication
authenticator = CloudPakForDataAuthenticator(
                 username='my_username',
                 apikey='my_apikey',
                 url='https://my-cp4d-url',
                 disable_ssl_verification=True)

service = ExampleService(authenticator=authenticator)

service.get_authenticator().set_headers({'dummy': 'headers'})
```
### Configuration example
External configuration:
```
# Username / password authentication
export EXAMPLE_SERVICE_AUTH_TYPE=cp4d
export EXAMPLE_SERVICE_USERNAME=myuser
export EXAMPLE_SERVICE_PASSWORD=mypassword
export EXAMPLE_SERVICE_URL=https://mycp4dhost.com/

# Username / apikey authentication
export EXAMPLE_SERVICE_AUTH_TYPE=cp4d
export EXAMPLE_SERVICE_USERNAME=myuser
export EXAMPLE_SERVICE_APIKEY=myapikey
export EXAMPLE_SERVICE_URL=https://mycp4dhost.com/
```
Application code:
```python
from ibm_cloud_sdk_core import get_authenticator_from_environment

authenticator = get_authenticator_from_environment('example_service')
service = ExampleService(authenticator=authenticator)
```

## No Auth Authentication
The `NoAuthAuthenticator` is a placeholder authenticator which performs no actual authentication function.   It can be used in situations where authentication needs to be bypassed, perhaps while developing or debugging an application or service.
### Properties
None
### Programming example
```python
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator

authenticator = NoAuthAuthenticator()
service = ExampleService(authenticator=authenticator)
```
### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=noauth
```
Application code:
```python
from ibm_cloud_sdk_core import get_authenticator_from_environment

authenticator = get_authenticator_from_environment('example_service')
service = ExampleService(authenticator=authenticator)
```
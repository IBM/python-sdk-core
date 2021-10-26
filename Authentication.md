# Authentication
The python-sdk-core project supports the following types of authentication:
- Basic Authentication
- Bearer Token Authentication
- Identity and Access Management (IAM) Authentication
- VPC Instance Authentication
- Container Authentication
- Cloud Pak for Data Authentication
- No Authentication

The SDK user configures the appropriate type of authentication for use with service instances.
The authentication types that are appropriate for a particular service may vary from service to service,
so it is important for the SDK user to consult with the appropriate service documentation
to understand which authenticators are supported for that service.

The python-sdk-core allows an authenticator to be specified in one of two ways:
1. programmatically - the SDK user invokes the appropriate function(s) to create an instance of the
desired authenticator and then passes the authenticator instance when constructing an instance of the service.
2. configuration - the SDK user provides external configuration information (in the form of environment variables
or a credentials file) to indicate the type of authenticator, along with the configuration of the necessary properties for that authenticator. The SDK user then invokes the configuration-based service client constructor method to construct an instance of the authenticator and service client that reflect the external configuration information.

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
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = BasicAuthenticator(<your_username>, <your_password>)

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
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
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
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
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = BearerTokenAuthenticator(<your_bearer_token>)

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
...
# Later, if your bearer token value expires, you can set a new one like this:
new_token = '<new token>'
authenticator.set_bearer_token(new_token);
```

### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=bearertoken
export EXAMPLE_SERVICE_BEARER_TOKEN=<the bearer token value>
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
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

- apikey: (required) the IAM api key

- url: (optional) The base endpoint URL of the IAM token service.
The default value of this property is the "prod" IAM token service endpoint
(`https://iam.cloud.ibm.com`).
Make sure that you use an IAM token service endpoint that is appropriate for the
location of the service being used by your application.
For example, if you are using an instance of a service in the "production" environment
(e.g. `https://resource-controller.cloud.ibm.com`),
then the default "prod" IAM token service endpoint should suffice.
However, if your application is using an instance of a service in the "staging" environment
(e.g. `https://resource-controller.test.cloud.ibm.com`),
then you would also need to configure the authenticator to use the IAM token service "staging"
endpoint as well (`https://iam.test.cloud.ibm.com`).

- client_id/client_secret: (optional) The `client_id` and `client_secret` fields are used to form a
"basic auth" Authorization header for interactions with the IAM token server. If neither field
is specified, then no Authorization header will be sent with token server requests.  These fields
are optional, but must be specified together.

- scope: (optional) the scope to be associated with the IAM access token.
If not specified, then no scope will be associated with the access token.

- disable_ssl_verification: (optional) A flag that indicates whether verification of the server's SSL
certificate should be disabled or not. The default value is `false`.

- headers: (optional) A set of key/value pairs that will be sent as HTTP headers in requests made to the IAM token service.

### Programming example
```python
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = IAMAuthenticator('myapikey')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
```

### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=iam
export EXAMPLE_SERVICE_APIKEY=myapikey
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
```


## Container
The `ContainerAuthenticator` is intended to be used by application code
running inside a compute resource managed by the IBM Kubernetes Service (IKS)
in which a secure compute resource token (CR token) has been stored in a file
within the compute resource's local file system.
The CR token is similar to an IAM apikey except that it is managed automatically by
the compute resource provider (IKS).
This allows the application developer to:
- avoid storing credentials in application code, configuraton files or a password vault
- avoid managing or rotating credentials

The `ContainerAuthenticator` will retrieve the CR token from
the compute resource in which the application is running, and will then perform
the necessary interactions with the IAM token service to obtain an IAM access token
using the IAM "get token" operation with grant-type `cr-token`.
The authenticator will repeat these steps to obtain a new IAM access token when the
current access token expires.
The IAM access token is added to each outbound request in the `Authorization` header in the form:
```
   Authorization: Bearer <IAM-access-token>
```

### Properties

- cr_token_filename: (optional) The name of the file containing the injected CR token value.
If not specified, then `/var/run/secrets/tokens/vault-token` is used as the default value.
The application must have `read` permissions on the file containing the CR token value.

- iam_profile_name: (optional) The name of the linked trusted IAM profile to be used when obtaining the
IAM access token (a CR token might map to multiple IAM profiles).
One of `iam_profile_name` or `iam_profile_id` must be specified.

- iam_profile_id: (optional) The ID of the linked trusted IAM profile to be used when obtaining the
IAM access token (a CR token might map to multiple IAM profiles).
One of `iam_profile_name` or `iam_profile_id` must be specified.

- url: (optional) The base endpoint URL of the IAM token service.
The default value of this property is the "prod" IAM token service endpoint
(`https://iam.cloud.ibm.com`).
Make sure that you use an IAM token service endpoint that is appropriate for the
location of the service being used by your application.
For example, if you are using an instance of a service in the "production" environment
(e.g. `https://resource-controller.cloud.ibm.com`),
then the default "prod" IAM token service endpoint should suffice.
However, if your application is using an instance of a service in the "staging" environment
(e.g. `https://resource-controller.test.cloud.ibm.com`),
then you would also need to configure the authenticator to use the IAM token service "staging"
endpoint as well (`https://iam.test.cloud.ibm.com`).

- client_id/client_secret: (optional) The `client_id` and `client_secret` fields are used to form a
"basic auth" Authorization header for interactions with the IAM token server. If neither field
is specified, then no Authorization header will be sent with token server requests.  These fields
are optional, but must be specified together.

- scope (optional): the scope to be associated with the IAM access token.
If not specified, then no scope will be associated with the access token.

- disable_ssl_verification: (optional) A flag that indicates whether verification of the server's SSL
certificate should be disabled or not. The default value is `False`.

- proxies (optional): The proxy endpoint to use for HTTP(S) requests.

- headers: (optional) A set of key/value pairs that will be sent as HTTP headers in requests
made to the IAM token service.

### Programming example
```python
from ibm_cloud_sdk_core.authenticators import ContainerAuthenticatior
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = ContainerAuthenticator(iam_profile_name='iam-user-123')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
```

### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=container
export EXAMPLE_SERVICE_IAM_PROFILE_NAME=iam-user-123
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
```


## VPC Instance Authentication
The `VpcInstanceAuthenticator` is intended to be used by application code
running inside a VPC-managed compute resource (virtual server instance) that has been configured
to use the "compute resource identity" feature.
The compute resource identity feature allows you to assign a trusted IAM profile to the compute resource as its "identity".
This, in turn, allows applications running within the compute resource to take on this identity when interacting with
IAM-secured IBM Cloud services.
This results in a simplified security model that allows the application developer to:
- avoid storing credentials in application code, configuraton files or a password vault
- avoid managing or rotating credentials

The `VpcInstanceAuthenticator` will invoke the appropriate operations on the compute resource's locally-available
VPC Instance Metadata Service to (1) retrieve an instance identity token
and then (2) exchange that instance identity token for an IAM access token.
The authenticator will repeat these steps to obtain a new IAM access token whenever the current access token expires.
The IAM access token is added to each outbound request in the `Authorization` header in the form:
```
   Authorization: Bearer <IAM-access-token>
```

### Properties

- iam_profile_crn: (optional) the crn of the linked trusted IAM profile to be used when obtaining the IAM access token.

- iam_profile_id: (optional) the id of the linked trusted IAM profile to be used when obtaining the IAM access token.

- url: (optional) The VPC Instance Metadata Service's base URL.  
The default value of this property is `http://169.254.169.254`, and should not need to be specified in normal situations.

Usage Notes:
1. At most one of `iam_profile_crn` or `iam_profile_id` may be specified.  The specified value must map
to a trusted IAM profile that has been linked to the compute resource (virtual server instance).

2. If both `iam_profile_crn` and `iam_profile_id` are specified, then an error occurs.

3. If neither `iam_profile_crn` nor `iam_profile_id` are specified, then the default trusted profile linked to the compute resource will be used to perform the IAM token exchange.
If no default trusted profile is defined for the compute resource, then an error occurs.


### Programming example
```python
from ibm_cloud_sdk_core.authenticators import VPCInstanceAuthenticator
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator.
authenticator = VPCInstanceAuthenticator(iam_profile_crn='crn:iam-profile-123')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
```

### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=vpc
export EXAMPLE_SERVICE_IAM_PROFILE_CRN=crn:iam-profile-123
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
```


##  Cloud Pak for Data
The `CloudPakForDataAuthenticator` will accept a user-supplied username value, along with either a
password or apikey, and will 
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

- apikey: (required if password is not specified) the apikey used to obtain a bearer token.

- url: (required) The URL representing the Cloud Pak for Data token service endpoint's base URL string.
This value should not include the `/v1/authorize` path portion.

- disable_ssl_verification: (optional) A flag that indicates whether verification of the server's SSL
certificate should be disabled or not. The default value is `false`.

- headers: (optional) A set of key/value pairs that will be sent as HTTP headers in requests
made to the Cloud Pak for Data token service.

### Programming example
```python
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator using username/apikey.
authenticator = CloudPakForDataAuthenticator(username='myuser', apikey='myapikey', url='https://mycp4dhost.com')

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
```

### Configuration example
External configuration:
```
# Configure "example_service" with username/apikey.
export EXAMPLE_SERVICE_AUTH_TYPE=cp4d
export EXAMPLE_SERVICE_USERNAME=myuser
export EXAMPLE_SERVICE_PASSWORD=myapikey
export EXAMPLE_SERVICE_URL=https://mycp4dhost.com
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.
```

## No Auth Authentication
The `NoAuthAuthenticator` is a placeholder authenticator which performs no actual authentication function.
It can be used in situations where authentication needs to be bypassed, perhaps while developing
or debugging an application or service.

### Properties
None

### Programming example
```python
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
from <sdk-package-name>.example_service_v1 import *

# Create the authenticator using username/apikey.
authenticator = NoAuthAuthenticator()

# Construct the service instance.
service = ExampleServiceV1(authenticator=authenticator)

# 'service' can now be used to invoke operations.
```

### Configuration example
External configuration:
```
export EXAMPLE_SERVICE_AUTH_TYPE=noauth
```
Application code:
```python
from <sdk-package-name>.example_service_v1 import *

# Construct the service instance.
service = ExampleServiceV1.new_instance(service_name='example_service')

# 'service' can now be used to invoke operations.

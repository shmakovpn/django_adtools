  .. code-block:: python

   # DJANGO_ADTOOLS
   ADTOOLS_DOMAIN: str = 'example.com'  #: name of a windows domain
   # set list of dns servers if your server work under Windows
   # ADTOOLS_NAMESERVERS: List[str] = ['127.0.0.1']  #: list of dns servers to discover ip addresses of domain controllers
   ADTOOLS_TEST_USERNAME: str = 'test@example.com'  #: test ad username
   ADTOOLS_TEST_PASSWORD: str = 'somepassword'  #: test ad password
   ADTOOLS_TEST_GROUP: str = 'test-users'  #: test ad group
# project title --> E-Commerce Product API
Build a production-ready product and order REST API. It 
must use JWT authentication (access + refresh tokens), object-level permissions so 
users can only modify their own orders, DjangoFilterBackend and SearchFilter 
for product filtering and search, PageNumberPagination on all list endpoints, throttling 
for anonymous users, at least one custom @action on the orders ViewSet (e.g. a 
cancel action), CORS configured for a frontend origin, and auto-generated Swagger 
documentation via drf-spectacular.
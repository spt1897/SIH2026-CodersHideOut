## This is the core infra setup for all FastAPI microservices  
  
**The features include:**  

1) It handles server initialization/deinitialization.  
2) Connecting to database, cache and eureka servers  
3) Safe quering to database and redis guarded by retries and errorhandling and rollbacks  
4) Manages and tracks server health, DB-redis connections, and active/total requests and clients being processed.  
5) Handles file receiving/uploading via formdata/ws in memory or file storage.  
6) Verifies JWT token for requests.  
7) Seperate process pool for cpu extensive tasks without blocking event loop.  

**This core/ can be added to any microservice and it shall be setup , we can focus only on the service itself.**

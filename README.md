POST /auto-builder/v1/builds
Description: Builds a Docker image from the specified Git repository.

POST /auto-builder/v1/config-maps
Description: Creates a new ConfigMap for deployment.

PUT /auto-builder/v1/config-maps/:id
Description: Updates an existing ConfigMap for deployment.

PATCH /auto-builder/v1/config-maps/:id
Description: Partially updates an existing ConfigMap for deployment.

DELETE /auto-builder/v1/config-maps/:id
Description: Deletes an existing ConfigMap for deployment.

POST /auto-builder/v1/backend-configs
Description: Adds a new backend configuration for the specified service.

PUT /auto-builder/v1/backend-configs/:id
Description: Updates an existing backend configuration for the specified service.

PATCH /auto-builder/v1/backend-configs/:id
Description: Partially updates an existing backend configuration for the specified service.

DELETE /auto-builder/v1/backend-configs/:id
Description: Deletes an existing backend configuration for the specified service.

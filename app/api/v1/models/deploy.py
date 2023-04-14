from pydantic import BaseModel


class Deploy(BaseModel):
    # deployment_name: str
    # port_number: str
    cluster_name: str
    # image_name: str
    website_name: str
    rewrite_service_type: str = "ClusterIP"
    main_service_type: str = "ClusterIP"
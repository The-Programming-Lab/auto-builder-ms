from fastapi import APIRouter
from app.core.config import BASE_PATH
from app.api.v1.endpoints import build, deploy, create



router = APIRouter(prefix=BASE_PATH)

router.include_router(build.router)
router.include_router(deploy.router)
router.include_router(create.router)
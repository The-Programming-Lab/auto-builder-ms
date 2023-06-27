from fastapi import APIRouter
import os

from app.api.v1.endpoints import build, deploy, create

router = APIRouter(prefix=os.getenv("BASE_PATH")) # type: ignore

router.include_router(build.router)
router.include_router(deploy.router)
router.include_router(create.router)
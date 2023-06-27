import hashlib
import base64
import subprocess
from fastapi import HTTPException

from app.core.logging import logger


def encoded_string(user_id: str) -> str:
    user_id_bytes = user_id.encode('utf-8')
    hashed_id = hashlib.sha256(user_id_bytes).hexdigest()
    return hashed_id[:50].lower()  # take the first 50 characters


def run_command(command: str, stdout=None) -> None:
    try:
        result = subprocess.run(command, shell=True, capture_output=stdout==None, text=True, stdout=stdout, stderr=stdout)
        if stdout == None:
            logger.info(result.stderr.strip())
    except Exception as e:
        logger.error(e)

def run_command_HTTP_exception(command: str, exception: HTTPException, stdout=None) -> None:
    try:
        result = subprocess.run(command, shell=True, capture_output=stdout==None, text=True, stdout=stdout, stderr=stdout)
        if stdout == None:
            logger.info(result.stderr.strip())
    except Exception as e:
        logger.error(e)
        raise exception

import logging

logging.basicConfig(
    level=logging.DEBUG,
    # '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    format='%(levelname)s - %(filename)s:%(lineno)d - %(message)s'

)

logger = logging.getLogger(__name__)

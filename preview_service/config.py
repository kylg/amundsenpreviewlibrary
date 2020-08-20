import os

PREVIEW_FILE_REPO = 'PREVIEW_FILE_REPO'

class Config:
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:'\
                 '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'

    # Path to the logging configuration file to be used by `fileConfig()` method
    # https://docs.python.org/3.7/library/logging.config.html#logging.config.fileConfig
    # LOG_CONFIG_FILE = 'search_service/logging.conf'
    LOG_CONFIG_FILE = None

    SWAGGER_ENABLED = False


class LocalConfig(Config):
    DEBUG = False
    TESTING = False
    STATS = False
    PREVIEW_FILE_REPO = os.environ.get('PREVIEW_FILE_REPO', f'/var/amundsen/preview_data')
    SWAGGER_ENABLED = True
    SWAGGER_TEMPLATE_PATH = os.path.join('api', 'swagger_doc', 'template.yml')
    SWAGGER = {
        'openapi': '3.0.2',
        'title': 'Preview Service',
        'uiversion': 3
    }

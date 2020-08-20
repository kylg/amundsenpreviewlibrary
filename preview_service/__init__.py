import ast
import importlib
import os
import logging
import logging.config
import sys

from flask import Flask, Blueprint
from flask_restful import Api
from flask_cors import CORS
from typing import Dict, Any  # noqa: F401
from flasgger import Swagger


from preview_service.api.healthcheck import healthcheck
from preview_service.api.preview_data import PreviewDataAPI



# For customized flask use below arguments to override.
FLASK_APP_MODULE_NAME = os.getenv('FLASK_APP_MODULE_NAME')
FLASK_APP_CLASS_NAME = os.getenv('FLASK_APP_CLASS_NAME')
FLASK_APP_KWARGS_DICT_STR = os.getenv('FLASK_APP_KWARGS_DICT')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Environment Variable to enable cors
CORS_ENABLED = os.environ.get('CORS_ENABLED', False)


def create_app(*, config_module_class: str) -> Flask:
    """
    Creates app in function so that flask with flask extensions can be
    initialized with specific config. Here it defines the route of APIs
    so that it can be seen in one place where implementation is separated.

    Config is being fetched via module.class name where module.class name
    can be passed through environment variable.
    This is to make config fetched through runtime PYTHON_PATH so that
    Config class can be easily injected.
    More on: http://flask.pocoo.org/docs/1.0/config/

    :param config_module_class: name of the config
    :return: Flask
    """
    if FLASK_APP_MODULE_NAME and FLASK_APP_CLASS_NAME:
        print(f'Using requested Flask module {FLASK_APP_MODULE_NAME} '
              f'and class {FLASK_APP_CLASS_NAME}', file=sys.stderr)
        class_obj = getattr(
            importlib.import_module(FLASK_APP_MODULE_NAME),
            FLASK_APP_CLASS_NAME
        )

        flask_kwargs_dict = {}  # type: Dict[str, Any]
        if FLASK_APP_KWARGS_DICT_STR:
            print(f'Using kwargs {FLASK_APP_KWARGS_DICT_STR} to instantiate Flask',
                  file=sys.stderr)
            flask_kwargs_dict = ast.literal_eval(FLASK_APP_KWARGS_DICT_STR)

        app = class_obj(__name__, **flask_kwargs_dict)

    else:
        from werkzeug.serving import WSGIRequestHandler
        WSGIRequestHandler.protocol_version = "HTTP/1.1"
        app = Flask(__name__)

    if CORS_ENABLED:
        CORS(app)
    config_module_class = \
        os.getenv('PREVIEW_SVC_CONFIG_MODULE_CLASS') or config_module_class
    app.config.from_object(config_module_class)

    if app.config.get('LOG_CONFIG_FILE'):
        logging.config.fileConfig(app.config.get('LOG_CONFIG_FILE'), disable_existing_loggers=False)
    else:
        logging.basicConfig(format=app.config.get('LOG_FORMAT'), datefmt=app.config.get('LOG_DATE_FORMAT'))
        logging.getLogger().setLevel(app.config.get('LOG_LEVEL'))

    logging.info('Creating app with config name {}'
                 .format(config_module_class))
    logging.info('Created app with config name {}'.format(config_module_class))

    app.config['UPLOAD_FOLDER'] = app.config['PREVIEW_FILE_REPO']
    api_bp = Blueprint('api', __name__)
    api_bp.add_url_rule('/healthcheck', 'healthcheck', healthcheck)
    api = Api(api_bp)
    # Preview Data API
    api.add_resource(PreviewDataAPI, '/preview_data')

    app.register_blueprint(api_bp)

    if app.config.get('SWAGGER_ENABLED'):
        Swagger(app, template_file=os.path.join(ROOT_DIR, app.config.get('SWAGGER_TEMPLATE_PATH')), parse=True)
    return app

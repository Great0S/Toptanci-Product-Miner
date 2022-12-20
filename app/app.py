from __future__ import absolute_import

import configparser
from logging import config

from celery import Celery, chord, group
from celery.signals import setup_logging
from flask import Flask
import telegram
from telegram.utils import request as telegram_request

group = group
chord = chord


# Logging config
log_config1 = {
    "version": 1,
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG"
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "formatter": "std_out",
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "mode": "a",
            "encoding": "utf-8",
            "filename": f"logs/{__name__}.log"
        }
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s %(levelname)s / Module: %(module)s / Function: %(funcName)s / Message: %(message)s / Line: %(lineno)d",
        }
    },
}


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "celeryTask": {
            "()": "celery.app.log.TaskFormatter",
            "fmt": "[%(asctime)s: %(levelname)s/%(processName)s] %(task_name)s[%(task_id)s]:%(module)s:%(funcName)s: %(name)s - %(message)s",
        },
        'default': {
            'format': '[%(asctime)s:%(levelname)s:%(name)s:%(threadName)s] %(message)s',
        },
        'base': {
            'format': '%(message)s'
        }
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "base",
            "level": "INFO",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "mode": "a",
            "encoding": "utf-8",
            "filename": f"logs/{__name__}.log",
            'maxBytes': 5000000,
            'backupCount': 30
        }
    },
    "loggers": {
        "mainLog": {
            "handlers": ["file"],
            "level": "INFO",
        }
    },
    'root': {
        'handlers': ["console"],
        'level': 'DEBUG',
    },
}


@setup_logging.connect
def config_logger(*args, **kwargs):
    config.dictConfig(log_config)


# Read credentials
Config = configparser.ConfigParser()
Config.read("config.ini")

# Assign values to internal variables
api_id = Config['Telegram']['api_id']
api_hash = Config['Telegram']['api_hash']
username = Config['Telegram']['username']
channel_id = Config['Telegram']['channel_id']
Target = Config['Telegram']['Target']
token = Config['Telegram']['KAtoken']

# Telegram client object
bot = telegram.Bot(
    token=token,  request=telegram_request.Request(read_timeout=120))


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=["app.tasks"]
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_RESULT_BACKEND="redis://localhost:6379",
    CELERY_BROKER_URL="redis://localhost:6379"
)

celery = make_celery(flask_app)

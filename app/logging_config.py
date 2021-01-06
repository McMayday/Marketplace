"""
Настройки логгера.
"""
import logging
from .read_config import *

LOGGER_LEVEL = os.environ.get('LOGGER_LEVEL', 'DEBUG')
TEST_MODE = os.environ.get('TEST_MODE', 'False') == 'True'

MAIN_LOGGER_NAME = PROJECT_NAME

AVAILABLE_LOGGER_LEVELS = [
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
]


def produce_logger(name):
    """
    Функция создания дочернего логгера приложения с определенным именем модуля логгера.
    """
    return logging.getLogger(f'{MAIN_LOGGER_NAME}.{name}')


def set_logger_level():
    """
    Принудительное задание уровня логгирования.

    В случае если принудительно уровень логгирования не задан
    то значение назанчаетсяв соответсвии с переменной  DEBUG_MODE
    """
    if LOGGER_LEVEL in AVAILABLE_LOGGER_LEVELS:
        return LOGGER_LEVEL
    return None


MANUAL_LOGGER_LEVEL = set_logger_level()

APP_LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s: [%(asctime)s.%(msecs)03d] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)s:  %(message)s'
        },
    },
    'handlers': {
        'console_info': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'console': {
            'level': MANUAL_LOGGER_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console_info'],
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
        'django.db': {
            'level': MANUAL_LOGGER_LEVEL,
            'handlers': ['console'] if not TEST_MODE else [],
            'propagate': False,
        },
        MAIN_LOGGER_NAME: {
            'level': MANUAL_LOGGER_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'django.template': {  # Для предотвращения отображения информационного сообщения
            'handlers': ['console'],  # django.template.base.VariableDoesNotExist: Failed lookup for key [name] in
            'level': 'INFO',  # <URLResolver <URLPattern list>
            'propagate': True,  # (admin:admin) 'super_admin/'>
        }
    },
}

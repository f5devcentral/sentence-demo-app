import os
import redis
import sys


class BaseConfig(object):
    # Get Env vars

    PREFIX = os.environ.get('PREFIX')
    if type(PREFIX) == type(None):
        PREFIX = ""

    NAMESPACE = os.environ.get('NAMESPACE')
    if type(NAMESPACE) == type(None):
        NAMESPACE = ""

    SITE_ENV = os.environ.get('SITE_ENV')
    if type(SITE_ENV) == type(None):
        SITE_ENV = ""

    SITE_ENV_MESSAGE = os.environ.get('SITE_ENV_MESSAGE')
    if type(SITE_ENV_MESSAGE) == type(None):
        SITE_ENV_MESSAGE = ""

    ADJECTIVES_URL = os.environ.get('ADJECTIVES_URL')
    if type(ADJECTIVES_URL) == type(None):
        ADJECTIVES_URL = ""

    ANIMALS_URL = os.environ.get('ANIMALS_URL')
    if type(ANIMALS_URL) == type(None):
        ANIMALS_URL = ""

    COLORS_URL = os.environ.get('COLORS_URL')
    if type(COLORS_URL) == type(None):
        COLORS_URL = ""

    LOCATIONS_URL = os.environ.get('LOCATIONS_URL')
    if type(LOCATIONS_URL) == type(None):
        LOCATIONS_URL = ""

    REDIS_HOST = os.environ.get('REDIS_HOST')
    if type(REDIS_HOST) == type(None):
        REDIS_HOST = ""

    REDIS_PORT = os.environ.get('REDIS_PORT')
    if type(REDIS_PORT) == type(None):
        REDIS_PORT = 6379

    REDIS_TTL = os.environ.get('REDIS_TTL')
    if type(REDIS_TTL) == type(None):
        REDIS_TTL = 1
    else:
        REDIS_TTL = int(REDIS_TTL)

    LOG_LEVEL = os.environ.get('LOG_LEVEL')
    if type(LOG_LEVEL) == type(None):
        LOG_LEVEL = "WARNING"


def redis_connect() -> redis.client.Redis:
    # try to connect to Redis cache
    try:
        client = redis.Redis(
            host=BaseConfig.REDIS_HOST,
            port=BaseConfig.REDIS_PORT,
            password="",
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)

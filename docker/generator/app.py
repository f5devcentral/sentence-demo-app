import logging
import requests
import json
from config import BaseConfig, redis_connect
from datetime import timedelta
from flask import Flask, request, abort
from random import randint


PREFIX = BaseConfig.PREFIX
NAMESPACE = BaseConfig.NAMESPACE
SITE_ENV = BaseConfig.SITE_ENV
SITE_ENV_MESSAGE = BaseConfig.SITE_ENV_MESSAGE
REDIS_TTL = BaseConfig.REDIS_TTL
LOG_LEVEL = BaseConfig.LOG_LEVEL
CACHE_ENABLED = bool(BaseConfig.REDIS_HOST)

# Map provided URL with service
BASE_URL_DICT = {"adjectives": BaseConfig.ADJECTIVES_URL, "animals": BaseConfig.ANIMALS_URL,
                 "colors": BaseConfig.COLORS_URL, "locations": BaseConfig.LOCATIONS_URL}

# Set Logging Level
logging.basicConfig(level=LOG_LEVEL)

# Init generator
generator = Flask(__name__)
# Check if REDIS service is specified
if CACHE_ENABLED:
    # Init Redis Client
    r = redis_connect()
    logging.info("Cache enabled from %s", r.client())
else:
    logging.info("Cache disabled")


@generator.get('/health')
def get_health():
    # Healthcheck endpoint
    return "health OK\n", 200


@generator.get('/api/sentence')
def get_sentence():
    # Route to get generated sentence
    logging.debug("GET request,\nPath: %s\nHeaders:\n%s",
                  str(request.path), str(request.headers))
    sentence_json = {}
    sentence = ""
    attributes_list = ['adjectives', 'animals', 'colors', 'locations']
    for attribute in attributes_list:
        words = get_words(attribute)
        words_size = len(words)
        logging.debug("words_size: %i ", words_size)
        if words_size == 0:  # error api_size
            sentence_json[attribute] = "null"
        else:
            logging.debug("Words from %s - %s", attribute, words)
            index = randint(0, words_size-1)
            logging.debug(index)
            name = words[index]['name']
            sentence_json[attribute] = name
            sentence = sentence + " " + name
    logging.info("Generated sentence:%s", sentence)

    response = {}
    response['sentence'] = sentence_json
    return response


@generator.get('/api/sentence/<any(adjectives, colors, animals, locations):service>')
def get_service(service=None):
    # Route to get all entries in a specific service
    logging.debug("GET request,\nPath: %s\nHeaders:\n%s",
                  str(request.path), str(request.headers))
    words = get_words(service)
    if len(words) == 0:
        words = "null"
    return {service: words}


@generator.post('/api/sentence/<any(adjectives, colors, animals, locations):service>')
def post_service(service=None):
    # Route to post a value to specific service
    post_data = request.get_json()
    response_content = post_data
    logging.debug("POST request,\nPath: %s\nHeaders:\n%s\nBody:\n%s\n",
                  request.path, request.headers, post_data)

    if "value" not in post_data:
        return abort(400)

    logging.info("POST %s to service %s requested",
                 post_data["value"], service)
    successful, info = post_word(service, post_data["value"])
    if successful:
        logging.info("POST %s to service %s successful",
                     post_data["value"], service)
        response_content['accepted'] = "true"
    else:
        logging.info("POST %s to service %s failed",
                     post_data["value"], service)
        response_content['accepted'] = "false"
    response_content['info'] = info

    return response_content


@generator.after_request
def add_env(response):
    # Add environment variable SITE_ENV to all responses as header
    # and add as key in all json payloads
    if SITE_ENV != "":
        response.headers['x-sentence-env'] = SITE_ENV
        logging.debug("added %s as header x-sentence-env", SITE_ENV)
        if response.content_type == 'application/json':
            response_json = response.get_json()
            response_json['env'] = SITE_ENV
            response.data = json.dumps(response_json)
            logging.debug("added %s to key env in json payload", SITE_ENV)
    return response


def get_words(attribute):
    # function to get all entries from a service.
    # Checks the Redis Cache first, if miss -
    # tries to reach the backend service and then updates the cache with new value

    # try:
    #     baseURL = getBaseURL(attribute)
    # except Exception:
    #     return []
    baseURL = getBaseURL(attribute)
    url = baseURL + "/" + attribute

    headers = {
        'content-type': 'application/json',
    }

    if CACHE_ENABLED:
        if checkCache(attribute):
            cached_value = r.get(attribute)
            return json.loads(cached_value)

    try:
        logging.info('Trying GET on URI %s', url)
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.info("Could not reach %s", url)
        logging.debug(e)
        return []

    if (response.ok):
        logging.info('Response: %s %s', response.status_code, response.reason)
        if CACHE_ENABLED:
            updateCache(attribute, response.json())
        return response.json()
    else:
        logging.warning('%s not accepted', url)
        logging.warning('Response: %s %s',
                        response.status_code, response.reason)
        return []


def get_word(attribute, index=None, query=None):
    try:
        baseURL = getBaseURL(attribute)
    except Exception:
        return []

    # Gets a specific entry from specified service, either with index or query
    if (index is not None and query is not None):
        raise ValueError("should have index or query, but not both")
    elif (index is not None):
        logging.debug("index: %s", index)
        url = baseURL + '/' + attribute + '/' + str(index)
    elif (query is not None):
        logging.debug("query: %s", query)
        url = baseURL + '/' + attribute + '?q=' + query

    headers = {
        'content-type': 'application/json',
    }

    try:
        logging.info('Trying GET on URI %s', url)
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.info("Could not reach %s", url)
        logging.debug(e)
        return []

    if (response.ok):
        logging.debug('Response: %s %s', response.status_code, response.reason)
        return response.json()
    else:
        logging.warning('%s not accepted', url)
        logging.warning('Response: %s %s',
                        response.status_code, response.reason)
        return []


def post_word(attribute, value):
    # Post a value to specified service, checks if entry already exists
    # If sucessful, resets the cache fo that service

    try:
        baseURL = getBaseURL(attribute)
    except Exception:
        return (False, "Service could not be reached")

    # Find if duplicate exists
    word = get_word(attribute, query=value)

    if (len(word) != 0):  # word exists
        logging.info("%s exists in %s", value, attribute)
        return (False, "Error: " + value + " already exists")

    url = baseURL + '/' + attribute

    headers = {
        'content-type': 'application/json'
    }

    data = {
        'name': value
    }

    try:
        logging.info('Trying POST with %s to URI %s', value, url)
        response = requests.post(url, data=json.dumps(data), headers=headers)
    except requests.exceptions.RequestException as e:
        logging.info("Could not reach %s", url)
        logging.debug(e.response)
        return (False, str(e))

    if (response.ok):
        logging.debug(url + ' Accepted')
        if CACHE_ENABLED:
            deleteFromCache(attribute)
        return (True, "")
    else:
        logging.debug("Response code: {}".format(response.status_code))
        return (False, "Response code: {}".format(response.status_code))


def getBaseURL(attribute):
    attrURL = BASE_URL_DICT.get(attribute)
    if attrURL == "":
        logging.info(
            "No URL for service %s provided, defaulting to http://<prefix>-<attribute>.<namespace>", attribute)
        return "http://%s-%s.%s" % (PREFIX, attribute, NAMESPACE)
    return attrURL


def checkCache(key):
    isCached = False
    if r.exists(key):
        logging.info("Cache Hit for %s", key)
        isCached = True
    else:
        logging.info("Cache Miss for %s", key)
    return isCached


def updateCache(key, value):
    r.setex(key, timedelta(minutes=REDIS_TTL),
            json.dumps(value))
    logging.info("Added %s to cache with %imin TTL", key, REDIS_TTL)


def deleteFromCache(key):
    r.delete(key)
    logging.info("Deleted %s from cache", key)


# A method that runs the application server.
if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    generator.run(debug=False, host='0.0.0.0', threaded=True, port=8080)

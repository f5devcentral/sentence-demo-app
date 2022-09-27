# Description
This is a very simple kubernetes demo application intended to show most of the benefits of using F5 Technology for your application delivery and security.
It is composed of multiple technology frameworks.

This app will generate a sentence :)

  ![alt text](images/app.png)

![alt text](docs/images/sentence-webapp.gif)


# App Documentation

Every `WORD` pod delivers a list of `WORDS`. Then, the `GENERATOR` select one `WORD` per POD, and generates a `SENTENCE` in a JSON format

  ![alt text](images/topology.png)


``` json
{
    "adjectives": "proud",
    "animals": "lion",
    "colors": "blue",
    "locations": "park"
}
```

Then, the frontend web application will `display` all the `words` in a `sentence`. If one micro-service is not deployed, the word is not displayed.

In term of micro-services, this is how there are used by the Webapp frontend.

  ![alt text](images/webapp-containers.png)



# Courtesy of:
Thanks to https://www.npmjs.com/package/json-server for the zero coding JSON Server.

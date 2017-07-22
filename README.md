# JakeSky

Returns the current weather, as well as a forecast for 8am, 12pm, and 6pm for the current date.

[<img src="https://darksky.net/dev/img/attribution/poweredby-oneline.png" width="600"/>](https://darksky.net/poweredby/)

## Setup

1. Get a [DarkSky key](https://darksky.net/dev/)
1. Check out this project
1. [Create a virtual environment](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install/osx/):
    1. `cd $jakesky_directory`
    1. `python -m virtualenv activate`
1. Source the virtualenv file: `source bin/activate`
1. Install the required libraries:
    * `pip install requests`
    * `pip install pytz`
1. Set up environment variables, for example, by modifying `jakesky.example.vars` and sourcing it before working.

## Running
1. Test `jakesky.py` by running it with `-v` (use `--use-cache` to reduce the number of DarkSky API calls you have to make while testing)

## Hooking up to Alexa/AWS

1. Run `build.sh` to create `JakeSky.zip`, which will be uploaded as the Lambda
1. Optionally install [Terraform](https://www.terraform.io) and use the provided configuration file (`jakesky.tf`) in order to configure the AWS side of things.
1. Follow [this walkthrough](http://moduscreate.com/build-an-alexa-skill-with-python-and-aws-lambda/) for a description of how to set up the Alexa Skill and Lambda function.
1. If your Amazon developer account is the same as the account your Echo devices are registered to, the JakeSky skill should be automatically available on each device.

### Intent Schema

```
{
  "intents": [
    {
      "intent": "GetWeather"
    },
    {
      "intent": "AMAZON.HelpIntent"
    },
    {
      "intent": "AMAZON.StopIntent"
    },
    {
      "intent": "AMAZON.CancelIntent"
    }
  ]
}
```

### Utterances

These are the utterances I chose for the `GetWeather` intent:

```
GetWeather what is the weather
GetWeather what is the forecast
GetWeather what is the weather like today
GetWeather what is the forecast like today
GetWeather what is it like today
GetWeather the weather
GetWeather the forecast
GetWeather the weather today
GetWeather the forecast today
```

## TODOs

- Try something like [Kappa](https://github.com/garnaat/kappa)
- Use the Alexa location APIs and [use the device location](https://geocod.io)

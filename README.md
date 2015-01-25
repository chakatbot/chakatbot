# chakatbot

This is a twitter bot that assembles the latest in chakat and taur artwork for the discerning
furry art connoisseur. See [@chakatbot](https://twitter.com/chakatbot) (NSFW).

If you don't like chakats, then you can easily change this bot to use keywords of your choosing.

This bot uses thricedotted's [twitterbot](https://github.com/thricedotted/twitterbot) framework and rechner's [pyweasyl](https://github.com/rechner/pyweasyl) library.

Currently, only Weasyl is supported.

## quick start

1. Follow the twitterbot [installation instructions](https://github.com/thricedotted/twitterbot).
2. From the bots directory, run:

``` shell
pip install pyweasyl
git clone https://github.com/chakatbot/chakatbot.git
cd chakatbot
```

3. Copy `default.ini` to another file, e.g. `test.ini`. Change what keywords you'd like to target, and add your bot's Twitter and Weasyl credentials. Edit `chakatbot.py`, changing `default.ini` to `test.ini` (or whatever you've named it).
4. Run the bot: `python chakatbot.py` (Make sure you still have the virtualenv active.)

Don't have a bot account? I like [this tutorial](http://dghubble.com/blog/posts/twitter-app-write-access-and-bots).

Don't have a Weasyl key? Make sure you're logged in, then visit [this page](https://www.weasyl.com/control/apikeys) to generate one.

## additional info

### configuration file

Here's a description of the options in `default.ini`:

- **tweet_interval:** the number of seconds between tweets. Default is 15 minutes.
- **filter_strings:** a list of keywords that the bot will look for in the title, tags, and description of submissions. **The bot will find these keywords even if they are substrings.**
- **ignore_strings:** a list of keywords that the bot will ignore, even if it contains a keyword as a substring.
- **api_key, api_secret, access_key, access_secret:** your bot's Twitter credentials.
- **weasyl_api:** your bot's Weasyl key.

There are additional options, but you must set them within `chakatbot.py`. Assuming you followed the quick start instructions, refer to the template in `twitterbot/examples/template/mytwitterbot.py`.

### to do

- Add an option to ignore keywords that appear as substrings.
- Add support for other art portals with public APIs.
- Add support for additional options in configuration files.

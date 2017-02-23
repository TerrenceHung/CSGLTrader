# CSGLTradeFinder

Finds trades on CSGO Lounge and automatically sends Steam trade requests.

Written in Python 3

Requires Selenium and Chrome
```
pip install selenium
```
**IMPORTANT**: Create a CSGO Lounge account and link your Steam account to it, otherwise this script will not work.

### How does it work?

Inside trades.txt, there are four lines.

The first line is the path to the ChromeDriver executable. [See here for downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads)

The second line is how many trades you want to send in total; keep in mind you can only have 30 trade offers active at once.

The third line is what you are trading away.

The fourth line is what you are looking for.

The third and fourth lines must be either a single item with the exact name and condition, or a number followed by the word 'keys'.
Follow the example in the default trades.txt file.
Only trading single items or multiple keys are supported at this time.


Chrome will start and will automatically go to the Steam login page. Log in to Steam community, and the script will search for trades and send offers, which need to be confirmed from your mobile authenticator. The browser will close once all trades are sent.

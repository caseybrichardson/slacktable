# Slacktable

#### Installation
To install the requirements, just run `pip install -r requirements.txt` in the root folder of the project. 

To run the API, you need to setup an instance folder with a file named `config.py` (more on this [here](http://flask.pocoo.org/docs/0.10/config/#instance-folders)). An example of my config is:
```python
INCOMING_WEBHOOK = "<SLACK INCOMING WEBHOOK>"
OUTGOING_TOKEN = "<SLACK OUTGOING WEBHOOK TOKEN>"
SLASH_TOKEN = "<SLACK SLASH TOKEN>"
HOST = "<YOUR HOST HERE>"
DEBUG = True
SERVER_NAME = "<YOUR SERVER HERE>"
JSONIFY_PRETTYPRINT_REGULAR = False
```

#### Usage
To use the API, you can setup a slash command in a slack chat that points at a server hosting the API. Or you can just use curl and fake the data being sent by slack. Once tests are added mocking can be done to make testing the API simpler.

#### Issues
* The song queuing system is basically totally broken. It's hacked together and was just the dumbest first pass I could think of.
* No testing.
* Needs code cleanup.
* Definitely more.

#### License
MIT License

Copyright (c) 2016 Casey Richardson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

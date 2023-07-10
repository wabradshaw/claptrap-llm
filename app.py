import os
import logging

from flask import Flask, redirect, render_template, request, url_for

from services import Services
from errors import *

app = Flask(__name__)
services = Services()
_log_level = eval(f"logging.{os.getenv('LOG_LEVEL')}")
logging.basicConfig(level=_log_level,
                    format="%(asctime)s %(levelname)-8s %(message)s")

@app.route("/jokes", methods=(["GET", "POST"]))
def index():
    punchline = request.args.get("punchline")

    if not punchline:
        logging.info("New joke requested")
        try:        
            if request.method == "POST":
                topic = request.form["topic"]
                joke = services.tell_joke_about(topic)
            else:
                joke = services.tell_joke()
            return redirect(url_for("index", 
                                    setup=joke.setup, 
                                    punchline=joke.punchline, 
                                    nucleus=joke.nucleus, 
                                    component=joke.component,
                                    change=joke.change, 
                                    substitution=joke.substitution))
        except PermanentOpenAIError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we can't generate jokes at the moment.") 
        except RetriableOpenAIError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we couldn't generate a joke. Please try again.") 
        except NoJokeFoundError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we couldn't think of a joke. Let's try again.")
        except MissingTopicError as e:
            return render_template("index.html",
                                   error="Please enter a topic.")
        except LongTopicError as e:
            return render_template("index.html",
                                   error="We can only support topics up to 16 chars long.") 
        except InappropriateTopicError as e:
            return render_template("index.html",
                                   error="No.")
        except Exception as e:
            logging.CRITICAL("UNHANDLED ERROR!")
            return render_template("index.html", error="ERROR") 
        
    else:
        logging.info(f"Displaying joke - [{punchline}]")
        return render_template("index.html", 
                               setup=request.args.get("setup"), 
                               punchline=punchline, 
                               nucleus=request.args.get("nucleus"),                                
                               component=request.args.get("component"), 
                               change=request.args.get("change"),
                               substitution=request.args.get("substitution"))
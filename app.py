import os
import logging

from flask import Flask, redirect, render_template, request, url_for

from services import Services
from errors import PermanentOpenAIError, RetriableOpenAIError, NoJokeFoundError

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
                phrase = request.form["phrase"]
                joke = services.tell_joke_about(phrase)
            else:
                joke = services.tell_joke()
            return redirect(url_for("index", 
                                    setup=joke.setup, 
                                    punchline=joke.punchline, 
                                    origin=joke.origin, 
                                    component=joke.component, 
                                    replacement=joke.replacement))        
        except PermanentOpenAIError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we can't generate jokes at the moment.") 
        except RetriableOpenAIError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we couldn't generate a joke. Please try again.") 
        except NoJokeFoundError as e:
            return render_template("index.html", 
                                   error="I'm sorry, we couldn't think of a joke. Let's try again.") 
        except Exception as e:
            logging.CRITICAL("UNHANDLED ERROR!")
            return render_template("index.html", error="ERROR") 
        
    else:
        logging.info(f"Displaying joke - [{punchline}]")
        return render_template("index.html", 
                               setup=request.args.get("setup"), 
                               punchline=punchline, 
                               origin=request.args.get("origin"), 
                               component=request.args.get("component"), 
                               replacement=request.args.get("replacement"))
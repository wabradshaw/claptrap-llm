from flask import Flask, redirect, render_template, request, url_for

from services import Services

app = Flask(__name__)
services = Services()

@app.route("/jokes", methods=(["GET"]))
def index():
    punchline = request.args.get("punchline")

    if not punchline:
        try:
            joke = services.tell_joke()
            return redirect(url_for("index", 
                                    setup=joke.setup, 
                                    punchline=joke.punchline, 
                                    origin=joke.origin, 
                                    component=joke.component, 
                                    replacement=joke.replacement))        
        except Exception as e:
            return render_template("index.html", error=str(e)) 
        
    else:
        return render_template("index.html", 
                               setup=request.args.get("setup"), 
                               punchline=punchline, 
                               origin=request.args.get("origin"), 
                               component=request.args.get("component"), 
                               replacement=request.args.get("replacement"))
# project: p4
# submitter: rarora23
# partner: none
# hours: 45

import pandas as pd
from flask import Flask, request, jsonify, Response
import re
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams["font.size"] = 16
from io import BytesIO



app = Flask(__name__)
df = pd.read_csv("main.csv", index_col = 0)
#https://www.kaggle.com/michau96/restaurant-business-rankings-2020
#interesting graph cusines that are most famous around the world and their sales


global counter
global A_count
global B_count

counter = 0
A_count = 0
B_count = 0

@app.route('/')
def home():
    global counter
    counter +=  1
    
    if counter <= 10:    
        if counter%2 == 1:
            color = "Green"
            source = "A"
        else:
            color = "Red"
            source = "B"
    else:
        if A_count >= B_count:
            color = "Green"
            source = "A"
        else:
            color = "Red"
            source = "B"
        
    with open("index.html") as f:
        html = f.read()
        
    html = html.replace("<COLOR>", color)
    html =  html.replace("<AORB>", source)
    

    return html

@app.route('/browse.html')
def browse():
    html = """<html>
            <body>
            <h1>Browse</h1>
            {}
            </body>
            </html>""".format(df.to_html())
    
    return html

@app.route('/donate.html')
def donate():
    with open("donate.html") as f:
        html = f.read()
    if len(request.args) > 0:
        source = request.args["from"]
        global A_count
        global B_count

        if source == "A":
            A_count += 1
        elif source == "B":
            B_count += 1
        
    
    return html


@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"^\D{1}\w*@\w+\.com$", email): # 1
        with open("emails.txt", "a+") as f: # open file in append mode
            f.write(email + "\n") # 2
            f.seek(0)
            n = len(f.read().strip().split("\n"))
        return jsonify("thanks, you're subscriber number {}!".format(n))
    return jsonify("Invalid Email Address!") # 3


@app.route("/dashboard_1.svg")
def plot_1():
    category = request.args["Segment_Category"]
    
    fig,ax = plt.subplots()
    df.plot.line("Segment_Category",category,ax=ax)
    ax.set_xlabel("Segment_Category")
    ax.set_ylabel(category)
    plt.xticks(rotation=45)
    plt.title("Segment_Category vs " + category) 
    f = BytesIO()
    ax.get_figure().savefig(f, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(f.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})
  
        
    
@app.route("/dashboard_2.svg")
def plot_2(): 
   
    fig,ax = plt.subplots()
    df.plot.scatter("Sales","Units",ax=ax)
    
    ax.set_xlabel("Sales")
    ax.set_ylabel("Units")
    plt.title("Sales VS Units") 
    f = BytesIO()
    ax.get_figure().savefig(f, format="svg", bbox_inches="tight")
    plt.close(fig)
    return Response(f.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})

    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
import requests
from flask import Flask, request, send_file, render_template
from hashlib import md5
import json
import flask
import glob

app = Flask(__name__, template_folder='.')

with open('./schedules.json', 'r') as file:
    schedules = json.load(file)
    new_schedules = json.dumps(schedules)

password = "a4c35816b670f3ef85f07c20727047ad"


@app.route("/<person>.png", methods=["GET"])
def get_img(person):
    if person == "calendar" or person == "splash":
        return send_file(f'{person}.png', mimetype="image/png")
    
    try:
        if md5(request.args.get('id').encode()).hexdigest() == password:
            return send_file(f'{person}.png', mimetype="image/png")
    except:
        pass
    return "<h1>404 Not Found", 418


@app.route("/", methods=["GET"])
def new_schedules():
    return render_template('index.html')


@app.route("/schedules", methods=["GET"])
def send_schedules():
    try:
        if md5(request.args.get('id').encode()).hexdigest() != password:
            return "<h1>404 Not Found", 418
    except:
        return "<h1>404 Not Found", 418

    return flask.Response(new_schedules, mimetype='application/json'), 200


#@app.route("/", methods=["GET"])
def get_schedules():
    try:
        if md5(request.args.get('id').encode()).hexdigest() != password:
            return "<h1>404 Not Found", 418
    except:
        return "<h1>404 Not Found", 418

    response = requests.get(
        "http://worldtimeapi.org/api/timezone/America/Toronto")

    if response.status_code == 200:
        time = dict(response.json())
        current_time = time["datetime"].split("T")[1].split("-")[0].split(":")
        current_time = int(current_time[0])*60 + int(current_time[1])
        dotw = str(time["day_of_week"])

        person_list = []

        for person in schedules:
            closest_class = None
            class_found = False

            for course in schedules[person][dotw]:
                start_time = schedules[person][dotw][course]["start"].split(
                    "h")
                start_time = int(start_time[0])*60 + int(start_time[1])
                duration = int(schedules[person][dotw][course]["duration"])
                end_time = f"{(start_time+duration)//60}h{round(((start_time+duration)/60-(start_time+duration)//60)*60)}"
                if end_time.split("h")[1] == "0":
                    end_time += "0"

                if start_time <= current_time and current_time <= start_time + duration:
                    person_list.append(
                        f"<a href='{person}.png?id={request.args.get('id')}'>{person}</a>🔴: {course} - {schedules[person][dotw][course]['room']} in progress until {end_time}")
                    class_found = True
                    break
                else:
                    if closest_class == None:
                        if start_time > current_time:
                            closest_class = schedules[person][dotw][course]
                            closest_class["name"] = course
                            closest_class["soon"] = True if (
                                start_time - current_time) < 10 else False
                    elif int(closest_class["start"].split("h")[0]) > start_time:
                        closest_class = schedules[person][dotw][course]
                        closest_class["name"] = course
                        closest_class["soon"] = True if (
                            int(closest_class["start"].split("h")[0]) - start_time) < 10 else False

            if not class_found:
                if closest_class == None:
                    person_list.append(
                        f"<a href='{person}.png?id={request.args.get('id')}'>{person}</a>🟢: Done for the day")
                else:
                    person_list.append(
                        f"<a href='{person}.png?id={request.args.get('id')}'>{person}</a>{'🟠' if closest_class['soon'] else '🟢'}: {closest_class['name']} - {closest_class['room']} at {closest_class['start']}")
        
#        answer = "<a href='/bus' style='height:4rem;width:8rem;background-color:black;color:white;position:fixed;bottom:0;right:0;text-decoration:none;display:flex;justify-content:center;align-items:center;font-weight:bold;font-size:1.5rem;'>Bus</a>"
        answer = ""
        answer += "<style>body{font-family:Arial,Helvetica,'sans-serif';background-color:#242424}li{font-size:5vw;color:white}ul{list-style:none}a{color:white}</style><ul>"
        for person in person_list:
            answer += f"<li>{person}</li>"
        return answer

    else:
        return "Error: {}".format(response.status_code)


@app.route("/manifest.json", methods=["GET", "POST"])
def get_manifest():
    return send_file("manifest.json", mimetype="application/json")


@app.route("/serviceWorker.js", methods=["GET", "POST"])
def get_service_worker():
    return send_file("serviceWorker.js", mimetype="text/javascript")


@app.route("/favicon.svg", methods=["GET", "POST"])
def get_favicon():
    return send_file("favicon.svg", mimetype="image/svg+xml")


@app.route("/image-paths", methods=["GET"])
def get_image_paths():
    try:
        if md5(request.args.get('id').encode()).hexdigest() != password:
            return "<h1>404 Not Found", 418
    except:
        return "<h1>404 Not Found", 418

    images = glob.glob('./*.png')

    return json.dumps(images)


if __name__ == "__main__":
    app.run()

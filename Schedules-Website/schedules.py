import requests
from flask import Flask, request, send_file
from hashlib import md5
import json

app = Flask(__name__)

with open('./schedules.json', 'r') as file:
    schedules = json.load(file)

#replace this string with an md5 hash of the wanted password
password = "__password_md5_hash__"

@app.route("/<person>.png", methods=["GET"])
def get_img(person):
    try:
        if md5(request.args.get('id').encode()).hexdigest() == password:
            return send_file(f'{person}.png', mimetype="image/png")
    except:
        pass
    return "<h1>404 Not Found", 418


@app.route("/", methods=["GET"])
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

        answer = "<a href='/bus' style='height:4rem;width:8rem;background-color:black;color:white;position:fixed;bottom:0;right:0;text-decoration:none;display:flex;justify-content:center;align-items:center;font-weight:bold;font-size:1.5rem;'>Bus</a><style>body{font-family:Arial,Helvetica,'sans-serif';background-color:#242424}li{font-size:5vw;color:white}ul{list-style:none}a{color:white}</style><ul>"
        for person in person_list:
            answer += f"<li>{person}</li>"
        return answer

    else:
        return "Error: {}".format(response.status_code)


#FIXME: make in input field for the start and end locations with a javascript frontend to process the browser's geolocation if chosen

#@app.route("/bus", methods=["GET"])
#def bus_routes():
#    return get_route()
#
#@app.route("/", methods=["POST"])
#def get_route():
#    with requests.get("http://worldtimeapi.org/api/timezone/America/Toronto") as response:
#        time = dict(response.json())["datetime"].split("T")[1].split("-")[0].split(":")
#        date = dict(response.json())["datetime"].split("T")[0]
#    time = f'{time[0]}:{time[1]}'
#
#    headers = {'Content-type': 'application/json'}
#    body = {}
#
#    response = requests.post(
#        'https://www.planibus.sto.ca/HastInfo/TravelPlans/RequestTravelPlans', headers=headers, json=body)
#
#    if response.status_code != 200:
#        return
#
#    return "<link rel='stylesheet' href='static/style.css'><ul class='Steps'>" + response.json()['Html'].split('<ul class="Steps">')[1].replace('HastInfo/Content/Shared/Images', 'static').replace('HastInfo/Content/Shared/Images', 'static').replace('HastInfo/Content/TravelPlans/Images', 'static')


if __name__ == "__main__":
    app.run()

import json

def test_schedules():
    with open('schedules.json', 'r') as f:
        schedules = json.loads(''.join(f.readlines()))

    for name in schedules.keys():
        for day in schedules[name].keys():
            if day == {}:
                continue
            for event in schedules[name][day].keys():
                assert type(schedules[name][day][event]['start']) == str
                assert type(schedules[name][day][event]['duration']) == int
                assert type(schedules[name][day][event]['room'])


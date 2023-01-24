schedule = {
    "0": {},
    "1": {},
    "2": {},
    "3": {},
    "4": {},
    "5": {},
    "6": {},
}

yesses = ['y', 'yes']


def get_class_info(day):
    print()
    class_name = input('What is the name of the class? ')
    start = input('When does the class start? (0h00) ')
    duration = int(input('How long is the class? (in minutes ex: 180) '))
    room = input('What is the room number? ')
    schedule[str(day)][class_name] = {
        "start": start,
        "duration": duration,
        "room": room
    }


name = input('What is your name? ')

weekends = input("Do you have any classes on weekends? [y/N] ")
if weekends.lower() in yesses:
    weekend_days = ["Saturday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"]
    for day in [0, 6]:
        is_class = input(f'Do you have class on {weekend_days[day]}? [Y/n] ')
        if is_class.lower() in yesses or is_class == '':
            class_num = int(input('How many classes do you have that day? '))
            for i in range(class_num):
                get_class_info(day)


days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

for day in range(1,6):
    is_class = input(f'Do you have class on {days[day-1]}? [Y/n] ')
    if is_class.lower() in yesses or is_class == '':
        class_num = int(input('How many classes do you have that day? '))
        for i in range(class_num):
            get_class_info(day-1)

print(f'''"{name}": {str(schedule).replace("'", '"')}''')
print('Add this to schedules.json')

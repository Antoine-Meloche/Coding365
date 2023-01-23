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

name = input('What is your name? ')

weekends = input("Do you have any classes on weekends? [y/N] ")
if weekends.lower() in yesses:
    print('soy lazy rn, sooo.. just continue and update it in the schedules.json (also I\'m sorry for you)') # TODO: Add functionality

days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

for day in range(1,6):
    is_class = input(f'Do you have class on {days[day-1]}? [Y/n] ')
    if is_class.lower() in yesses or is_class == '':
        class_num = int(input('How many classes do you have that day? '))
        for i in range(class_num):
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
print(f'''"{name}": {str(schedule).replace("'", '"')}''')
print('Add this to schedules.json')

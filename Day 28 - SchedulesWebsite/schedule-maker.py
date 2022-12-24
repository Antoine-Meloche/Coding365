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

name = input('What do be thou name? ')

days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
nb_days = 5+1 # added one because first, sunday, is skipped
days_start = 1

weekends = input("Do you have any classes on weekends? [y/N] ")
if weekends.lower() in yesses:
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    nb_days = 7
    days_start = 0

for day in range(days_start, nb_days):
    is_class = input(f'Do you have class on {days[day-1]}? [Y/n] ')
    if is_class.lower() in yesses or is_class.lower() == '\n':
        class_num = int(input('How many classes do you have that day? '))
        for i in range(class_num):
            print()
            class_name = input('What is the name of the class? ')
            start = input('When does the class start? (00h00) ')
            duration = int(input('How long is the class? (in minutes ex: 180) '))
            room = input('What is the room number? ')
            schedule[str(day)][class_name] = {
                "start": start,
                "duration": duration,
                "room": room
            }
print(f'{name}: {schedule}')
print('add this to schedules.json and add a png photo with the person\'s name as the name of the file in the main folder')

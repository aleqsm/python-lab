date = input("введите день и месяц рождения через пробел ")
day_str, month_str = date.split()
day = int(day_str)
month = int(month_str)
if (month == 1 and day <= 19):
    print("козерог")
elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
    print("водолей")
elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
    print("рыбы")
elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
    print("овен")
elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
    print("телец")
elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
    print("близнецы")
elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
    print("рак")
elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
    print("лев")
elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
    print("дева")
elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
    print("весы")
elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
    print("скорпион")
elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
    print("стрелец")
else:
    print("козерог")

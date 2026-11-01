zp = float(input(' зп '))
rent = float(input(' аренда жилья '))
food = float(input(' траты на питание '))
transport = float(input(' траты на транспорт '))
chill= float(input(' траты на чилл '))
sport = float(input(' траты на спорт '))
black_day = float(input('запасы на черный день '))
target = input(' Какую крупную покупку планируете? ')
target_cost = float(input(f' Сколько стоит {target}? '))
max_rent = zp * 0.30
max_food = zp * 0.20
max_transport = zp * 0.10
max_chill = zp * 0.10
max_sport = zp * 0.10
min_black_day = zp * 0.20
total = rent + food + transport + chill + sport
chp = zp - total 

print(f" всего потрачено за месяц {total}")
print(f" оставили на черный день  {chp}")
if total > zp :
    print(f"вот столько нужно у соседа отдолжить {(total-zp)} ")
if rent > max_rent:
    print(f" дорогая аренда , максимум платить это  {max_rent}")
if food > max_food:
    print(f"покупаете дорогую еду, максы можно  {max_food}")
if transport > max_transport:
    print(f" большие затраты на транспорт , меньше на такси надо ездить максиммум это  {max_transport}")
if chill > max_chill:
    print(f" много отдыхаете , максимум это  {max_chill}")
if sport > max_sport:
    print(f" качок , надо отдыхать больше максимум это  {max_sport}")
if black_day < min_black_day:
    print(f" вы так ничего не накопите надо минимум  {min_black_day}")
else:
    print(f" красавчик столько отложить  {black_day}")
if black_day <= 0:
    print('с запасами в 0 рублей накопить не получится, сосед на покупку точно не займет')
else:
    months = target_cost / black_day
    print(f'На {target} вы накопите за {months} месяца')
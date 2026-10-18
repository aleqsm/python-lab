sum = int(input('введите сумму'))
count_100 = sum//100
ost_ot_100 = sum % 100
count_50 = ost_ot_100 // 50 
ost_ot_50 = ost_ot_100 % 50
count_10 = ost_ot_50 // 10
ost_ot_10 = ost_ot_50 % 10
count_5 = ost_ot_10 // 5
ost_ot_5 = ost_ot_10 % 5
count_2 = ost_ot_5 // 2
ost_ot_2 = ost_ot_5 % 2
count_1 = ost_ot_2 // 1
ost_ot_1 = ost_ot_2 % 1
print(f"для размена суммы нам надо {count_100} соток; {count_50} пятидесяток; {count_10}  десяток; {count_5}  пятерок; {count_2} двоек; {count_1}  рубликов; ")
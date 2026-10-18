a1 = int(input("введите число a "))
b1 = int(input("введите число b "))
sum = a1 + b1 
razn = a1 - b1
proizved = a1 * b1
#delen = a1//b1
#ost = a1%b1
stepen = a1**b1
if b1 != 0 :
    delen = a1//b1
    ost = a1%b1 
    print(f"{delen} - это результат деления")
    print(f"{ost} - результат остатка")
else :
    print("деление на 0 ")
print(f"{sum} - результат суммы")
print(f"{razn} - результат разности")
print(f"{proizved} - результат произведение")
print(f"{stepen} - результат возведения в степень")
# 1. Ввод данных
age = int(input("введите возраст заемщика: "))
doxod = float(input("введите ежемесячный доход: "))
sum = float(input("введите сумму кредита: "))
months = int(input("введите срок кредита: "))
history = input("кредитная история (отличная/хорошая/удовлетворительная/плохая): ")
poruchiteli = input("поручители? (да/нет): ")
zalog = input("залог? (да/нет): ")
month_payment = sum / months
payment = (month_payment / doxod) * 100
if history == "отличная":
    risk = "низкий"
elif history == "хорошая":
    risk = "средний"
elif history == "удовлетворительная":
    risk = "большой"
else:
    risk = "максимальный"
if payment > 50 or age < 21 or age > 65:
    risk = "максимальный"
if zalog == "да" or poruchiteli == "да":
    if risk == "максимальный":
        risk = "большой"
    elif risk == "большой":
        risk = "средний"
if risk == "низкий":
    rate = 12
    verdict = "одобрено"
elif risk == "средний":
    rate = 16
    verdict = "одобрено но лучше"
elif risk == "большой":
    rate = 22
    verdict = "одобрено на соплях "
else:
    rate = 0
    verdict = "отказано"
print(f" месячная плата {month_payment:.2f}")
print(f"доход {payment:.1f}%")
print(f"риск {risk}")

if rate > 0:
    print(f" ставка: {rate}% годовых")
    
print(f"{verdict}")

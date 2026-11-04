cost = int(input("введите сумму покупки "))
age = int(input("введите ваш возраст "))
dr = input("у вас сегодня день рождения да/нет ")
vip = input("вы наш вип клиент да/нет ")
if cost > 1000:
    discount = 10
if vip == "да":
    if discount < 15:
        discount = 15
if age >= 63:
    discount += 5 
if dr == "да":
    discount += 5
if discount > 25:
    discount = 25
final_cost = cost - (cost * discount / 100)
print(f"скидка: {discount}%")
print(f"оплата: {final_cost} руб")

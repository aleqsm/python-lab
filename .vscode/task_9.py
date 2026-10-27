#время начальное будет считаться в секундах
sek = 1
minute = 60
chas = 3600
sytki = 86400
# длинна начальная будет в метрах 
mm = 0.001
cm = 0.01
m = 1 
km = 1000
#масса начальная в граммах 
mg = 0.001
g = 1
kg = 1000
t = 1000000
from_user = input("откуда переводим ")
to_user = input("во что переводим ")
user_znach = input("введите ")
if from_user == "sek":
     k1 = sek
elif from_user == "minute":
     k1 = minute
elif from_user == "chas":
     k1 = chas
elif from_user == "sytki":
     k1 = sytki
elif from_user == "mm":
     k1 = mm
elif from_user == "cm":
     k1 = cm
elif from_user == "m":
     k1 = m
elif from_user == "km":
     k1 = km
elif from_user == "mg":
     k1 = mg
elif from_user == "g":
     k1 = g
elif from_user == "kg":
     k1 = kg
elif from_user == "t":
     k1 = t
if to_user == "sek":
     k2 = sek
elif to_user == "minute":
     k2 = minute
elif to_user == "chas":
     k2 = chas
elif to_user == "sytki":
     k2 = sytki
elif to_user == "mm":
     k2 = mm
elif to_user == "cm":
     k2 = cm
elif to_user == "m":
     k2 = m
elif to_user == "km":
     k2 = km
elif to_user == "mg":
     k2 = mg
elif to_user == "g":
     k2 = g
elif to_user == "kg":
     k2 = kg
elif to_user == "t":
     k2 = t
result = user_znach * k1 / k2
print("перевод", result)

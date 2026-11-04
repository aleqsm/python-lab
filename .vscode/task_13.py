numbers_input = input("введите числа через пробел ")
list = numbers_input.split()

numbers = []
for item in list:
    if "." in item:
        numbers.append(float(item))
    else:
        numbers.append(int(item))
unique_numbers = []
povt = []
for num in numbers:
    count = 0
    for x in numbers:
        if x == num:
            count += 1
    if count == 1:
        unique_numbers.append(num)
    else:
        added = False
        for d in povt:
            if d == num:
                added = True
        if not added:
            povt.append(num)
chetn = []
nechet = []
for num in numbers:
    if int(num) == num:
        if num % 2 == 0:
            chetn.append(num)
        else:
            nechet.append(num)
negative_numbers = []
for num in numbers:
    if num < 0:
        negative_numbers.append(num)
drob = []
for num in numbers:
    if int(num) != num:
        drob.append(num)
krat_5 = 0
for num in numbers:
    if num % 5 == 0:
        krat_5 += num
max_num = numbers[0]
min_num = numbers[0]
for num in numbers:
    if num > max_num:
        max_num = num
    if num < min_num:
        min_num = num
print("уникальные числа", unique_numbers)
print("повторяющиеся числа", povt)
print("четные числа", chetn)
print("нечетные числа",nechet)
print("отрицательные числа", negative_numbers)
print("дробные", drob)
print("лратные 5", krat_5)
print("самое большое число", max_num)
print("самое маленькое число", min_num)

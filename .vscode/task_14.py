input_1 = input('введите 1 набор чисел(через пробел) ').split()
list_1 = []
for num in input_1:
    list_1.append(int(num))
set_1 = set(list_1)
input_2 = input('введите 2 набор чисел (через пробел) ').split()
list_2 = []
for num in input_2:
    list_2.append(int(num))
set_2 = set(list_2)
point1 = set_1 & set_2
point2_1 = set_1 - set_2
point2_2 = set_2 - set_1
point_3 = set_1 ^ set_2
print(f'решение пункта 1 {point1}')
print(f'решение пункта 2_1 {point2_1}')
print(f' решение пункта 2_2 {point2_2}')
print(f'решение 3 пункта {point_3}')

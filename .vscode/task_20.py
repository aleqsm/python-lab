result=[]
def uniq_elements(list_1):
   # result=[]
    for item in list_1:
        if type(item) == list :
             uniq_elements(item)
        else:
            if item not in result :
                result.append(item)
list_a = [1, 2, 3, [4, 3, 1], 5, [6, [7, [10], 8, [9, 2, 3]]]]
uniq_elements(list_a)
print(f" наш вывод {result}")

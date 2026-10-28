def func_list(list_1):
    k = -1
    while k >= -len(list_1):
        curr = list_1[k]
        if isinstance(curr, list):
            func_list(curr)
            if k == -1:
                list_1[k:] = curr
            else:
                list_1[k:k+1] = curr
            k -= len(curr)  
        else:
            k -= 1  
list_1111111 = [1, 2, 3, [4], 5, [6, [7, [], 8, [9]]]] 
func_list(list_1111111)
print((list_1111111))
   
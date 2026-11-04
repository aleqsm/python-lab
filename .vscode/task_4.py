str_1 = input("write  ")
poli = 1
print(len(str_1))
for i in range(len(str_1)):
    if str_1[i] != str_1[-1-i] :
        poli = 0
        print("net")
        break
        #print("polindrom")
if poli == 1 :
        print("da")
#else : 
       # print("net")
        

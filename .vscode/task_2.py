password = input("введите пароль"'\n')
num_count = 0
lettr_count = 0
for curr in password :
    if '0' <= curr <= '9' :
        num_count += 1
       # print(f"cимвол {curr} цифра")
    else : 
       # print( f" символ {curr} буква")
        lettr_count +=1
         

 

if len(password) < 16 :
    print('eror')
    
elif  num_count !=0 and lettr_count !=0 :
        print("okay")
else : 
        print("weak password")
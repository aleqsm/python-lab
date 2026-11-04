import random
rand_num = random.randint(1, 100)
while True :
    user_num = int(input("введите ваше число "))
    if user_num > rand_num : 
        print("ваше число больше ")
    elif user_num < rand_num :
        print("ваше число меньше ")
    else :
        print ("вы угадали")
        break            
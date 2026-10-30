from datetime import datetime 
def log_calls(text):
    def dec(func):
        def wrp(*args):
            result = func(*args) 
            file = open('text.txt', 'a')
            file.write('priwet')
            file.write("[" + str(datetime.now()) + "] ")
            #file.write("функция  " + func.__name__ + " ") выводит какие то вопросы 
            #file.write("аргументы  " + str(args) + "\n") тоже самое 



            file.close()
            return result
        return wrp 
    return dec 
@log_calls("text.txt")
def wrt():
    print("priwet")
wrt()   

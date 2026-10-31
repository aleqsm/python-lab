from datetime import datetime 
def log_calls(text):
    def dec(func):
        def wrp(*args):
            result = func(*args) 
            file = open('text.txt', 'a', encoding='utf-8') # выводились нечитаемые символы пришлось добавить кодировку
            file.write('priwet')
            file.write("[" + str(datetime.now()) + "] ")
            file.write("функция  " + func.__name__ + " ")
            file.write("аргументы  " + str(args) + "\n")  



            file.close()
            return result
        return wrp 
    return dec 
@log_calls("text.txt")
def wrt():
    print("priwet")
wrt()   

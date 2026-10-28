import time
def timing(func):
    def wrapper (*args):
        start = time.time()
        result = func(*args)
        end = time.time()
        result_1 = (end - start) * 1000 
        print(f" разница {result_1}")
        return result
    return wrapper

@timing
def func_1():
    test = input("ввод")
    print(f'{test}\n' * 52)
func_1()
def cache(func):
    dict_1 = dict()
    def wrp(*args):
        if args in dict_1:
            return dict_1[args]
        dict_1[args] = func(*args)  
    return wrp
@cache
def keshic():
    print("priwet")
keshic()  
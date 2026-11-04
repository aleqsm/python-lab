def type_check(*types):
    def dec(func):
        def wrp(*args):
            for i in range(len(args)): 
                if not isinstance(args[i], types[i]):
                    raise TypeError(" eoror")
            result = func(*args)
            return result 
        return wrp
    return dec
@type_check()
def keshic():
    print("priwet")
keshic()  
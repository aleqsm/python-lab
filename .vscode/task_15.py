products = [
    {"name": "тормозные колодки", "price": 120, "sold": 40},
    {"name": "масляный фильтр", "price": 45, "sold": 150},
    {"name": "амортизатор", "price": 50, "sold": 30},
    {"name": "свеча зажигания", "price": 15, "sold": 100},
    {"name": "патрубки", "price": 25, "sold": 10} 
]

all_sum = []
for tovar in products :
    sum = tovar["price"] * tovar["sold"]
    print(f" продажи по {tovar["name"]} вышли в {sum}")
    all_sum.append(sum)
max_sum = max(all_sum)    
for tovar in products :
    if tovar["price"] * tovar["sold"] == max_sum :
        print(f"самый прибыльный товар {tovar['name']} вышел в {max_sum} ")
uniq_name = []
for tovar in products:
    if   tovar["name"]  not in uniq_name:
        uniq_name.append(tovar["name"])
print(len(uniq_name))        

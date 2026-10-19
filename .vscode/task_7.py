minut_tarif = 60
sms_tarif = 30
internet_tarif = 1024
sum_tarif = 24.99
minut = int(input(" write minutes"))
sms = int(input(" write sms"))
internet = int(input(" write internet"))
if minut > minut_tarif :
    minut_dop = (minut - minut_tarif)* 0.89
else : 
    minut_dop = 0
   # print("vse horosho po minutam ")
if sms > sms_tarif :
    sms_dop = (sms - sms_tarif)* 0.59
else : 
    sms_dop = 0
  #  print("vse horosho po sms ")
if internet > internet_tarif :
    internet_dop = (internet - internet_tarif)* 0.79
else : 
    internet_dop = 0
  #  print("vse horosho po internety ")    
all_sum = minut_dop + sms_dop + internet_dop + sum_tarif
sum_nalog = all_sum * 0.02
itog_sum = all_sum + sum_nalog 
if minut_dop > 0 :
    print(f"doplata za minuty {minut_dop:.2f}")
if sms_dop > 0 :
    print(f"doplata za sms {sms_dop:.2f}")
if internet_dop > 0 :
    print(f"doplata za internet {internet_dop:.2f}")
print(f"tarif {sum_tarif:.2f}")
print(f" nalog {sum_nalog:.2f}")
print(f"itog {itog_sum:.2f}")    

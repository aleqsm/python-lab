text_input = input("введите ваш текст ")
all_words = text_input.split()







for i in range(2):
    total_words = len(all_words)
    print(f"всего слов {total_words}")
    com_words = {}
    for word in all_words:
        if word in com_words:
            com_words[word] += 1
        else:
            com_words[word] = 1
    for word in com_words:
        print(f"слово {word} встречается {com_words[word]}")
    max_value = max(com_words.values())        
    most_com_word = []
    for k in com_words:
        if com_words[k] == max_value:
            most_com_word.append(k)      
    result_common = ""
    for wrd in most_com_word:
        result_common += wrd + " "
    print(f"больше всего встретилось {result_common}")
    word_lengths = []
    for word in com_words:
        word_lengths.append(len(word))
    max_len = max(word_lengths)
    min_len = min(word_lengths) 
    bigest_word = []
    smalest_word = []
    for word in com_words:
        if len(word) == max_len:
            bigest_word.append(word)
        if len(word) == min_len:
            smalest_word.append(word)
    result_bigest = ""
    for wrd in bigest_word:
        result_bigest += wrd + " "    
    result_smalest = ""
    for wrd in smalest_word:
        result_smallest += wrd + " "
    print(f"больше всех по длине {result_bigest}")
    print(f"меньше всех по длине {result_smalest}\n")
    filtered_words = []
    for word in all_words:
        if len(word) >= 3:
            filtered_words.append(word)       
    all_words = filtered_words

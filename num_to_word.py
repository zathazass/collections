__author__ = 'Sathananthan A'
__description__ = 'Get textual representation for integer number from 1 to 999999999'
__version__ = (0,1,0)


ones = {
    1:'one', 2:'two', 3:'three', 4:'four', 5:'five',
    6:'six', 7:'seven', 8:'eight', 9:'nine'
}
twos = {
    11:'eleven', 12:'twelve', 13:'thirteen', 14:'forteen', 15:'fifteen',
    16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19:'nineteen'
}
twos_full = {
    10:'ten', 20: 'twenty', 30:'thirty', 40:'forty', 50:'fifty',
    60: 'sixty', 70:'seventy', 80: 'eighty', 90: 'ninety'
}

grade = {
    3:'hundred',4:'thousand', 5:'thousand',
    6:'lakh', 7:'lakh', 8:'crore', 9:'crore'
}


def get_word_for_number(number):
    '''
    Get integer as input and returns appropriate word for that number.
    
    Range from 1 to 999999999
    '''
    # required variables
    word, space, len_of_num = '', ' ', len(str(number))

    # some pre-conditions
    try: number = int(number)
    except: return number
    if not isinstance(number, (int, float)) or len_of_num > 9: return number

    # process below 100
    if len_of_num < 3:
        quatient, remainder = divmod(number, 10)
        if remainder == 0 and quatient == 0: pass
        if remainder == 0 and quatient: 
            word += space+twos_full.get(number, ones.get(number))
        elif remainder and quatient:
            if quatient == 1:
                word += space+twos.get(number)
            else:
                word += space+twos_full.get(quatient*10)+space+ones.get(remainder)
        elif remainder and quatient ==0: word += space+ones.get(number)
        return word.strip().capitalize()

    # process above 99 and below 1000000000
    if len_of_num >= 3 and len_of_num <= 9:
        if len_of_num%2==1 and len_of_num>4:
            right_most = int(str(number)[:2])
            modulo_number = '1'+'0'*(len_of_num-1-1)
        else:
            right_most = int(str(number)[0])
            modulo_number = '1'+'0'*(len_of_num-1)

        quatient, remainder = divmod(number, int(modulo_number))
        odds_word = ones.get(right_most,
            twos.get(right_most, twos_full.get(right_most))
        )
        if odds_word is None and len_of_num>4:
            odds_word = twos_full.get((right_most//10)*10)+space+ones.get(right_most%10)
        word += odds_word+space+grade.get(len_of_num)+space
        return (word + get_word_for_number(remainder)).strip().capitalize() # recursive loop
    

n2w = get_word_for_number # simple alias
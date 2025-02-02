# Q3 --> without challenge
def q3_solution_1():
    words = set()
    while True:
        word = input(f'Please type a word: ')
        if word in words:
            print(f'You entered the word {word} twice. Good bye...')
            break
        words.add(word)


# Q3 --> with challenge
def q3_solution_2():
    words = {}
    while True:
        word = input(f'Please type a word: ').lower()
        words.setdefault(word, 0)
        words[word] += 1
        if words[word] == 3:
            print(f'You entered the word {word} three times. Good bye...')
            break


if __name__ == '__main__':
    q3_solution_1()
    # q3_solution_2()  # Uncomment for solution 2 with challenge

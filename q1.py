# Q1 - solution
user_input = int(input('Please enter a number: '))
divisors = (str(i) for i in range(user_input // 2, 0, -1) if user_input % i == 0)
print(' ,'.join(divisors))
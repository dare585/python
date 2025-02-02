# Q4 - solution
from random import randint

# Generate random lists
l1 = [randint(-100, 100) for _ in range(randint(1, 10))]
l2 = [randint(-100, 100) for _ in range(randint(1, 10))]

print(f'l1 is: {l1}')
print(f'l2 is: {l2}')

def num_compare(n1, n2):
    return 1 if n1 > n2 else (-1 if n1 < n2 else 0)


total_sum = sum(map(num_compare, l1, l2))
msg = f'{l1} is bigger' if total_sum > 0 else (f'{l2} is bigger' if total_sum < 0 else 'Teko')
print(msg)
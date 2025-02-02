# Q2 - solution
count = 1
total_sum = 0

user_input = int(input(f'Please enter number #{count}: '))
while user_input >= 0:
    total_sum +=  user_input
    average = total_sum // count # Round the average to align the Example output 
    count += 1
    user_input = int(input(f'Please enter number #{count} '
                           f'(avg={average}. Sum={total_sum}): '))
print('Thank you. Goodbye.')
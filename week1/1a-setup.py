print("Hello, World!")

# Write your greet function definition below:

def greet(name):
  return 'Hello, '+name+'!'

# Any code inside the if statement will be ignored by the automarker.
# Put your test code in here, since it will be run by clicking Run or Terminal.
if __name__ == '__main__':
  print(greet('World'))
  print(greet('Grok'))
  print(greet('123'))

# Python function syntax examples

def double(val):
  return val + val

print(double(3))
print(double('3'))

def add(a, b):
  return a + b
  
if __name__ == '__main__':
  print(add(2, 3))
  print(add(1, 5))
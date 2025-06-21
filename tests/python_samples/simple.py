def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def calculate(a, b):
    result = add(a, b)
    return multiply(result, 2)

def main():
    print(calculate(5, 3))

if __name__ == "__main__":
    main()
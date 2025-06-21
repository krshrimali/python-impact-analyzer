class Calculator:
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, x):
        self.value += x
        return self.value
    
    def multiply(self, x):
        self.value *= x
        return self.value
    
    def calculate(self, a, b):
        self.add(a)
        self.multiply(b)
        return self.value


class AdvancedCalculator(Calculator):
    def __init__(self, initial_value=0):
        super().__init__(initial_value)
    
    def power(self, exponent):
        self.value = self.value ** exponent
        return self.value
    
    def advanced_calculate(self, a, b, exponent):
        self.calculate(a, b)
        self.power(exponent)
        return self.value


def process_data(data, exponent=2):
    calculator = Calculator()
    for item in data:
        calculator.add(item)
    
    advanced = AdvancedCalculator(calculator.value)
    return advanced.advanced_calculate(10, 2, exponent)


def main():
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
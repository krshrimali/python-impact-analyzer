def is_valid_input(value):
    if value < 0:
        return False
    if value > 100:
        return False
    return True

def process_positive(value):
    return value * 2

def process_negative(value):
    return abs(value) * 3

def process_large(value):
    return value // 10

def process_value(value):
    if not is_valid_input(value):
        if value < 0:
            return process_negative(value)
        else:  # value > 100
            return process_large(value)
    else:
        return process_positive(value)

def calculate_results(values):
    results = []
    for value in values:
        results.append(process_value(value))
    return results

def main():
    values = [-5, 10, 50, 200]
    results = calculate_results(values)
    print(f"Results: {results}")

if __name__ == "__main__":
    main()
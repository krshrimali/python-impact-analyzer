def check_condition(value):
    if value > 10:  # This condition uses the variable 'value'
        return "Greater than 10"
    elif value < 0:  # This condition also uses 'value'
        return "Negative"
    else:
        return "Between 0 and 10"

def process_value(value):
    # This function uses the same variable 'value' in its condition
    if value % 2 == 0:  # This condition would be impacted if 'value' changes meaning
        return "Even"
    else:
        return "Odd"

def calculate_result(value):
    # This function calls check_condition and would be impacted by changes to it
    result = check_condition(value)

    # It also uses the same variable in its own condition
    if value > 100:  # This condition shares a variable with check_condition
        result += " (Large)"

    return result

def main():
    values = [-5, 5, 15, 200]
    for val in values:
        print(f"Value {val}: {calculate_result(val)}, {process_value(val)}")

if __name__ == "__main__":
    main()

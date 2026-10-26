
# Do not change this function!
def divide(n, d):
    if d == 0:
        raise ZeroDivisionError

    return n / d


# Do not change this function!
def get_element(a, i):
    if i < 0 or i >= len(a):
        return -1

    return a[i]


def wrapped_divide(n, d):
    try:
        return divide(n, d)
    except ZeroDivisionError:
        return -1


def wrapped_get_element(a, i):
    result = get_element(a, i)

    if result == -1:
        raise IndexError

    return result


# Test cases for wrapped_divide and wrapped_get_element functions
print(wrapped_divide(10, 2))  # 5.0
print(wrapped_divide(10, 0))  # -1

print(wrapped_get_element([10, 20, 30], 1))  # 20

try:
    wrapped_get_element([10, 20, 30], 5)
except IndexError:
    print("IndexError caught!")
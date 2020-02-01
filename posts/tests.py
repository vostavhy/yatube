from django.test import TestCase
import datetime as dt

# print(dt.datetime.now().year)


def cache3(func):

    _cache = {'count': 0}
    _cache['result'] = ''

    def wrapper(*args, **kwargs):
        _cache['count'] += 1
        if _cache['count'] == 1:
            _cache['result'] = func(*args, **kwargs)
        elif _cache['count'] == 3:
            _cache['count'] = 0
        return _cache['result']

    return wrapper


@cache3
def heavy():
    print('Сложные вычисления')
    return 1


print(heavy())
# Сложные вычисления
# 1
print(heavy())
# 1
print(heavy())
# 1

# Опять кеш устарел, надо вычислять заново
print(heavy())
# Сложные вычисления
# 1


'''
def cache_args(func):
    _cache = {}

    def wrapper(*args, **kwargs):
        if args in _cache:
            print('вывод кешированного результата')
            return _cache[args]
        else:
            _cache[args] = func(*args, **kwargs)
        return _cache[args]
    return wrapper


@cache_args
def long_heavy(num):
    print(f"Долго и сложно {num}")
    return num ** num


print(long_heavy(1))
# Долго и сложно 1
# 1
print(long_heavy(1))
# 1
print(long_heavy(2))
# Долго и сложно 2
# 4
print(long_heavy(2))
# 4
print(long_heavy(2))
# 4

'''



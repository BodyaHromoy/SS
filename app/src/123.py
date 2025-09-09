# Читаем из stdin и суммируем N вещественных чисел
# в формате ОДИНАРНОЙ точности (float32), как требует условие.

import sys
from ctypes import c_float

data = sys.stdin.read().split()

# Количество дальнейших чисел
n = int(data[0])

# Сумма
s = c_float(0.0)

# Последовательно добавляем каждое из N чисел,
# приводя и слагаемое, и накопленную сумму к float32.
for i in range(1, n + 1):
    x = c_float(float(data[i]))
    s = c_float(s.value + x.value)

print(f"{s.value:.2f}")

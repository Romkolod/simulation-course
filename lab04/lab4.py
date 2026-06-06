import random
class LinearCongruentialGenerator:
    def __init__(self, seed):
        self.state = seed

        self.a = 1103515245
        self.c = 12345
        self.m = 2 ** 31

    def next_float(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state / self.m

def calc_M(data):
    return sum(data) / len(data)

def calc_D(data, mean):
    variance_sum = sum((x - mean) ** 2 for x in data)
    return variance_sum / (len(data) - 1)
if __name__ == "__main__":
    SAMPLE_SIZE = 100000

    theoretical_M = 0.5
    theoretical_D = 1 / 12
    lcg = LinearCongruentialGenerator(seed=50)
    custom_sample = [lcg.next_float() for _ in range(SAMPLE_SIZE)]


    random.seed(50)
    builtin_sample = [random.random() for _ in range(SAMPLE_SIZE)]

    custom_M = calc_M(custom_sample)
    custom_D = calc_D(custom_sample, custom_M)

    builtin_M = calc_M(builtin_sample)
    builtin_D = calc_D(builtin_sample, builtin_M)

    print(f"{'Показатель':<25} | {'Теория':<12} | {'Сделанный':<15} | {'Встроенный':<15}")
    print("-" * 75)
    print(f"{'Выборочное среднее':<25} | {theoretical_M:<12.6f} | {custom_M:<15.6f} | {builtin_M:<15.6f}")
    print(f"{'Выборочная дисперсия':<25} | {theoretical_D:<12.6f} | {custom_D:<15.6f} | {builtin_D:<15.6f}")

    print("\nПогрешность:")
    print(f"Сделанный:    Мат ожид = {abs(custom_M - theoretical_M):.6f},  Дисперсии= {abs(custom_D - theoretical_D):.6f}")
    print(f"Встроенный:   Мат ожид = {abs(builtin_M - theoretical_M):.6f},  Дисперсии = {abs(builtin_D - theoretical_D):.6f}")
def breeding_time(hut_level, braves, population):
    """Breeding time in seconds, straight from constant.dat values.

    T = (base_sprog_time * band% / 100) / (hut_multiplier * 12.5)

    hut_multiplier = 0.5 + 0.5 * braves   ("X 0 - 0.5, 1 - 1.0, 2 - 1.5 ...")
    band% is P3CONST_SPROG%_POP_BAND_* selected by the tribe's population
    as a percentage of the 200 max population.
    12.5 = game turns per second.
    """
    base_sprog_time = {1: 4000, 2: 3000, 3: 2000}[hut_level]
    hut_multiplier = 0.5 + 0.5 * braves
    bands = [30, 35, 40, 50, 60, 70, 80, 90, 100, 110,
             120, 130, 140, 150, 160, 170, 180, 190, 195, 200]
    band_pct = bands[min(int(population / 200 * 100) // 5, 19)]
    return (base_sprog_time * band_pct / 100) / (hut_multiplier * 12.5)


# Test the function with the measured in-game data points
print(breeding_time(1, 1, 4))  # Measured: 97
print(breeding_time(1, 2, 4))  # Measured: 64
print(breeding_time(1, 3, 4))  # Measured: 48
print(breeding_time(2, 1, 4))  # Measured: 65
print(breeding_time(2, 2, 4))  # Measured: 47
print(breeding_time(2, 3, 4))  # Measured: 34
print(breeding_time(2, 4, 4))  # Measured: 27
print(breeding_time(3, 1, 4))  # Measured: 48
print(breeding_time(3, 2, 4))  # Measured: 30
print(breeding_time(3, 3, 4))  # Measured: 22
print(breeding_time(3, 4, 4))  # Measured: 18
print(breeding_time(3, 5, 4))  # Measured: 14
print(breeding_time(3, 5, 15)) # Measured: 19
print(breeding_time(3, 5, 25)) # Measured: 22
print(breeding_time(3, 1, 25)) # Measured: 65
print(breeding_time(1, 0, 4))  # Measured: 197 (empty hut!)
print(breeding_time(3, 0, 14)) # Measured: 120 (empty hut!)

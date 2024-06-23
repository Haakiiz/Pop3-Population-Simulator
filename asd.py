def breeding_time(hut_level, braves, population):
    base_sprog_time = {1: 4000, 2: 3000, 3: 2000}[hut_level]
    hut_multiplier = braves
    if 0 <= population < 5:
        population_band_modifier = 0.30
    elif 5 <= population < 10:
        population_band_modifier = 0.35
    elif 10 <= population < 15:
        population_band_modifier = 0.40
    # Add more conditions here if needed
    else:
        population_band_modifier = 0.40  # Default value
    return (base_sprog_time / hut_multiplier) * population_band_modifier


# Test the function with the provided data points
print(breeding_time(1, 1, 4))  # Expected: 97
print(breeding_time(1, 2, 4))  # Expected: 64
print(breeding_time(1, 3, 4))  # Expected: 48
print(breeding_time(2, 1, 4))  # Expected: 65
print(breeding_time(2, 2, 4))  # Expected: 47
print(breeding_time(2, 3, 4))  # Expected: 34
print(breeding_time(2, 4, 4))  # Expected: 27
print(breeding_time(3, 1, 4))  # Expected: 48
print(breeding_time(3, 2, 4))  # Expected: 30
print(breeding_time(3, 3, 4))  # Expected: 22
print(breeding_time(3, 4, 4))  # Expected: 18
print(breeding_time(3, 5, 4))  # Expected: 14
print(breeding_time(3, 5, 10)) # Expected: 19
print(breeding_time(3, 5, 20)) # Expected: 22
print(breeding_time(3, 1, 20)) # Expected: 65

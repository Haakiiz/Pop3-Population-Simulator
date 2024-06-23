import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Data (population, hut_level, brave_count, sprog_rate)
data = [
    (4, 1, 2, 55),
    (14, 1, 1, 116),
    (14, 1, 3, 57),
    (14, 2, 4, 33),
    (14, 2, 3, 42),
    (14, 2, 2, 55),
    (14, 3, 3, 27),
    (14, 3, 2, 19),
    (14, 3, 0, 120),
    (4, 1, 0, 197),
    (4, 1, 1, 100),
    (4, 1, 2, 71)
]

# Separate input variables (population, hut_level, brave_count) and output variable (sprog_rate)
X = np.array([[pop, hut_lvl, brave_count] for pop, hut_lvl, brave_count, _ in data])
y = np.array([sprog_rate for _, _, _, sprog_rate in data])

# Create polynomial features for the input variables
degree = 3
poly = PolynomialFeatures(degree, interaction_only=False, include_bias=True)
X_poly = poly.fit_transform(X)

# Fit a linear regression model to the polynomial features
model = LinearRegression()
model.fit(X_poly, y)

# Use the fitted model to make predictions
predicted_sprog_rates = model.predict(X_poly)

print("Predicted sprog rates:", predicted_sprog_rates)

from execution.geospatial_engine import engine

# Test Case 1: Arbitrary location (Santiago)
# Santiago ~ -33.4489, -70.6693
print("Testing Santiago...")
result = engine.check_location(-33.4489, -70.6693)
print(result)

# Test Case 2: Near known coastal area (valparaisoish)
# Valparaiso ~ -33.0472, -71.6127
print("\nTesting Valparaiso...")
result_valpo = engine.check_location(-33.0472, -71.6127)
print(result_valpo)

# from lightkurve import search
# import lightkurve as lk

# # Search for a known exoplanet (e.g., Kepler-10b, TIC ID or KIC)
# search_result = search.lightcurve("Kepler-10")  # Or use target pixel file: search.targetpixelfile("KIC 11914151")
# lc = search_result[0].download()  # Downloads from MAST
# lc.plot()  # Visualize flux over time

import pandas as pd

# csv_file_path = "/home/mhabrar/Downloads/NASA Space Apps/candidates_FIXED.csv"
csv_file_path = "/home/mhabrar/Downloads/NASA Space Apps/exoplanets_vs_false_FIXED.csv"

# Load your CSV file into a DataFrame
# Replace 'your_data.csv' with the actual path to your file
df = pd.read_csv(csv_file_path)

# Use the head() method to get the first 10 rows
first_10_rows = df.head(10)

# Print the result to the console
print(first_10_rows)

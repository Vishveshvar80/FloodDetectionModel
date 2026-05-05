import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

print("Generating dummy finalDataset.csv...")
# Create a dummy dataset
data = {
    'water_level': np.random.uniform(10, 90, 100),
    'rainfall': np.random.uniform(0, 50, 100),
    'humidity': np.random.uniform(40, 100, 100),
    'soil_moisture': np.random.uniform(10, 80, 100),
}
# Add a target variable for the model (water_level > 75 = DANGER)
target = (data['water_level'] > 75).astype(int)

df = pd.DataFrame(data)
df.to_csv('finalDataset.csv', index=False)
print("finalDataset.csv created!")

print("Training dummy model and scaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

model = LogisticRegression()
model.fit(X_scaled, target)

# Save to pickle
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("scaler.pkl created!")

with open('flood_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("flood_model.pkl created!")

print("All dummy files generated successfully! You can now run the Flask backend.")

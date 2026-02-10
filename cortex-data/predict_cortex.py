import sys
import joblib
import json
import numpy as np

# Load model
model = joblib.load('cortex_model.pkl')
encoder = joblib.load('category_encoder.pkl')
with open('cortex_config.json') as f:
    config = json.load(f)

# Get args
if len(sys.argv) < 3:
    print("Usage: python3 predict_cortex.py <sqft> <category>")
    print("Example: python3 predict_cortex.py 1500 Bardeaux")
    print(f"\nCategories: {list(config['category_mapping'].keys())}")
    sys.exit(1)

sqft = float(sys.argv[1])
category = sys.argv[2]
has_subs = int(sys.argv[3]) if len(sys.argv) > 3 else 0

# Encode
cat_encoded = config['category_mapping'].get(category, 0)

# Predict
X = np.array([[sqft, cat_encoded, has_subs]])
prediction = model.predict(X)[0]

print(f"\n{'='*50}")
print(f"CORTEX ESTIMATE")
print(f"{'='*50}")
print(f"Sqft: {sqft:,.0f}")
print(f"Category: {category}")
print(f"Has subs: {'Yes' if has_subs else 'No'}")
print(f"\n💰 Estimated: ${prediction:,.0f} CAD")
print(f"   Range: ${prediction*0.85:,.0f} - ${prediction*1.15:,.0f}")
print(f"{'='*50}\n")

import sys
import joblib
import json
import numpy as np

# Load models
global_model = joblib.load('cortex_model_global.pkl')
bardeaux_model = joblib.load('cortex_model_Bardeaux.pkl')
encoder = joblib.load('category_encoder_v3.pkl')

with open('cortex_config_v3.json') as f:
    config = json.load(f)

def predict(sqft, category, material_lines=5, labor_lines=2, has_subs=0, complexity=10):
    """
    Predict quote price.
    
    Args:
        sqft: Square footage
        category: Job category (Bardeaux, Élastomère, Other, etc.)
        material_lines: Number of material line items (default 5)
        labor_lines: Number of labor line items (default 2)
        has_subs: Whether subcontractors involved (0 or 1)
        complexity: Complexity score (default 10)
    """
    
    # Per-category features (no cat_enc)
    X_cat = np.array([[sqft, material_lines, labor_lines, has_subs, complexity]])
    
    # Global features (with cat_enc)
    cat_enc = config['category_mapping'].get(category, 0)
    X_global = np.array([[sqft, material_lines, labor_lines, has_subs, complexity, cat_enc]])
    
    # Use specialized model for Bardeaux, global for others
    if category == 'Bardeaux':
        prediction = bardeaux_model.predict(X_cat)[0]
        model_used = 'Bardeaux (R²=0.65)'
        confidence = 'HIGH'
    else:
        prediction = global_model.predict(X_global)[0]
        model_used = 'Global (R²=0.59)'
        confidence = 'MEDIUM' if category in ['Other', 'Élastomère'] else 'LOW'
    
    return {
        'estimate': prediction,
        'range_low': prediction * 0.80,
        'range_high': prediction * 1.20,
        'model': model_used,
        'confidence': confidence
    }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("\nUsage: python3 predict_final.py <sqft> <category> [material_lines] [labor_lines] [has_subs] [complexity]")
        print("\nExamples:")
        print("  python3 predict_final.py 1500 Bardeaux")
        print("  python3 predict_final.py 1500 Bardeaux 8 3 0 15")
        print("  python3 predict_final.py 2000 Élastomère")
        print(f"\nCategories: {list(config['category_mapping'].keys())}")
        sys.exit(1)
    
    sqft = float(sys.argv[1])
    category = sys.argv[2]
    material_lines = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    labor_lines = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    has_subs = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    complexity = int(sys.argv[6]) if len(sys.argv) > 6 else 10
    
    result = predict(sqft, category, material_lines, labor_lines, has_subs, complexity)
    
    print(f"""
{'='*55}
CORTEX V3 ESTIMATE
{'='*55}
Sqft:           {sqft:,.0f}
Category:       {category}
Material Lines: {material_lines}
Labor Lines:    {labor_lines}
Has Subs:       {'Yes' if has_subs else 'No'}
Complexity:     {complexity}

💰 ESTIMATE:    ${result['estimate']:,.0f} CAD
   Range:       ${result['range_low']:,.0f} - ${result['range_high']:,.0f}

Model:          {result['model']}
Confidence:     {result['confidence']}
{'='*55}
""")

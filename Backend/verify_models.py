"""Quick verification of trained models"""
import joblib
from pathlib import Path
import pandas as pd

model_dir = Path('models')
temp_model = joblib.load(model_dir / 'temp_model.pkl')
rain_model = joblib.load(model_dir / 'rain_model.pkl')
feature_list = joblib.load(model_dir / 'feature_list.pkl')

print('='*80)
print('MODEL TRAINING COMPLETE')
print('='*80)

print(f'\n📊 Temperature Model:')
print(f'   Type: {type(temp_model).__name__}')
print(f'   Trees: {temp_model.n_estimators}')
print(f'   Max depth: {temp_model.max_depth}')
print(f'   Input features: {temp_model.n_features_in_}')
print(f'   Features: {feature_list}')

print(f'\n📊 Rainfall Model:')
print(f'   Type: {type(rain_model).__name__}')
print(f'   Trees: {rain_model.n_estimators}')
print(f'   Max depth: {rain_model.max_depth}')
print(f'   Input features: {rain_model.n_features_in_}')

# Feature importance
print(f'\n🔍 Temperature - Top 5 Important Features:')
importance = pd.DataFrame({
    'feature': feature_list, 
    'importance': temp_model.feature_importances_
}).sort_values('importance', ascending=False)

for i, (idx, row) in enumerate(importance.head(5).iterrows(), 1):
    print(f'   {i}. {row["feature"]:25s} {row["importance"]:.4f}')

print(f'\n🔍 Rainfall - Top 5 Important Features:')
importance = pd.DataFrame({
    'feature': feature_list, 
    'importance': rain_model.feature_importances_
}).sort_values('importance', ascending=False)

for i, (idx, row) in enumerate(importance.head(5).iterrows(), 1):
    print(f'   {i}. {row["feature"]:25s} {row["importance"]:.4f}')

print(f'\n✅ Models are ready for deployment!')
print(f'   Files in {model_dir}:')
for f in model_dir.glob('*.pkl'):
    print(f'   - {f.name}')

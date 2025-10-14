# src/model_training.py
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import argparse
from preprocessing import run_preprocessing

def model_train(input_path: str, model_path: str, n_estimators: int = 20):
    
    print(f"[INFO] model_train called with input_path={input_path}, model_path={model_path}, n_estimators={n_estimators}")

    # If input file missing, run preprocessing to create it
    if not os.path.exists(input_path):
        print(f"[INFO] input file not found at {input_path}. Running preprocessing to create it.")
        parent_dir = os.path.dirname(input_path) or "."
        os.makedirs(parent_dir, exist_ok=True)
        run_preprocessing(parent_dir)

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"input file still not found after preprocessing: {input_path}")

    # Load data
    df = pd.read_csv(input_path)
    feature_cols = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    if not set(feature_cols).issubset(df.columns):
        raise ValueError(f"Expected feature columns {feature_cols}. Found: {df.columns.tolist()}")
    if 'target' not in df.columns:
        raise ValueError("Expected 'target' column in input CSV.")

    X = df[feature_cols]
    y = df['target']

    # Train / evaluate
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"[INFO] Training complete. Accuracy: {acc:.4f}")

    # Save model
    os.makedirs(model_path, exist_ok=True)
    model_file = os.path.join(model_path, "model.joblib")
    joblib.dump(model, model_file)
    print(f"[INFO] Model saved to: {model_file}")

    return model_file

def parse_args():
    parser = argparse.ArgumentParser
    parser.add_argument(
        "--input-path",
        type=str,
        default="/opt/ml/input/data/train/processed.csv"
        )
    parser.add_argument(
        "--model-path",
        type=str,
        default="/opt/ml/model",
        )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=20,
        help="n_estimators for RandomForest"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    model_train(args.input_path, args.model_path, n_estimators=args.n_estimators)

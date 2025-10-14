import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import argparse

def model_train(input_path,model_path):

 
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"input file not found: {input_path}")
    df = pd.read_csv(input_path)
    X = df[['sepal length (cm)','sepal width (cm)','petal length (cm)','petal width (cm)']]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"Training complete. Accuracy: {acc:.4f}")

    
    os.makedirs(model_path, exist_ok=True)
    model_obj_loc=joblib.dump(model, os.path.join(model_path, "model.joblib"))
    print(f"Model saved to: {model_obj_loc}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-path",
        type=str,
        default="./processed_output/processed.csv")

    parser.add_argument(
        "--model-path",
        type=str,
        default="./model_output")

    args = parser.parse_args()

    model_train(args.input_path, args.model_path)
    model_train()

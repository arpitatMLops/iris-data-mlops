from sklearn.datasets import load_iris
import pandas as pd
import os
import argparse

def load_data(output_dir):
   
    print("Starting preprocessing job...")

    iris = load_iris(as_frame=True)
    df = iris.frame
    df["target"] = iris.target
    
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "processed.csv")
    df.to_csv(out_file, index=False)
    print("Saved processed data to:", out_file)
    print("Shape:", df.shape)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir",
                       type=str,
                       default="./processed_output"
                       )
    args = parser.parse_args()
    load_data(args.output_dir)

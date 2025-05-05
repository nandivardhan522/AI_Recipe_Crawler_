import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "final" / "recipes.csv"

def generate_summary():
    logger.info("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    logger.info("Dataset Stats:")
    print(f"Total recipes: {len(df)}")
    print(f"Recipes with image: {df['image_path'].notna().sum()}")
    print(f"Recipes with video: {df['video_link'].notna().sum()}")

    # Ingredients length distribution
    df["num_ingredients"] = df["ingredients"].apply(lambda x: len(str(x).split("|")))
    df["num_words_instructions"] = df["instructions"].apply(lambda x: len(str(x).split()))

    # Plotting
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    df["num_ingredients"].hist(bins=15)
    plt.title("Number of Ingredients per Recipe")
    plt.xlabel("# Ingredients")
    plt.ylabel("Count")

    plt.subplot(1, 2, 2)
    df["num_words_instructions"].hist(bins=20)
    plt.title("Instruction Length (Words)")
    plt.xlabel("# Words")
    plt.ylabel("Count")

    plt.tight_layout()
    plt.savefig(PROJECT_ROOT / "data" / "final" / "dataset_summary.png")
    logger.success("Saved summary chart to dataset_summary.png")

if __name__ == "__main__":
    generate_summary()

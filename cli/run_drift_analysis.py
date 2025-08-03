
import pandas as pd
from drift_utils import analyze_text

# Configuration
INPUT_CSV = "GoEmotions_1K_Sample.csv"
OUTPUT_CSV = "LLOYD_Phase2_Results.csv"
OUTPUT_JSON = "LLOYD_Phase2_Results.json"
OUTPUT_MD = "LLOYD_Phase2_Results.md"

def main():
    # Load CSV
    df = pd.read_csv(INPUT_CSV)

    # Filter neutral entries only (assuming column named 'neutral' exists)
    neutral_df = df[df.get("neutral", 0) == 1].copy()

    # Run symbolic drift analysis
    results = neutral_df["text"].apply(analyze_text).tolist()
    results_df = pd.DataFrame(results)

    # Save outputs
    results_df.to_csv(OUTPUT_CSV, index=False)
    results_df.to_json(OUTPUT_JSON, orient="records", indent=2)
    with open(OUTPUT_MD, "w") as f:
        f.write(results_df.head(15).to_markdown(index=False))

    print("✅ Drift analysis complete. Files saved:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_MD}")

if __name__ == "__main__":
    main()

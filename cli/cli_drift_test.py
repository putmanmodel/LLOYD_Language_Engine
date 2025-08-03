import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.drift_utils_v2 import analyze_drift, log_drift_result
from engine.token_heatmap import generate_token_heatmap
from utils.display import colorize_label, print_colored_bar
from datetime import datetime
import json

def run_repl(polarity_threshold=0.5, journal=True, export_name=None, use_color=True):
    print("Drift CLI REPL — Enter baseline & incoming phrases (Ctrl+C to exit)")
    session = []

    try:
        while True:
            baseline = input("Baseline: ").strip()
            incoming = input("Incoming: ").strip()
            result = analyze_drift(baseline, incoming, polarity_threshold)

            if use_color:
                print(colorize_label(result.label, result.rationale))
            else:
                print(f"[{result.label.upper()}] {result.rationale}")

            heatmap = generate_token_heatmap(incoming)
            print("Token heatmap:")
            if use_color:
                print_colored_bar(heatmap)
            else:
                print(json.dumps(heatmap, indent=2))

            if journal:
                # pass export_name (string or None) as the file-path arg so
                # log_drift_result’s internal open() always gets a str or None
                log_drift_result(baseline, incoming, result, heatmap, export_name)

            if export_name:
                session.append({
                    "timestamp": datetime.now().isoformat(),
                    "baseline": baseline,
                    "incoming": incoming,
                    "result": {
                        "label": result.label,
                        "rationale": result.rationale,
                        "drift_score": result.drift_score
                    },
                    "heatmap": heatmap,
                })

    except KeyboardInterrupt:
        print("\nExiting.")
        if export_name and session:
            with open(export_name, "w") as f:
                for entry in session:
                    f.write(json.dumps(entry) + "\n")
            print(f"Session exported to {export_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLOYD Drift Detection CLI")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Polarity delta threshold")
    parser.add_argument("--no-journal", action="store_true",
                        help="Disable journal logging")
    parser.add_argument("--export", type=str,
                        help="Export session to JSONL file")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI color output")
    args = parser.parse_args()

    run_repl(
        polarity_threshold=args.threshold,
        journal=not args.no_journal,
        export_name=args.export,
        use_color=not args.no_color,
    )
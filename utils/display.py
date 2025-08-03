# utils/display.py

def colorize_label(label, rationale):
    if label == "NEGATIVE":
        return f"\033[91m[{label}]\033[0m {rationale}"  # Red
    elif label == "POSITIVE":
        return f"\033[92m[{label}]\033[0m {rationale}"  # Green
    elif label == "STABLE":
        return f"\033[93m[{label}]\033[0m {rationale}"  # Yellow
    else:
        return f"[{label}] {rationale}"

def print_colored_bar(heatmap):
    for token in heatmap["tokens"]:
        word = token["word"]
        score = token["score"]
        if score > 0.66:
            color = "\033[91m"  # Red
        elif score > 0.33:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[90m"  # Gray
        print(f"{color}{word}\033[0m", end=" ")
    print()
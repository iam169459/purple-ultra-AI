"""Training and fine-tuning system for Purple Ultra AI."""

from __future__ import annotations

import json
import subprocess
import argparse
from pathlib import Path


class Training:
    def __init__(self, config=None):
        self.config = config

    def export_history(self, history_file: str = "memory/history.jsonl", output_file: str = "training/examples.jsonl", min_user_chars: int = 10) -> int:
        """Export conversation history to training JSONL format."""
        history_path = Path(history_file)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not history_path.exists():
            return 0

        count = 0
        with open(history_path) as hf, open(output_path, "w") as of:
            for line in hf:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    user = entry.get("user", "")
                    assistant = entry.get("assistant", "")
                    if len(user) >= min_user_chars and assistant:
                        row = {
                            "messages": [
                                {"role": "system", "content": "You are Purple Ultra, an advanced AI voice assistant."},
                                {"role": "user", "content": user},
                                {"role": "assistant", "content": assistant},
                            ]
                        }
                        of.write(json.dumps(row) + "\n")
                        count += 1
                except json.JSONDecodeError:
                    continue
        return count

    def add_example(self, dataset_file: str, user: str, assistant: str):
        """Add a manual training example."""
        output_path = Path(dataset_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        row = {
            "messages": [
                {"role": "system", "content": "You are Purple Ultra, an advanced AI voice assistant."},
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ]
        }

        with open(output_path, "a") as f:
            f.write(json.dumps(row) + "\n")

    def train(self, base_model: str = "mlx-community/Qwen2.5-3B-Instruct-4bit", dataset: str = "training/examples.jsonl", output_dir: str = "training/output", iterations: int = 200):
        """Run MLX LoRA fine-tuning on Apple Silicon."""
        dataset_path = Path(dataset)
        if not dataset_path.exists():
            print(f"No dataset found at {dataset}. Run 'export' first.")
            return False

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        cmd = [
            "python3", "-m", "mlx_lm.lora",
            "--model", base_model,
            "--train",
            "--data", str(dataset_path),
            "--output", str(output),
            "--num-layers", "4",
            "--batch-size", "4",
            "--lr", "1e-5",
            "--iterations", str(iterations),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            if result.returncode == 0:
                print(f"Training complete. Output: {output}")
                return True
            else:
                print(f"Training failed: {result.stderr}")
                return False
        except FileNotFoundError:
            print("mlx_lm not found. Install with: pip install mlx-lm")
            return False
        except subprocess.TimeoutExpired:
            print("Training timed out after 1 hour")
            return False


def main():
    parser = argparse.ArgumentParser(description="Purple Ultra AI Training")
    sub = parser.add_subparsers(dest="command")

    export_parser = sub.add_parser("export", help="Export history to training data")
    export_parser.add_argument("--history", default="memory/history.jsonl")
    export_parser.add_argument("--output", default="training/examples.jsonl")
    export_parser.add_argument("--min-chars", type=int, default=10)

    add_parser = sub.add_parser("add-example", help="Add a manual example")
    add_parser.add_argument("--dataset", default="training/examples.jsonl")
    add_parser.add_argument("--user", required=True)
    add_parser.add_argument("--assistant", required=True)

    train_parser = sub.add_parser("train", help="Run LoRA fine-tuning")
    train_parser.add_argument("--model", default="mlx-community/Qwen2.5-3B-Instruct-4bit")
    train_parser.add_argument("--data", default="training/examples.jsonl")
    train_parser.add_argument("--output", default="training/output")
    train_parser.add_argument("--iterations", type=int, default=200)

    args = parser.parse_args()
    t = Training()

    if args.command == "export":
        count = t.export_history(args.history, args.output, args.min_chars)
        print(f"Exported {count} examples")
    elif args.command == "add-example":
        t.add_example(args.dataset, args.user, args.assistant)
        print("Example added")
    elif args.command == "train":
        t.train(args.model, args.data, args.output, args.iterations)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

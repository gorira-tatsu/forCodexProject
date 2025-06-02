"""CLI tool to analyze abstraction level of each sentence using GPT-4o."""
import argparse
import json
import os
import re
from pathlib import Path

try:
    import openai
except ImportError:  # pragma: no cover - openai may not be installed
    openai = None


def split_into_sentences(text: str):
    """Simple sentence splitter using regex."""
    # This regex splits on common English and Japanese sentence terminators.
    sentence_endings = re.compile(r"(?<=[。．.!?])\s*")
    sentences = sentence_endings.split(text.strip())
    # Remove empty strings
    return [s.strip() for s in sentences if s.strip()]


# Few-shot examples for GPT prompting
def _load_few_shot_examples() -> str:
    """Load few-shot examples from fewshot.json if available."""
    path = Path(__file__).with_name("fewshot.json")
    if not path.exists():
        return (
            "文: このプレゼンテーションでは、プロジェクトの目標について説明します。\nレベル: 1\n"
            "文: 雲は気象学において大気中の水滴や氷晶が集まったものです。\nレベル: 2\n"
            "文: 日本経済の構造改革は複数の要因が複雑に絡み合っています。\nレベル: 3\n"
            "文: 存在論的な議論では、存在そのものの定義が問われます。\nレベル: 4\n"
            "文: 意識の本質は何かという問いは哲学の中でも最も抽象的な議論の一つです。\nレベル: 5\n"
        )
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        examples = []
        for item in data:
            sentence = item.get("sentence")
            level = item.get("level")
            if sentence is not None and level is not None:
                examples.append(f"文: {sentence}\nレベル: {level}\n")
        return "".join(examples)
    except Exception:  # pragma: no cover - reading may fail
        return ""


FEW_SHOT_EXAMPLES = _load_few_shot_examples()


SYSTEM_PROMPT = (
    "あなたは与えられた文の抽象度を1から5のレベルで判定するアシスタントです。"
    "数値のみで回答してください。1は最も具体的、5は最も抽象的です。"
)


def analyze_sentence(sentence: str) -> int:
    """Query GPT-4o to analyze abstraction level of a sentence."""
    if openai is None:
        raise RuntimeError("openai package is not available")
    try:
        client = openai.OpenAI()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": FEW_SHOT_EXAMPLES + f"文: {sentence}\nレベル:"},
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        content = response.choices[0].message.content.strip()
        level = int(re.search(r"(\d)", content).group(1))
        return level
    except Exception as exc:
        raise RuntimeError(f"Failed to analyze sentence: {exc}")


def analyze_text(text: str):
    """Analyze each sentence and track which paragraph it belongs to."""
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    results = []
    for p_idx, paragraph in enumerate(paragraphs, start=1):
        sentences = split_into_sentences(paragraph)
        for sentence in sentences:
            level = analyze_sentence(sentence)
            results.append({"sentence": sentence, "level": level, "paragraph": p_idx})
    return results


def _print_ascii_graph(results):
    """Display a simple ASCII graph of abstraction levels."""
    levels = [r["level"] for r in results]
    paragraphs = [r["paragraph"] for r in results]
    max_level = max(levels) if levels else 0
    for lvl in range(max_level, 0, -1):
        row = f"{lvl} | "
        for val in levels:
            row += "#" if val >= lvl else " "
            row += " "
        print(row.rstrip())
    print("    " + "-" * (2 * len(levels)))
    print("     " + " ".join(str(i + 1) for i in range(len(levels))))
    if len(set(paragraphs)) > 1:
        marker = "     "
        for i in range(len(paragraphs)):
            if i and paragraphs[i] != paragraphs[i - 1]:
                marker += "| "
            else:
                marker += "  "
        print(marker.rstrip())


def main():
    parser = argparse.ArgumentParser(description="Analyze abstraction level of sentences.")
    parser.add_argument("input", help="Input text file")
    parser.add_argument("--output", help="Output JSON file", default=None)
    parser.add_argument("--graph", action="store_true", help="Display ASCII graph")
    args = parser.parse_args()

    if openai is None:
        parser.error("openai package is not installed")

    # Check API key from environment
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY environment variable is not set")

    # Read file
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        parser.error(f"Input file not found: {args.input}")

    try:
        results = analyze_text(text)
    except Exception as exc:
        parser.error(str(exc))

    for item in results:
        print(f"{item['sentence']}\tレベル{item['level']}")

    if args.graph:
        _print_ascii_graph(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

# forCodexProject
Test environment for Codex

## Usage

Run the abstraction level analyzer with a text file:

```bash
python abstract_level_analyzer.py input.txt
```

Pass `--graph` to display a simple ASCII chart of abstraction levels.

Set your OpenAI API key in the `OPENAI_API_KEY` environment variable. The
`openai` package must be installed for the analyzer to work.

## Running tests

Unit tests verify the sentence splitting logic and do not require the `openai`
package:

```bash
python -m unittest discover -s tests
```

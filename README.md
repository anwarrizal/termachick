# Pattern Matching CLI

A command-line tool for efficient string pattern matching using automaton-based algorithms.

## Overview

This tool implements the Knuth-Morris-Pratt (KMP) and Aho-Corasick algorithms for efficient string pattern matching. It provides a unified command-line interface that supports:

- Single pattern matching (KMP) and multiple pattern matching (Aho-Corasick)
- Building and saving automata (DFAs) for later reuse
- Reading patterns from command line or from pattern files
- Configurable performance options (precomputed transitions)
- Multiple output formats (text or CSV)

## Installation

### Prerequisites

- Python 3.11 or higher

### Setup

1. Clone the repository:
   ```
   git clone git@github.com:anwarrizal/termachick.git
   cd termachick
   ```

## Usage

The tool provides two main commands:

- `strbuild`: Build and save a pattern matching automaton (DFA)
- `strsearch`: Search for patterns in text

### Building a DFA

Build a DFA from patterns and save it to a file for later use:

```bash
# Build an Aho-Corasick DFA from command-line patterns
python tchick.py strbuild --patterns ABABC BCDEF DEFGH -o patterns.dfa

# Build a KMP DFA from a single pattern
python tchick.py strbuild --patterns ABABC -a kmp -o kmp_pattern.dfa

# Build a DFA from patterns in a file (one pattern per line)
python tchick.py strbuild --patterns-file dna_patterns.txt -o dna.dfa
```

### Searching for Patterns

Search for patterns in text using various input methods:

```bash
# Search using patterns directly with text from a file
python tchick.py strsearch --patterns ABABC BCDEF -f genome.txt

# Search using patterns with text provided directly as an argument
python tchick.py strsearch --patterns ABABC BCDEF -t "ABABCDEFABABC"

# Search using patterns from a file with CSV output
python tchick.py strsearch --patterns-file proteins.txt -f sequence.txt --output-format csv

# Search using a pre-built DFA and save results to a file
python tchick.py strsearch --dfa-file patterns.dfa -f input.txt --output-file results.csv --output-format csv

# Search from stdin and save the DFA for later use
cat input.txt | python tchick.py strsearch --patterns ABABC BCDEF --save-dfa patterns.dfa
```

## Command Reference

### strbuild

Build a string pattern DFA and save it to a file.

```
python tchick.py strbuild [options]
```

Options:
- `--patterns PATTERN [PATTERN ...]`: One or more patterns to build the DFA from
- `--patterns-file FILE`: File containing patterns, one per line
- `-o, --output FILE`: Output file to save the DFA (required)
- `-a, --algorithm {kmp,aho-corasick}`: Algorithm to use (default: aho-corasick)
- `--no-precompute`: Don't precompute transitions (uses less memory but may be slower)
- `--alphabet CHARS`: Explicitly specify the alphabet characters

### strsearch

Search for string patterns in text.

```
python tchick.py strsearch [options]
```

Pattern options (one required):
- `--patterns PATTERN [PATTERN ...]`: One or more patterns to search for
- `--patterns-file FILE`: File containing patterns, one per line
- `--dfa-file FILE`: Load a pre-built DFA from a JSON file

Input text options (one optional, stdin used if none provided):
- `-f, --file FILE`: Input file to search in
- `-t, --text TEXT`: Text to search in (provided directly as an argument)

Other options:
- `-a, --algorithm {kmp,aho-corasick}`: Algorithm to use (default: aho-corasick)
- `--no-precompute`: Don't precompute transitions (uses less memory but may be slower)
- `--alphabet CHARS`: Explicitly specify the alphabet characters
- `--save-dfa FILE`: Save the DFA to a JSON file
- `--output-format {csv,text}`: Output format for search results (default: text)
- `--output-file FILE`: File to write search results to (default: stdout)

## Performance Considerations

- **Algorithm Selection**:
  - Aho-Corasick is for multiple patterns
  - KMP is optimized for single pattern searches

- **Memory vs. Speed**:
  - Precomputed transitions (default) use more memory but are faster
  - Use `--no-precompute` for lower memory usage at the cost of speed

- **DFA Reuse**:
  - Building a DFA can be time-consuming for large pattern sets
  - Save DFAs for reuse to avoid rebuilding the automaton

## Examples

### DNA Pattern Matching

Create a file with DNA patterns:

```
# dna_patterns.txt
GATTACA
TCGA
AAAA
```

Build a DFA and search for these patterns in a genome file:

```bash
# Build the DFA
python tchick.py strbuild --patterns-file dna_patterns.txt -o dna.dfa

```


## Implementation Details

The implementation uses deterministic finite automata (DFA) with failure transitions:

- **KMP Algorithm**: Optimized for single pattern matching y
- **Aho-Corasick Algorithm**: Extends KMP for multiple pattern matching with

Both algorithms use automaton-based approaches that avoid backtracking in the input text, making them highly efficient for large texts and pattern sets.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
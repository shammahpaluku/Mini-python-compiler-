# PyMini LL(1) Parser

A table-driven LL(1) parser for the PyMini programming language with comprehensive error reporting, recovery, and parse tree generation.

## Overview

This project implements a complete LL(1) parser for the PyMini programming language as part of a compiler construction course. The parser features:

- **Table-driven LL(1) parsing algorithm** with hardcoded parse table
- **Comprehensive error reporting** with multi-error collection and recovery
- **Parse tree generation** in multiple formats (ASCII art and Graphviz DOT)
- **Scanner integration** with proper token passing
- **Modular architecture** with separate scanner and parser modules

## Architecture

### Module Structure

The project consists of three main files:

- **`scanner.py`**: Lexical analyzer that tokenizes PyMini source code
- **`parser.py`**: LL(1) table-driven parser with parse tree generation
- **`main.py`**: Integration module that connects scanner and parser

### Parser Implementation Details

The parser uses a stack-based LL(1) algorithm with the following key features:

- **Parse Table**: Hardcoded LL(1) parse table with 16 non-terminals
- **Stack Management**: Stores tuples `(symbol, node)` for parallel tree construction
- **Error Handling**: Collects multiple errors and attempts recovery
- **Parse Tree**: Built during parsing using parallel node stack

## Installation

### Requirements

- Python 3.7 or higher
- Graphviz (optional, for tree visualization)

### Setup

```bash
git clone https://github.com/shammahpaluku/Mini-python-compiler-.git
cd Mini-python-compiler-
```

## Usage

### Running the Parser

To parse a PyMini source file:

```bash
python3 main.py sample_correct.pymini
```

This will:
1. Display the source code
2. Print the token list from the scanner
3. Show the parsing steps and summary
4. Display the parse tree in ASCII art format
5. Generate a Graphviz DOT file for visualization

### Running Scanner Independently

```bash
python3 scanner.py filename.pymini
```

### Programmatic Usage

```python
from scanner import scan
from parser import Parser

# Scan source code
with open('source.pymini', 'r') as f:
    source = f.read()

tokens, errors = scan(source)

# Parse tokens
parser = Parser(tokens)
success = parser.parse()

# Display parse tree
if success:
    parser.print_parse_tree()
```

## Parse Tree Generation

The parser supports multiple parse tree output formats:

### 1. ASCII Art Format (Default)

The parse tree is displayed in terminal-friendly ASCII art format:

```
└── program
    └── statement_list
        ├── statement
        │   └── assignment
        │       ├── IDENTIFIER: x
        │       ├── =: =
        │       └── expression
```

### 2. Graphviz DOT Format

The parser automatically generates a DOT file for professional visualization:

```bash
# DOT file is generated automatically when running main.py
python3 main.py sample_correct.pymini

# Convert DOT to PNG (requires Graphviz)
dot -Tpng sample_correct.dot -o sample_correct.png

# View the image
xdg-open sample_correct.png  # Linux
open sample_correct.png      # macOS
```

### 3. Online Visualization

Upload the generated `.dot` file to online Graphviz viewers:
- [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/)
- [Viz.js](https://viz-js.com/)

### Programmatic DOT Export

```python
from scanner import scan
from parser import Parser

tokens, _ = scan(source_code)
parser = Parser(tokens)
parser.parse()
parser.export_parse_tree_dot('output.dot')
```

## Grammar

The PyMini grammar consists of the following productions:

### Non-terminals

- `<program>`: Start symbol
- `<statement_list>`: List of statements
- `<statement>`: Individual statement (assignment, if, while, print)
- `<assignment>`: Variable assignment
- `<if_statement>`: Conditional statement
- `<while_statement>`: Loop statement
- `<print_statement>`: Output statement
- `<expression>`: Expression hierarchy
- `<logical_expression>`: Logical operations
- `<comparison_expression>`: Comparisons
- `<arithmetic_expression>`: Arithmetic operations
- `<term>`, `<factor>`: Expression components
- `<logical_tail>`, `<comparison_tail>`, `<arithmetic_tail>`: Expression continuations
- `<else_clause>`: Optional else branch

### Terminals

- **Keywords**: `if`, `while`, `print`, `else`, `and`
- **Operators**: `+`, `-`, `<`, `=`
- **Delimiters**: `:`, `(`, `)`
- **Tokens**: `IDENTIFIER`, `NUMBER`, `STRING`, `BOOLEAN`
- **EOF**: `$`

## Error Handling

The parser implements comprehensive error handling:

### Error Types

1. **Unexpected Token Error**: Token doesn't match expected terminal
2. **No Production Error**: No parse table entry for non-terminal/terminal pair
3. **Unexpected End of Input**: EOF reached with non-terminals remaining on stack

### Error Recovery

- Continues parsing after errors
- Skips unexpected tokens
- Collects all errors in a single run
- Provides detailed error context (line, column, expected tokens)

## Sample Program

A correct PyMini program demonstrating all language features:

```python
x = 5
print(x)

y = 10
if x < y:
    x = y

a = 1
b = 2
c = a + b
print(c)

flag = True
if flag:
    result = "yes"
else:
    result = "no"
print(result)
```

### Parsing Statistics

- **Total parsing steps**: 218
- **Tokens processed**: 51
- **Errors collected**: 0
- **Error recoveries**: 0
- **Production applications**: 166

## Parse Table

The parser uses a hardcoded LL(1) parse table. Key entries include:

```
<program>:
  if, while, print, IDENTIFIER → <statement_list>

<statement_list>:
  if, while, print, IDENTIFIER → <statement> <statement_list>
  else, ), $ → ε

<expression>:
  IDENTIFIER, NUMBER, STRING, BOOLEAN → <logical_expression>

<arithmetic_expression>:
  IDENTIFIER, NUMBER, STRING, BOOLEAN → <term> <arithmetic_tail>

<arithmetic_tail>:
  + → + <term> <arithmetic_tail>
  -, <, and, :, ), else, $ → ε
```

## Implementation Notes

### Assignment Compliance

This implementation meets the following assignment requirements:

1. **Parser Implementation**: Complete table-driven LL(1) parser
2. **Scanner Integration**: Receives tokens from scanner module
3. **Parse Tree Generation**: Multiple output formats (ASCII and DOT)
4. **Error Handling**: Comprehensive error messages with recovery
5. **Grammar Compliance**: Full implementation of mini-grammar
6. **Runtime Demonstration**: Command-line interface with full output

### Key Design Decisions

1. **Tuple-based Stack**: Stores `(symbol, node)` tuples for efficient tree construction
2. **Epsilon Visibility**: Epsilon productions shown as explicit tree nodes
3. **Symbol Formatting**: Angle brackets removed from non-terminals for readability
4. **Quote Escaping**: Proper DOT format escaping for string literals
5. **Modular Design**: Separate scanner and parser for independent testing

## License

This project is part of a compiler construction course assignment.

## Author

Shammah Paluku

## Acknowledgments

Developed as part of a compiler construction course assignment demonstrating LL(1) parsing techniques.

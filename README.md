# PyMini LL(1) Parser

A minimal table-driven LL(1) parser for PyMini language with hardcoded parse table.

## Files (2 total)

- **scanner.py** - Lexical analyzer with grammar definitions
- **parser.py** - LL(1) table-driven parser with error handling

## Usage

### Scanner independently:
```bash
python3 scanner.py filename.pymini
```

### Parser independently:
```bash
python3 parser.py filename.pymini
```

### Programmatic usage:
```python
from scanner import scan, is_terminal, is_non_terminal
from parser import create_parser

# Scan
tokens, errors = scan(code)

# Parse
parser = create_parser(code)
success = parser.parse()
```

## Features

- ✅ **2 files only** - scanner.py and parser.py
- ✅ **Independent execution** - both run standalone
- ✅ **Hardcoded LL(1) parse table** - no auto-generation
- ✅ **Stack-based parsing algorithm** - standard LL(1) implementation
- ✅ **Step-by-step parsing trace** - complete debugging output
- ✅ **Comprehensive error reporting** - multiple error collection
- ✅ **Error recovery** - continues parsing after errors
- ✅ **Self-contained** - all functionality merged into 2 files

## Parse Table

The parser uses a hardcoded LL(1) parse table with entries for `PARSE_TABLE[non_terminal][terminal]`:

### Program Level
```
<program>:
  if:         [<statement_list>]
  while:      [<statement_list>]
  print:      [<statement_list>]
  IDENTIFIER: [<statement_list>]
```

### Statement List Level
```
<statement_list>:
  if:         [<statement>, <statement_list>]
  while:      [<statement>, <statement_list>]
  print:      [<statement>, <statement_list>]
  IDENTIFIER: [<statement>, <statement_list>]
  else:       [ε]
  $:          [ε]
```

### Statement Level
```
<statement>:
  if:         [<if_statement>]
  while:      [<while_statement>]
  print:      [<print_statement>]
  IDENTIFIER: [<assignment>]
```

### Assignment Level
```
<assignment>:
  IDENTIFIER: [IDENTIFIER, =, <expression>]
```

### Control Statements
```
<if_statement>:
  if: [if, <expression>, :, <statement_list>, <else_clause>]

<while_statement>:
  while: [while, <expression>, :, <statement_list>]

<print_statement>:
  print: [print, (, <expression>, )]
```

### Expression Levels
```
<expression>:
  IDENTIFIER: [<logical_expression>]
  NUMBER:     [<logical_expression>]
  STRING:     [<logical_expression>]
  BOOLEAN:    [<logical_expression>]

<logical_expression>:
  IDENTIFIER: [<comparison_expression>, <logical_tail>]
  NUMBER:     [<comparison_expression>, <logical_tail>]
  STRING:     [<comparison_expression>, <logical_tail>]
  BOOLEAN:    [<comparison_expression>, <logical_tail>]

<logical_tail>:
  and: [and, <comparison_expression>, <logical_tail>]
  ::   [ε]
  ):   [ε]
  else:[ε]
  $:   [ε]

<comparison_expression>:
  IDENTIFIER: [<arithmetic_expression>, <comparison_tail>]
  NUMBER:     [<arithmetic_expression>, <comparison_tail>]
  STRING:     [<arithmetic_expression>, <comparison_tail>]
  BOOLEAN:    [<arithmetic_expression>, <comparison_tail>]

<comparison_tail>:
  <:   [<, <arithmetic_expression>]
  and: [ε]
  ::   [ε]
  ):   [ε]
  else:[ε]
  $:   [ε]

<arithmetic_expression>:
  IDENTIFIER: [<term>, <arithmetic_tail>]
  NUMBER:     [<term>, <arithmetic_tail>]
  STRING:     [<term>, <arithmetic_tail>]
  BOOLEAN:    [<term>, <arithmetic_tail>]

<arithmetic_tail>:
  +:   [+, <term>, <arithmetic_tail>]
  -:   [-, <term>, <arithmetic_tail>]
  <:   [ε]
  and: [ε]
  ::   [ε]
  ):   [ε]
  else:[ε]
  $:   [ε]

<term>:
  IDENTIFIER: [IDENTIFIER]
  NUMBER:     [NUMBER]
  STRING:     [STRING]
  BOOLEAN:    [BOOLEAN]

<else_clause>:
  else: [else, :, <statement_list>]
  if:   [ε]
  while:[ε]
  print:[ε]
  IDENTIFIER: [ε]
  $:    [ε]
```

### Terminal Matching Rules
- **Token Types**: `IDENTIFIER`, `NUMBER`, `STRING`, `BOOLEAN` - matched against token type
- **Keywords/Operators**: `if`, `while`, `print`, `else`, `and`, `+`, `-`, `<`, `=`, `:`, `(`, `)` - matched against lexeme
- **EOF**: `$` - end of input marker
- **Epsilon**: `ε` - empty production (pop stack, push nothing)

## Sample Correct Program

Here's a PyMini program that follows the grammar rules correctly:

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

### What Makes This Program Correct:

1. **Proper Assignments**: `IDENTIFIER = <expression>`
2. **Valid Print Statements**: `print(<expression>)` with parentheses
3. **Correct Conditionals**: `if <expression> : <statement_list>`
4. **Valid Expressions**: Uses `<arithmetic_expression>` and `<comparison_expression>` rules
5. **Boolean Handling**: Uses `BOOLEAN` tokens correctly
6. **String Literals**: Proper `STRING` token usage

### Actual Parsing Results:

- **Total steps**: 218 parsing operations
- **Tokens processed**: 51 (100% matched)
- **Errors collected**: 0 (perfect parsing)
- **Error recoveries**: 0 (no recovery needed)
- **Production applications**: 166 (complete grammar application)

### Expected Parser Behavior:

- **Tokenization**: All tokens recognized correctly
- **Stack Operations**: Proper push/pop sequence  
- **Production Applications**: Grammar rules applied correctly
- **Error-Free Parsing**: Zero syntax errors
- **Complete Trace**: Step-by-step parsing visible

## Parser Output

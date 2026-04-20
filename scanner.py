import sys
from datetime import datetime
from collections import Counter

OUTPUT_FILE = "lexer_output.txt"

KEYWORDS = {"if", "else", "while", "print"}
BOOLEANS = {"True", "False"}
WORD_OPERATORS = {"and"}
SYMBOL_OPERATORS = {"+", "-", "<", "=", ">"}
DELIMITERS = {":", "(", ")", ","}

# Grammar definitions
START_SYMBOL = "<program>"
EPSILON = "ε"

TERMINALS = {
    "if", "else", "while", "print", "and",
    "=", ":", "(", ")", "+", "-", "<",
    "IDENTIFIER", "NUMBER", "STRING", "BOOLEAN"
}

NON_TERMINALS = {
    "<program>", "<statement_list>", "<statement>", "<assignment>",
    "<if_statement>", "<while_statement>", "<print_statement>",
    "<expression>", "<logical_expression>", "<logical_tail>",
    "<comparison_expression>", "<comparison_tail>",
    "<arithmetic_expression>", "<arithmetic_tail>",
    "<term>", "<else_clause>"
}

def is_terminal(symbol: str) -> bool:
    """Check if symbol is a terminal."""
    return symbol in TERMINALS

def is_non_terminal(symbol: str) -> bool:
    """Check if symbol is a non-terminal."""
    return symbol in NON_TERMINALS


def is_letter(ch):
    return ch.isalpha() or ch == "_"


def is_digit(ch):
    return ch.isdigit()


def is_alnum_or_underscore(ch):
    return ch.isalnum() or ch == "_"


def scan(code):
    tokens = []
    errors = []
    i = 0
    line = 1
    col = 1
    length = len(code)

    while i < length:
        ch = code[i]

        # Skip spaces/tabs/carriage returns
        if ch in " \t\r":
            i += 1
            col += 1
            continue

        # Newline
        if ch == "\n":
            i += 1
            line += 1
            col = 1
            continue

        start_line = line
        start_col = col

        # IDENTIFIER / KEYWORD / BOOLEAN / word-operator
        if is_letter(ch):
            lexeme = ch
            i += 1
            col += 1

            while i < length and is_alnum_or_underscore(code[i]):
                lexeme += code[i]
                i += 1
                col += 1

            if lexeme in KEYWORDS:
                token_type = "KEYWORD"
            elif lexeme in BOOLEANS:
                token_type = "BOOLEAN"
            elif lexeme in WORD_OPERATORS:
                token_type = "OPERATOR"
            else:
                token_type = "IDENTIFIER"

            tokens.append((token_type, lexeme, start_line, start_col))
            continue

        # NUMBER
        if is_digit(ch):
            lexeme = ch
            i += 1
            col += 1

            while i < length and is_digit(code[i]):
                lexeme += code[i]
                i += 1
                col += 1

            tokens.append(("NUMBER", lexeme, start_line, start_col))
            continue

        # STRING
        if ch == '"':
            lexeme = ch
            i += 1
            col += 1
            string_start_line = start_line
            string_start_col = start_col

            while i < length and code[i] != '"':
                if code[i] == "\n":
                    errors.append(f"Unterminated string starting at line {string_start_line}, column {string_start_col}")
                    # Skip to next line to continue scanning
                    i += 1
                    line += 1
                    col = 1
                    break
                lexeme += code[i]
                i += 1
                col += 1

            if i >= length and code[i-1] != '"':
                errors.append(f"Unterminated string starting at line {string_start_line}, column {string_start_col}")
                break

            if i < length and code[i] == '"':
                lexeme += code[i]  # closing quote
                i += 1
                col += 1
                tokens.append(("STRING", lexeme, start_line, start_col))
            continue

        # Symbol operators
        if ch in SYMBOL_OPERATORS:
            tokens.append(("OPERATOR", ch, start_line, start_col))
            i += 1
            col += 1
            continue

        # Delimiters
        if ch in DELIMITERS:
            tokens.append(("DELIMITER", ch, start_line, start_col))
            i += 1
            col += 1
            continue

        # Unknown character - record error and continue
        errors.append(f"Unexpected character '{ch}' at line {line}, column {col}")
        i += 1
        col += 1

    return tokens, errors


def format_report(tokens, code, source_name, errors=None):
    counts = Counter(token_type for token_type, _, _, _ in tokens)
    lines = code.splitlines()

    out = []
    out.append("====================================================================")
    out.append("  PyMini Mini-Compiler  -  Lexical Analyser (DFA)")
    out.append("  Group 14")
    out.append("====================================================================")
    out.append(f"  Source : {source_name}")
    out.append("  Method : Hand-coded DFA (explicit state transitions, no regex)")
    out.append("  Source program:")
    out.append("  --------------------------------------------------------------")

    if lines:
        for line in lines:
            out.append(f"  {line}")
    else:
        out.append("  <empty input>")

    out.append("  --------------------------------------------------------------")
    out.append("  Token stream:")
    out.append("==================================================================")
    out.append("    #  TOKEN TYPE      LEXEME              LINE   COL")
    out.append("==================================================================")

    for idx, (token_type, lexeme, line, col) in enumerate(tokens, start=1):
        out.append(
            f"  {idx:>3}  {token_type:<14} {repr(lexeme):<18} {line:>5} {col:>5}"
        )

    out.append("==================================================================")
    out.append(f"  Total tokens: {len(tokens)}")
    out.append("==================================================================")
    out.append("  Token-type summary:")
    out.append("  Type            Count")
    out.append("  ----------------------")

    order = ["BOOLEAN", "DELIMITER", "IDENTIFIER", "KEYWORD", "NUMBER", "OPERATOR", "STRING"]
    for token_type in order:
        if counts[token_type] > 0:
            out.append(f"  {token_type:<15} {counts[token_type]:>5}")

    out.append("  ----------------------")
    out.append(f"  TOTAL           {len(tokens):>5}")

    if errors:
        out.append("==================================================================")
        out.append(f"  LEXICAL ERRORS ({len(errors)} found):")
        for i, error in enumerate(errors, 1):
            out.append(f"  {i}. {error}")
        out.append("==================================================================")

    return "\n".join(out)


def write_output(report):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("=====\n")
        f.write(f"Run at: {datetime.now()}\n")
        f.write(report)
        f.write("\n\n")


def read_input():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, "r", encoding="utf-8") as f:
            return f.read(), filename
    else:
        print("Enter source code. Press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows) to finish:\n")
        return sys.stdin.read(), "<terminal input>"


def main():
    try:
        code, source_name = read_input()
        tokens, errors = scan(code)
        report = format_report(tokens, code, source_name, errors)

        print(report)
        write_output(report)

        print(f"\nOutput also appended to {OUTPUT_FILE}")

    except FileNotFoundError as e:
        print(f"Error: file not found - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
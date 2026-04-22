"""
Table-Driven LL(1) Parser

Implements a table-driven LL(1) parser for PyMini language.
Uses hardcoded parse table to perform syntactic analysis.
"""

from typing import List, Tuple, Optional, Dict
from scanner import scan, is_terminal, is_non_terminal

class ParseTreeNode:
    """Node in the parse tree representing a grammar symbol or terminal."""
    
    def __init__(self, symbol, children=None, token=None):
        self.symbol = symbol        # grammar symbol e.g. "<statement>" or "IDENTIFIER"
        self.children = children or []
        self.token = token          # actual token value for terminals e.g. "x", "5", "if"
    
    def print_tree(self, prefix="", is_last=True):
        """Print the parse tree with ASCII art connectors."""
        connector = "└── " if is_last else "├── "
        
        if self.token:
            print(prefix + connector + f"{self.symbol}: {self.token}")
        else:
            print(prefix + connector + self.symbol)

        new_prefix = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            child.print_tree(new_prefix, is_last_child)

# Error handling classes
class ParseError(Exception):
    """Base class for parsing errors."""
    def __init__(self, message: str, line: int = None, column: int = None, lexeme: str = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.lexeme = lexeme
    
    def __str__(self):
        if self.line is not None:
            return f"ParseError at line {self.line}, column {self.column}: {self.message}"
        return f"ParseError: {self.message}"

class UnexpectedTokenError(ParseError):
    """Error when unexpected token encountered."""
    def __init__(self, token: str, line: int, column: int, lexeme: str, expected_terminal: str):
        message = f"Unexpected token '{token}', expected '{expected_terminal}'"
        super().__init__(message, line, column, lexeme)
        self.token = token
        self.expected_terminal = expected_terminal

class NoProductionError(ParseError):
    """Error when no production found in parse table."""
    def __init__(self, non_terminal: str, terminal: str, line: int, column: int, lexeme: str):
        message = f"No production found for <<{non_terminal}>> with token '{terminal}'"
        super().__init__(message, line, column, lexeme)
        self.non_terminal = non_terminal
        self.terminal = terminal

class UnexpectedEndOfInputError(ParseError):
    """Error when input ends unexpectedly."""
    def __init__(self, expected_non_terminal: str = None):
        message = f"Unexpected end of input while expecting <<{expected_non_terminal}>>"
        super().__init__(message)
        self.expected_non_terminal = expected_non_terminal

class ParseErrorCollector:
    """Collects and manages multiple parsing errors."""
    def __init__(self):
        self.errors = []
    
    def add_error(self, error: ParseError):
        """Add an error to the collection."""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self.errors) > 0
    
    def print_error_summary(self):
        """Print a summary of all collected errors."""
        if not self.has_errors():
            print("✅ No parsing errors found.")
            return
        
        print("❌ PARSING ERRORS SUMMARY")
        print("=" * 60)
        print(f"Total errors found: {len(self.errors)}")
        print("-" * 60)
        
        for i, error in enumerate(self.errors, 1):
            print(f"Error {i}:")
            if isinstance(error, (UnexpectedTokenError, NoProductionError)):
                print(f"  {error}")
                print(f"  Expected: expansion of <<{error.non_terminal if hasattr(error, 'non_terminal') else error.expected_terminal}>>")
                print(f"  Found: {error.token if hasattr(error, 'token') else error.lexeme} '{error.lexeme if hasattr(error, 'lexeme') else ''}'")
            else:
                print(f"  {error}")
            print()
        
        print("=" * 60)
        print("SUGGESTIONS:")
        print("-" * 60)
        print("• Check if tokens match the expected grammar symbols")
        print("• Verify that all keywords and operators are spelled correctly")
        print("• Check for incomplete statements or missing closing delimiters")
        print("-" * 60)

# Manually defined parse table - do not auto-generate
START_SYMBOL = "<program>"
PARSE_TABLE: Dict[str, Dict[str, List[str]]] = {
    "<program>": {
        "if":         ["<statement_list>"],
        "while":      ["<statement_list>"],
        "print":      ["<statement_list>"],
        "IDENTIFIER": ["<statement_list>"],
    },

    "<statement_list>": {
        "if":         ["<statement>", "<statement_list>"],
        "while":      ["<statement>", "<statement_list>"],
        "print":      ["<statement>", "<statement_list>"],
        "IDENTIFIER": ["<statement>", "<statement_list>"],
        "else":       ["ε"],
        ")":          ["ε"],
        "$":          ["ε"],
    },

    "<statement>": {
        "if":         ["<if_statement>"],
        "while":      ["<while_statement>"],
        "print":      ["<print_statement>"],
        "IDENTIFIER": ["<assignment>"],
    },

    "<assignment>": {
        "IDENTIFIER": ["IDENTIFIER", "=", "<expression>"],
    },

    "<if_statement>": {
        "if": ["if", "<expression>", ":", "<statement_list>", "<else_clause>"],
    },

    "<else_clause>": {
        "else": ["else", ":", "<statement_list>"],
        "if":   ["ε"],
        "while":["ε"],
        "print":["ε"],
        "IDENTIFIER": ["ε"],
        ")":   ["ε"],
        "$":    ["ε"],
    },

    "<while_statement>": {
        "while": ["while", "<expression>", ":", "<statement_list>"],
    },

    "<print_statement>": {
        "print": ["print", "(", "<expression>", ")"],
    },

    "<expression>": {
        "IDENTIFIER": ["<logical_expression>"],
        "NUMBER":     ["<logical_expression>"],
        "STRING":     ["<logical_expression>"],
        "BOOLEAN":    ["<logical_expression>"],
    },

    "<logical_expression>": {
        "IDENTIFIER": ["<comparison_expression>", "<logical_tail>"],
        "NUMBER":     ["<comparison_expression>", "<logical_tail>"],
        "STRING":     ["<comparison_expression>", "<logical_tail>"],
        "BOOLEAN":    ["<comparison_expression>", "<logical_tail>"],
    },

    "<logical_tail>": {
        "and": ["and", "<comparison_expression>", "<logical_tail>"],
        ":":   ["ε"],
        ")":   ["ε"],
        "else":["ε"],
        "if":  ["ε"],
        "while":["ε"],
        "print":["ε"],
        "IDENTIFIER": ["ε"],
        "$":   ["ε"],
    },

    "<comparison_expression>": {
        "IDENTIFIER": ["<arithmetic_expression>", "<comparison_tail>"],
        "NUMBER":     ["<arithmetic_expression>", "<comparison_tail>"],
        "STRING":     ["<arithmetic_expression>", "<comparison_tail>"],
        "BOOLEAN":    ["<arithmetic_expression>", "<comparison_tail>"],
    },

    "<comparison_tail>": {
        "<":   ["<", "<arithmetic_expression>"],
        "and": ["ε"],
        ":":   ["ε"],
        ")":   ["ε"],
        "else":["ε"],
        "if":  ["ε"],
        "while":["ε"],
        "print":["ε"],
        "IDENTIFIER": ["ε"],
        "$":   ["ε"],
    },

    "<arithmetic_expression>": {
        "IDENTIFIER": ["<term>", "<arithmetic_tail>"],
        "NUMBER":     ["<term>", "<arithmetic_tail>"],
        "STRING":     ["<term>", "<arithmetic_tail>"],
        "BOOLEAN":    ["<term>", "<arithmetic_tail>"],
    },

    "<arithmetic_tail>": {
        "+":   ["+", "<term>", "<arithmetic_tail>"],
        "-":   ["-", "<term>", "<arithmetic_tail>"],
        "<":   ["ε"],
        "and": ["ε"],
        ":":   ["ε"],
        ")":   ["ε"],
        "else":["ε"],
        "if":  ["ε"],
        "while":["ε"],
        "print":["ε"],
        "IDENTIFIER": ["ε"],
        "=":   ["ε"],
        "$":   ["ε"],
    },

    "<term>": {
        "IDENTIFIER": ["IDENTIFIER"],
        "NUMBER":     ["NUMBER"],
        "STRING":     ["STRING"],
        "BOOLEAN":    ["BOOLEAN"],
    },
}


def is_end() -> bool:
    """Check if all tokens are consumed (at EOF marker)."""
    return False  # Will be overridden in Parser class


class Parser:
    """Table-driven LL(1) parser for PyMini with improved error reporting."""
    
    def __init__(self, tokens: List[Tuple[str, str, int, int]]):
        """
        Initialize parser with token stream.
        
        Args:
            tokens: List of (token_type, lexeme, line, column) tuples
        """
        self.tokens = tokens + [('$', '$', -1, -1)]  # Add EOF marker
        self.current_token_index = 0
        self.parse_table = PARSE_TABLE
        self.parsing_steps = []  # For debugging/demonstration
        self.error_collector = ParseErrorCollector()  # Collect multiple errors
        self.parse_tree_root = None  # Root of the parse tree
    
    def is_end(self) -> bool:
        """Check if all tokens are consumed (at EOF marker)."""
        return self.current_token_index >= len(self.tokens) - 1
    
    def _get_terminal_for_matching(self, token_type: str, lexeme: str) -> str:
        """
        Get the terminal string to match against parse table.
        
        Args:
            token_type: Token type from scanner
            lexeme: Token lexeme from scanner
            
        Returns:
            Terminal string for parse table lookup
        """
        # IDENTIFIER, NUMBER, STRING, BOOLEAN are matched against token type
        if token_type in ['IDENTIFIER', 'NUMBER', 'STRING', 'BOOLEAN']:
            return token_type
        
        # Keywords and operators are matched against lexeme (value)
        return lexeme
    
    @property
    def current_token(self) -> Tuple[str, str, int, int]:
        """Get current token."""
        return self.tokens[self.current_token_index]
    
    @property
    def current_token_type(self) -> str:
        """Get current token type."""
        return self.current_token[0]
    
    @property
    def current_lexeme(self) -> str:
        """Get current lexeme."""
        return self.current_token[1]
    
    @property
    def current_line(self) -> int:
        """Get current line number."""
        return self.current_token[2]
    
    @property
    def current_column(self) -> int:
        """Get current column number."""
        return self.current_token[3]
    
    def parse(self) -> bool:
        """
        Parse token stream using table-driven LL(1) algorithm.
        Collects all errors instead of stopping at first one.
        Builds parse tree during parsing using (symbol, node) tuples on stack.
        
        Returns:
            True if parsing completed successfully, False otherwise
        
        Raises:
            ParseError: If critical parsing error occurs
        """
        # Initialize parsing stack with [(symbol, node)] tuples
        # $ at bottom, start symbol on top
        root_node = ParseTreeNode(START_SYMBOL)
        stack = [('$', ParseTreeNode('$')), (START_SYMBOL, root_node)]
        self.parse_tree_root = root_node
        
        # Record initial state
        current_terminal = self._get_terminal_for_matching(self.current_token_type, self.current_lexeme)
        self._record_step(stack, current_terminal, "Initialize", None)
        
        while len(stack) > 1:
            X, current_node = stack[-1]  # Top of stack: (symbol, node)
            t = self._get_terminal_for_matching(self.current_token_type, self.current_lexeme)  # Current input terminal
            
            # Case 1: X == t == $: parsing successful
            if X == t == '$':
                self._record_step(stack, t, "Accept", None)
                break
            
            # Case 2: X is a terminal
            elif is_terminal(X):
                if X == t:
                    # Match: pop stack, advance input, attach token value to node
                    stack.pop()
                    current_node.token = self.current_lexeme
                    self._advance_input()
                    action = f"Match terminal '{X}'"
                else:
                    # Mismatch: unexpected token
                    error = UnexpectedTokenError(
                        token=t,
                        line=self.current_line,
                        column=self.current_column,
                        lexeme=self.current_lexeme,
                        expected_terminal=X
                    )
                    self.error_collector.add_error(error)
                    # Try to recover by skipping the unexpected token
                    self._advance_input()
                    action = f"Error recovery: skip unexpected token '{t}'"
            
            # Case 3: X is a non-terminal
            elif is_non_terminal(X):
                # Look up production in parse table
                production = self._get_table_entry(X, t)
                
                if production == ['error']:
                    # No production found
                    error = NoProductionError(
                        non_terminal=X,
                        terminal=t,
                        line=self.current_line,
                        column=self.current_column,
                        lexeme=self.current_lexeme
                    )
                    self.error_collector.add_error(error)
                    # Try to recover by skipping the unexpected token
                    self._advance_input()
                    action = f"Error recovery: no production for <{X}> with '{t}'"
                else:
                    # Found production: pop X, push production symbols in REVERSE order
                    stack.pop()
                    
                    # Build parse tree for this production
                    child_nodes = []
                    for symbol in production:
                        if symbol != 'ε':  # Skip epsilon
                            child_node = ParseTreeNode(symbol)
                            current_node.children.append(child_node)
                            child_nodes.append(child_node)
                    
                    # Push (symbol, node) tuples in reverse order to preserve correct parsing order
                    for symbol, child in reversed(list(zip(production, child_nodes))):
                        if symbol != 'ε':  # Skip epsilon
                            stack.append((symbol, child))
                    
                    action = f"Apply {X} -> {' '.join(production)}"
            
            else:
                error = ParseError(
                    f"Invalid symbol on stack: '{X}'",
                    line=self.current_line,
                    column=self.current_column
                )
                self.error_collector.add_error(error)
                break
            
            # Record step
            self._record_step(stack, t, action, production if 'production' in locals() else None)
        
        # Check for unexpected end of input
        if len(stack) > 1 and self.is_end():
            # Find the top non-terminal that was expected
            top_non_terminal = None
            for symbol, _ in reversed(stack):
                if is_non_terminal(symbol):
                    top_non_terminal = symbol
                    break
            
            error = UnexpectedEndOfInputError(
                expected_non_terminal=top_non_terminal
            )
            self.error_collector.add_error(error)
        
        # Print error summary if any errors were collected
        if self.error_collector.has_errors():
            self.error_collector.print_error_summary()
        
        # Return success status
        return not self.error_collector.has_errors()
    
    def _get_table_entry(self, non_terminal: str, terminal: str) -> List[str]:
        """
        Get production from hardcoded parse table.
        
        Args:
            non_terminal: Non-terminal symbol
            terminal: Terminal symbol
            
        Returns:
            Production list or ['error'] if no entry
        """
        return self.parse_table.get(non_terminal, {}).get(terminal, ['error'])
    
    def _advance_input(self):
        """Advance to next input token."""
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
    
    def _record_step(self, stack: List[tuple], token: str, action: str, production: Optional[List[str]]):
        """
        Record a parsing step for debugging/demonstration.
        
        Args:
            stack: Current parsing stack with (symbol, node) tuples
            token: Current input token
            action: Action taken
            production: Production applied (if any)
        """
        # Extract symbols from tuples for display
        stack_symbols = [symbol for symbol, _ in stack]
        step = {
            'stack': stack_symbols,
            'token': token,
            'action': action,
            'production': production.copy() if production else None,
            'input_position': self.current_token_index
        }
        self.parsing_steps.append(step)
    
    def print_steps(self):
        """
        Print each parsing step showing stack state, current input token, and action.
        This is required for the demo.
        """
        print("\n" + "="*100)
        print("PARSING STEPS")
        print("="*100)
        
        # Header
        print(f"{'Step':<6} {'Stack':<30} {'Input Token':<15} {'Action':<40}")
        print("-" * 100)
        
        for i, step in enumerate(self.parsing_steps):
            # Format stack (show top at right)
            stack_str = " ".join(step['stack'])
            if len(stack_str) > 28:
                stack_str = stack_str[-28:]  # Show last 28 chars
            
            # Format action
            action = step['action']
            if step['production']:
                prod_str = " ".join(step['production'])
                action += f" ({prod_str})"
            
            print(f"{i:<6} {stack_str:<30} {step['token']:<15} {action:<40}")
        
        print("="*100)
    
    def print_parse_summary(self):
        """Print a summary of parsing process."""
        print("\nPARSING SUMMARY:")
        print("-" * 40)
        print(f"Total steps: {len(self.parsing_steps)}")
        print(f"Tokens processed: {self.current_token_index}")
        print(f"Parse table size: {len(self.parse_table) if self.parse_table else 0} non-terminals")
        print(f"Errors collected: {len(self.error_collector.errors)}")
        
        # Count different types of actions
        actions = [step['action'] for step in self.parsing_steps]
        matches = sum(1 for a in actions if 'Match' in a)
        productions = sum(1 for a in actions if 'Apply' in a)
        errors = sum(1 for a in actions if 'Error' in a)
        
        print(f"Terminal matches: {matches}")
        print(f"Production applications: {productions}")
        print(f"Error recoveries: {errors}")
    
    def print_parse_tree(self):
        if self.parse_tree_root:
            self.parse_tree_root.print_tree()
        else:
            print("No parse tree available")


# Utility functions for creating parser
def create_parser(source_code: str) -> Parser:
    """
    Create a parser from source code.
    
    Args:
        source_code: PyMini source code string
        
    Returns:
        Parser instance ready for parsing
        
    Raises:
        ParseError: If lexical analysis fails
    """
    tokens, lexical_errors = scan(source_code)
    
    if lexical_errors:
        error_msg = "Lexical errors found:\n" + "\n".join(f"  {e}" for e in lexical_errors)
        raise ParseError(error_msg)
    
    return Parser(tokens)


def parse_file(filename: str) -> bool:
    """
    Parse a PyMini file.
    
    Args:
        filename: Path to PyMini source file
        
    Returns:
        True if parsing succeeded, False otherwise
        
    Raises:
        ParseError: If parsing fails
        FileNotFoundError: If file doesn't exist
    """
    with open(filename, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    parser = create_parser(source_code)
    return parser.parse()


def parse_string(source_code: str) -> bool:
    """
    Parse a PyMini source code string.
    
    Args:
        source_code: PyMini source code string
        
    Returns:
        True if parsing succeeded, False otherwise
        
    Raises:
        ParseError: If parsing fails
    """
    parser = create_parser(source_code)
    return parser.parse()



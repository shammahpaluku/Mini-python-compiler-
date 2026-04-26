"""
Table-Driven LL(1) Parser

Implements a table-driven LL(1) parser for PyMini language.
Uses hardcoded parse table to perform syntactic analysis.
"""

from typing import List, Tuple, Optional, Dict
from scanner import scan, is_terminal, is_non_terminal

class ParseTreeNode:
    def __init__(self, symbol, children=None, token=None):
        self.symbol = symbol
        self.children = children or []
        self.token = token
    
    @staticmethod
    def clean_symbol(symbol):
        if symbol.startswith("<") and symbol.endswith(">"):
            return symbol[1:-1]
        return symbol
    
    @staticmethod
    def get_display_label(node):
        if node.token is not None:
            if node.symbol in ["IDENTIFIER", "NUMBER", "STRING", "BOOLEAN"]:
                return node.token
            return node.symbol
        if node.symbol.startswith("<") and node.symbol.endswith(">"):
            return node.symbol[1:-1]
        return node.symbol
    
    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        label = ParseTreeNode.get_display_label(self)
        print(prefix + connector + label)

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            child.print_tree(new_prefix, is_last_child)
    
    def to_dot(self, file):
        node_id = id(self)
        label = ParseTreeNode.get_display_label(self)
        label = label.replace('"', '\\"')
        file.write(f'{node_id} [label="{label}"];\n')

        for child in self.children:
            child_id = id(child)
            file.write(f"{node_id} -> {child_id};\n")
            child.to_dot(file)
    
    def print_horizontal(self):
        self._print_horizontal_recursive(0, "")
    
    def _print_horizontal_recursive(self, depth, prefix):
        label = ParseTreeNode.get_display_label(self)
        print(prefix + label)
        if self.children:
            for i, child in enumerate(self.children):
                is_last = (i == len(self.children) - 1)
                new_prefix = prefix + ("  " if is_last else "│ ")
                child._print_horizontal_recursive(depth + 1, new_prefix)

class ParseError(Exception):
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
    def __init__(self, token: str, line: int, column: int, lexeme: str, expected_terminal: str):
        message = f"Unexpected token '{token}', expected '{expected_terminal}'"
        super().__init__(message, line, column, lexeme)
        self.token = token
        self.expected_terminal = expected_terminal

class NoProductionError(ParseError):
    def __init__(self, non_terminal: str, terminal: str, line: int, column: int, lexeme: str):
        message = f"No production found for <<{non_terminal}>> with token '{terminal}'"
        super().__init__(message, line, column, lexeme)
        self.non_terminal = non_terminal
        self.terminal = terminal

class UnexpectedEndOfInputError(ParseError):
    def __init__(self, expected_non_terminal: str = None):
        message = f"Unexpected end of input while expecting <<{expected_non_terminal}>>"
        super().__init__(message)
        self.expected_non_terminal = expected_non_terminal

class ParseErrorCollector:
    def __init__(self):
        self.errors = []
    
    def add_error(self, error: ParseError):
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def print_error_summary(self):
        if not self.has_errors():
            print("[OK] No parsing errors found.")
            return
        
        print("[ERROR] PARSING ERRORS SUMMARY")
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
        print("- Check if tokens match the expected grammar symbols")
        print("- Verify that all keywords and operators are spelled correctly")
        print("- Check for incomplete statements or missing closing delimiters")
        print("-" * 60)

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
        "DEDENT":     ["ε"],
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
        "if": ["if", "<expression>", ":", "INDENT", "<statement_list>", "DEDENT", "<else_clause>"],
    },
    "<else_clause>": {
        "else": ["else", ":", "INDENT", "<statement_list>", "DEDENT"],
        "if":   ["ε"],
        "while":["ε"],
        "print":["ε"],
        "IDENTIFIER": ["ε"],
        ")":   ["ε"],
        "$":    ["ε"],
    },
    "<while_statement>": {
        "while": ["while", "<expression>", ":", "INDENT", "<statement_list>", "DEDENT"],
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
        "DEDENT": ["ε"],
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
        "DEDENT": ["ε"],
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
        "DEDENT": ["ε"],
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
    return False

class Parser:
    def __init__(self, tokens: List[Tuple[str, str, int, int]]):
        self.tokens = tokens + [('$', '$', -1, -1)]
        self.current_token_index = 0
        self.parse_table = PARSE_TABLE
        self.parsing_steps = []
        self.error_collector = ParseErrorCollector()
        self.parse_tree_root = None
    
    def is_end(self) -> bool:
        return self.current_token_index >= len(self.tokens) - 1
    
    def _get_terminal_for_matching(self, token_type: str, lexeme: str) -> str:
        if token_type in ['IDENTIFIER', 'NUMBER', 'STRING', 'BOOLEAN', 'INDENT', 'DEDENT']:
            return token_type
        return lexeme
    
    @property
    def current_token(self) -> Tuple[str, str, int, int]:
        return self.tokens[self.current_token_index]
    
    @property
    def current_token_type(self) -> str:
        return self.current_token[0]
    
    @property
    def current_lexeme(self) -> str:
        return self.current_token[1]
    
    @property
    def current_line(self) -> int:
        return self.current_token[2]
    
    @property
    def current_column(self) -> int:
        return self.current_token[3]
    
    def _perform_panic_recovery(self, stack):
        sync_terminals = {"if", "while", "print", "IDENTIFIER", "DEDENT", "$"}
        sync_non_terminals = {"<statement_list>", "<statement>", "<program>", "$"}
        
        while not self.is_end():
            t_term = self._get_terminal_for_matching(self.current_token_type, self.current_lexeme)
            if t_term in sync_terminals:
                break
            self._advance_input()
            
        while len(stack) > 1 and stack[-1][0] not in sync_non_terminals:
            stack.pop()
    
    def parse(self) -> bool:
        root_node = ParseTreeNode(START_SYMBOL)
        stack = [('$', ParseTreeNode('$')), (START_SYMBOL, root_node)]
        self.parse_tree_root = root_node
        
        current_terminal = self._get_terminal_for_matching(self.current_token_type, self.current_lexeme)
        self._record_step(stack, current_terminal, "Initialize", None)
        
        while len(stack) > 1:
            # Layer 1: Error Thresholding
            if len(self.error_collector.errors) >= 3:
                self.error_collector.add_error(ParseError("Error threshold reached. Aborting parsing.", self.current_line, self.current_column))
                break

            X, current_node = stack[-1]
            t = self._get_terminal_for_matching(self.current_token_type, self.current_lexeme)
            
            if X == t == '$':
                self._record_step(stack, t, "Accept", None)
                break
            
            elif is_terminal(X):
                if X == t:
                    stack.pop()
                    current_node.token = self.current_lexeme
                    self._advance_input()
                    action = f"Match terminal '{X}'"
                # Layer 3: Phrase-Level Insertion
                elif X == ":" and t == "INDENT":
                    error = ParseError("Missing expected ':' before indented block", self.current_line, self.current_column)
                    self.error_collector.add_error(error)
                    stack.pop()
                    current_node.token = ":"
                    action = "Error recovery: inserted missing ':'"
                else:
                    error = UnexpectedTokenError(
                        token=t, line=self.current_line, column=self.current_column,
                        lexeme=self.current_lexeme, expected_terminal=X
                    )
                    self.error_collector.add_error(error)
                    # Layer 2: Panic-Mode Recovery
                    self._perform_panic_recovery(stack)
                    action = f"Panic recovery: skipped to '{self.current_lexeme}'"
            
            elif is_non_terminal(X):
                production = self._get_table_entry(X, t)
                
                if production == ['error']:
                    error = NoProductionError(
                        non_terminal=X, terminal=t, line=self.current_line,
                        column=self.current_column, lexeme=self.current_lexeme
                    )
                    self.error_collector.add_error(error)
                    # Layer 2: Panic-Mode Recovery
                    self._perform_panic_recovery(stack)
                    action = f"Panic recovery: skipped to '{self.current_lexeme}'"
                else:
                    stack.pop()
                    if production != ['ε']:
                        child_nodes = []
                        for symbol in production:
                            if symbol != 'ε':
                                child_node = ParseTreeNode(symbol)
                                current_node.children.append(child_node)
                                child_nodes.append(child_node)
                        
                        for symbol, child in reversed(list(zip(production, child_nodes))):
                            if symbol != 'ε':
                                stack.append((symbol, child))
                    
                    action = f"Apply {X} -> {' '.join(production)}"
            
            else:
                error = ParseError(f"Invalid symbol on stack: '{X}'", self.current_line, self.current_column)
                self.error_collector.add_error(error)
                break
            
            self._record_step(stack, t, action, production if 'production' in locals() and production != ['error'] else None)
        
        if len(stack) > 1 and self.is_end() and len(self.error_collector.errors) < 3:
            top_non_terminal = None
            for symbol, _ in reversed(stack):
                if is_non_terminal(symbol):
                    top_non_terminal = symbol
                    break
            
            error = UnexpectedEndOfInputError(expected_non_terminal=top_non_terminal)
            self.error_collector.add_error(error)
        
        if self.error_collector.has_errors():
            self.error_collector.print_error_summary()
        
        return not self.error_collector.has_errors()
    
    def _get_table_entry(self, non_terminal: str, terminal: str) -> List[str]:
        return self.parse_table.get(non_terminal, {}).get(terminal, ['error'])
    
    def _advance_input(self):
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
    
    def _record_step(self, stack: List[tuple], token: str, action: str, production: Optional[List[str]]):
        stack_symbols = [symbol for symbol, _ in reversed(stack)]
        step = {
            'stack': stack_symbols,
            'token': token,
            'action': action,
            'production': production.copy() if production else None,
            'input_position': self.current_token_index
        }
        self.parsing_steps.append(step)
    
    def print_steps(self):
        print("\n" + "="*100)
        print("PARSING STEPS")
        print("="*100)
        
        print(f"{'Step':<6} {'Stack':<40} {'Input Token':<15} {'Action':<40}")
        print("-" * 100)
        
        for i, step in enumerate(self.parsing_steps):
            stack_str = " ".join(step['stack'])
            if len(stack_str) > 38:
                stack_str = stack_str[:38]
            
            action = step['action']
            if step['production']:
                prod_str = " ".join(step['production'])
                action += f" ({prod_str})"
            
            print(f"{i:<6} {stack_str:<40} {step['token']:<15} {action:<40}")
        
        print("="*100)
    
    def print_parse_summary(self):
        print("\nPARSING SUMMARY:")
        print("-" * 40)
        print(f"Total steps: {len(self.parsing_steps)}")
        print(f"Tokens processed: {self.current_token_index}")
        print(f"Parse table size: {len(self.parse_table) if self.parse_table else 0} non-terminals")
        print(f"Errors collected: {len(self.error_collector.errors)}")
        
        actions = [step['action'] for step in self.parsing_steps]
        matches = sum(1 for a in actions if 'Match' in a)
        productions = sum(1 for a in actions if 'Apply' in a)
        errors = sum(1 for a in actions if 'Error' in a or 'Panic' in a)
        
        print(f"Terminal matches: {matches}")
        print(f"Production applications: {productions}")
        print(f"Error recoveries: {errors}")
    
    def print_parse_tree(self):
        if self.parse_tree_root:
            self.parse_tree_root.print_tree()
        else:
            print("No parse tree available")
    
    def export_parse_tree_dot(self, filename):
        if not self.parse_tree_root:
            print("No parse tree available to export")
            return
        
        with open(filename, 'w') as f:
            f.write("digraph ParseTree {\n")
            self.parse_tree_root.to_dot(f)
            f.write("}\n")
        print(f"Parse tree exported to {filename}")
    
    def print_parse_tree_horizontal(self):
        if self.parse_tree_root:
            self.parse_tree_root.print_horizontal()
        else:
            print("No parse tree available")

def create_parser(source_code: str) -> Parser:
    tokens, lexical_errors = scan(source_code)
    
    if lexical_errors:
        error_msg = "Lexical errors found:\n" + "\n".join(f"  {e}" for e in lexical_errors)
        raise ParseError(error_msg)
    
    return Parser(tokens)

def parse_file(filename: str) -> bool:
    with open(filename, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    parser = create_parser(source_code)
    return parser.parse()

def parse_string(source_code: str) -> bool:
    parser = create_parser(source_code)
    return parser.parse()
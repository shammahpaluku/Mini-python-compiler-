"""
Semantic Analyzer for PyMini
Module Owner: Paluku Elishama and Odongo Jackton

Traverses the LL(1) parse tree to build a symbol table, perform static type inference,
and catch semantic errors (e.g., undeclared variables, type mismatches).
"""

class SemanticError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
    
    def __str__(self):
        return f"SemanticError at line {self.line}, col {self.column}: {self.message}"

class SymbolTable:
    """Tracks variable declarations and their inferred static types."""
    def __init__(self):
        self.symbols = {}
    
    def set_type(self, name: str, var_type: str):
        self.symbols[name] = var_type
        
    def get_type(self, name: str) -> str:
        return self.symbols.get(name, None)

class SemanticAnalyzer:
    def __init__(self, parse_tree_root):
        self.root = parse_tree_root
        self.symbol_table = SymbolTable()
        self.errors = []
        self.MAX_ERRORS = 3

    def report_error(self, message: str, line: int = 0, column: int = 0):
        self.errors.append(SemanticError(message, line, column))
        if len(self.errors) >= self.MAX_ERRORS:
            raise Exception("Semantic analysis aborted: Maximum error threshold (3) reached.")

    def analyze(self) -> bool:
        if not self.root:
            return False
        try:
            self._visit(self.root)
        except Exception as e:
            if "aborted" not in str(e):
                raise e # Re-raise if it's not our intentional abort
        return len(self.errors) == 0

    def print_errors(self):
        if not self.errors:
            print("SUCCESS::No semantic errors found.")
            return
        print("FAILURE::SEMANTIC ERRORS SUMMARY")
        print("=" * 60)
        for i, error in enumerate(self.errors, 1):
            print(f"  {i}. {error}")

    def _visit(self, node):
        if not node:
            return
        
        symbol = node.symbol.strip("<>")
        method_name = f"visit_{symbol}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self._visit(child)

    def visit_assignment(self, node):
        var_name = node.children[0].token
        expr_node = node.children[2]
        
        inferred_type = self.infer_expression(expr_node)
        if inferred_type and inferred_type != 'UNKNOWN':
            self.symbol_table.set_type(var_name, inferred_type)

    def visit_if_statement(self, node):
        cond_type = self.infer_expression(node.children[1])
        if cond_type and cond_type != 'BOOLEAN':
            self.report_error(f"Type mismatch: 'if' condition must be BOOLEAN, got {cond_type}")
        self._visit(node.children[4]) # statement_list
        if len(node.children) > 6:
            self._visit(node.children[6]) # else_clause

    def visit_while_statement(self, node):
        cond_type = self.infer_expression(node.children[1])
        if cond_type and cond_type != 'BOOLEAN':
            self.report_error(f"Type mismatch: 'while' condition must be BOOLEAN, got {cond_type}")
        self._visit(node.children[4]) # statement_list

    def visit_print_statement(self, node):
        self.infer_expression(node.children[2])

    def visit_term(self, node):
        child = node.children[0]
        if child.symbol in ['NUMBER', 'STRING', 'BOOLEAN']:
            return child.symbol
        if child.symbol == 'IDENTIFIER':
            var_type = self.symbol_table.get_type(child.token)
            if not var_type:
                # Extract the metadata from the terminal node
                line = getattr(child, 'line', 0)
                col = getattr(child, 'column', 0)
                
                # Crucial: Pass 'line' and 'col' to report_error instead of leaving them blank
                self.report_error(f"Undeclared variable '{child.token}'", line, col)
                return 'UNKNOWN'
            return var_type
        return 'UNKNOWN'

    def infer_expression(self, node) -> str:
        """Handles the LL(1) right-recursive expression structure."""
        if not node.children: return 'UNKNOWN'
        
        symbol = node.symbol.strip("<>")
        
        if symbol == 'expression':
            return self.infer_expression(node.children[0])
            
        elif symbol == 'logical_expression':
            left_type = self.infer_expression(node.children[0])
            tail = node.children[1] if len(node.children) > 1 else None
            return self._unwrap_tail(left_type, tail, ['and'], 'BOOLEAN')
            
        elif symbol == 'comparison_expression':
            left_type = self.infer_expression(node.children[0])
            tail = node.children[1] if len(node.children) > 1 else None
            # Comparisons (<) return BOOLEAN, but require NUMBER operands
            if tail and tail.children:
                return self._unwrap_tail(left_type, tail, ['<'], 'BOOLEAN', require_operands='NUMBER')
            return left_type
            
        elif symbol == 'arithmetic_expression':
            left_type = self.infer_expression(node.children[0])
            tail = node.children[1] if len(node.children) > 1 else None
            return self._unwrap_tail(left_type, tail, ['+', '-'], 'NUMBER', require_operands='NUMBER')
            
        elif symbol == 'term':
            child = node.children[0]
            if child.symbol in ['NUMBER', 'STRING', 'BOOLEAN']:
                return child.symbol
            if child.symbol == 'IDENTIFIER':
                var_type = self.symbol_table.get_type(child.token)
                if not var_type:
                    # Extract line and column metadata
                    line = getattr(child, 'line', 0)
                    col = getattr(child, 'column', 0)
                    self.report_error(f"Undeclared variable '{child.token}'", line, col)
                    return 'UNKNOWN'
                return var_type

        return 'UNKNOWN'

    def _unwrap_tail(self, current_type, tail_node, allowed_ops, result_type, require_operands=None):
        """Iteratively unwraps right-recursive tails (e.g., <arithmetic_tail>)."""
        curr = tail_node
        while curr and curr.children:
            op_node = curr.children[0]
            op = op_node.symbol
            right_node = curr.children[1]
            right_type = self.infer_expression(right_node)
            
            # Grab line/col from the operator node (+, -, etc.)
            line = getattr(op_node, 'line', 0)
            col = getattr(op_node, 'column', 0)
            
            if require_operands:
                if current_type != require_operands or right_type != require_operands:
                    self.report_error(f"Type mismatch: Operator '{op}' requires {require_operands}, got {current_type} and {right_type}", line, col)
                    return 'UNKNOWN'
            elif current_type != right_type:
                self.report_error(f"Type mismatch: Cannot operate on {current_type} and {right_type} with '{op}'", line, col)
                return 'UNKNOWN'
                
            current_type = result_type
            curr = curr.children[2] if len(curr.children) > 2 else None
            
        return current_type
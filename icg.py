"""
Intermediate Code Generator (TAC) for PyMini
Module Owner: Jilton Brian Chwanya

Traverses the semantically validated parse tree and generates Three Address Code.
Handles temporary variable allocation and control flow labels.
"""

class TACGenerator:
    def __init__(self, parse_tree_root):
        self.root = parse_tree_root
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def new_label(self):
        L = f"L{self.label_count}"
        self.label_count += 1
        return L

    def emit(self, instruction: str):
        self.code.append(instruction)

    def generate(self):
        if self.root:
            self._visit(self.root)
        return self.code
        
    def print_icg(self):
        for line in self.code:
            # Format labels differently from instructions for readability
            if line.endswith(":"):
                print(line)
            else:
                print(f"    {line}")

    def _visit(self, node):
        if not node:
            return None
        
        symbol = node.symbol.strip("<>")
        method_name = f"visit_{symbol}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self._visit(child)

    def visit_assignment(self, node):
        var_name = node.children[0].token
        expr_val = self.generate_expression(node.children[2])
        self.emit(f"{var_name} = {expr_val}")

    def visit_if_statement(self, node):
        cond_val = self.generate_expression(node.children[1])
        l_false = self.new_label()
        l_end = self.new_label()
        
        self.emit(f"ifFalse {cond_val} goto {l_false}")
        self._visit(node.children[4]) # statement_list (if body)
        self.emit(f"goto {l_end}")
        
        self.emit(f"{l_false}:")
        if len(node.children) > 6:
            self._visit(node.children[6]) # else_clause
            
        self.emit(f"{l_end}:")

    def visit_while_statement(self, node):
        l_start = self.new_label()
        l_end = self.new_label()
        
        self.emit(f"{l_start}:")
        cond_val = self.generate_expression(node.children[1])
        self.emit(f"ifFalse {cond_val} goto {l_end}")
        
        self._visit(node.children[4]) # statement_list (while body)
        self.emit(f"goto {l_start}")
        
        self.emit(f"{l_end}:")

    def visit_print_statement(self, node):
        val = self.generate_expression(node.children[2])
        self.emit(f"param {val}")
        self.emit("call print, 1")

    def generate_expression(self, node) -> str:
        """Returns the temporary variable or identifier holding the expression result."""
        if not node.children: return ""
        
        symbol = node.symbol.strip("<>")
        
        if symbol == 'expression':
            return self.generate_expression(node.children[0])
            
        elif symbol in ['logical_expression', 'comparison_expression', 'arithmetic_expression']:
            left_val = self.generate_expression(node.children[0])
            tail = node.children[1] if len(node.children) > 1 else None
            
            curr = tail
            curr_val = left_val
            
            while curr and curr.children:
                op = curr.children[0].symbol
                right_node = curr.children[1]
                right_val = self.generate_expression(right_node)
                
                t = self.new_temp()
                self.emit(f"{t} = {curr_val} {op} {right_val}")
                curr_val = t
                curr = curr.children[2] if len(curr.children) > 2 else None
                
            return curr_val
            
        elif symbol == 'term':
            child = node.children[0]
            # Strings and Booleans need to be preserved as literals in TAC
            if child.symbol in ['STRING', 'BOOLEAN']:
                return child.token
            return child.token # Return NUMBER value or IDENTIFIER name
            
        return ""
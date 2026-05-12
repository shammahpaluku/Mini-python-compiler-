import sys
from scanner import scan
from parser import Parser
from semantic import SemanticAnalyzer
from icg import TACGenerator

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <source_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        source = f.read()
    
    print("=" * 60)
    print("SOURCE CODE")
    print("=" * 60)
    print(source)
    
    print("\n" + "=" * 60)
    print("STAGE 1: SCANNER")
    print("=" * 60)
    tokens, lexical_errors = scan(source)
    
    # Indentation Fail-Fast check
    indent_errors = [e for e in lexical_errors if "Indentation error" in e]
    if indent_errors:
        print("FATAL: Scanner detected indentation errors. Pipeline halted.")
        for e in indent_errors:
            print(f"  {e}")
        sys.exit(1)
        
    for token in tokens:
        print(token)
        
    if lexical_errors:
        print("\nLexical warnings/errors (non-fatal):")
        for e in lexical_errors:
            print(f"  {e}")
            
    print("\n" + "=" * 60)
    print("STAGE 2: PARSER")
    print("=" * 60)
    parser = Parser(tokens)
    success = parser.parse()
    
    if not success:
        print("Parsing failed. Pipeline halted.")
        sys.exit(1)
        
    print("Parsing successful!")
    
    # Restored: Print Parse Tree
    print("\n" + "=" * 60)
    print("PARSE TREE (ASCII Art)")
    print("=" * 60)
    parser.print_parse_tree()
    
    # Restored: Export DOT file
    dot_filename = filename.replace('.pymini', '.dot')
    if dot_filename == filename:  # Fallback if no .pymini extension
        dot_filename = filename + '.dot'
    parser.export_parse_tree_dot(dot_filename)
    
    print("\n" + "=" * 60)
    print("STAGE 3: SEMANTIC ANALYSIS")
    print("=" * 60)
    semantic_analyzer = SemanticAnalyzer(parser.parse_tree_root)
    sem_success = semantic_analyzer.analyze()
    
    if not sem_success:
        semantic_analyzer.print_errors()
        print("Semantic errors detected. Pipeline halted. ICG will not be generated.")
        sys.exit(1)
        
    print("Semantic analysis successful! Types valid.\n")
    
    # New: Formatted Symbol Table output
    print("=" * 40)
    print("SYMBOL TABLE")
    print("=" * 40)
    print(f"{'Identifier':<20} | {'Inferred Type':<15}")
    print("-" * 40)
    if semantic_analyzer.symbol_table.symbols:
        for var_name, var_type in semantic_analyzer.symbol_table.symbols.items():
            print(f"{var_name:<20} | {var_type:<15}")
    else:
        print(f"{'<empty>':<20} | {'-':<15}")
    print("=" * 40)

    print("\n" + "=" * 60)
    print("STAGE 4: INTERMEDIATE CODE GENERATOR (TAC)")
    print("=" * 60)
    
    icg = TACGenerator(parser.parse_tree_root)
    icg.generate()
    icg.print_icg()
    print("\nIntermediate Code Generation complete.")

if __name__ == "__main__":
    main()
import sys
from scanner import scan
from parser import Parser

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
    
    print("=" * 60)
    print("TOKEN LIST (Scanner Output)")
    print("=" * 60)
    tokens, errors = scan(source)
    if errors:
        print("Lexical errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    for token in tokens:
        print(token)
    
    print("=" * 60)
    print("PARSING")
    print("=" * 60)
    parser = Parser(tokens)
    success = parser.parse()
    parser.print_steps()
    
    if success:
        print("=" * 60)
        print("PARSE TREE")
        print("=" * 60)
        parser.print_parse_tree()
        print("\nParsing successful!")
        
        # Export parse tree to DOT format
        dot_filename = filename.replace('.pymini', '.dot')
        parser.export_parse_tree_dot(dot_filename)
    else:
        print("\nParsing failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()

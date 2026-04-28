import os
import subprocess
import sys

# 1. Define the test cases and their source code
test_cases = {
    "test_lex_string.pymini": 'x = "This is a string without a closing quote\nprint(x)\n',
    "test_lex_invalid_char.pymini": 'price = 100\ntotal = price @ 5\n',
    "test_lex_indent.pymini": 'if True:\n      x = 1\n    y = 2\n',
    "test_parse_missing_colon.pymini": 'if True\n    print("Missing colon")\nx = 5\n',
    "test_parse_panic_mode.pymini": 'print( + )\nx = 10\n',
    "test_parse_threshold.pymini": 'a = +\nb = -\nc = <\nd = >\nprint("Will not reach here")\n',
    "test_parse_eof.pymini": 'while True:\n'
}

def main():
    print("============================================================")
    print(" PyMini Error Handling Test Suite")
    print("============================================================")

    # 2. Generate the physical test files
    for filename, content in test_cases.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    # 3. Run each file through the compiler
    for filename in test_cases.keys():
        print(f"\n\n{'='*60}")
        print(f" RUNNING TEST: {filename}")
        print(f"{'='*60}")
        
        # Call the compiler using the same Python executable running this script
        result = subprocess.run(
            [sys.executable, "main.py", filename], 
            capture_output=True, 
            text=True
        )
        
        # Combine stdout and stderr
        output = result.stdout + result.stderr
        
        # Optional: We filter out the massive "PARSING STEPS" table to keep the console readable,
        # focusing only on the Source Code, Tokens, and Error Summaries.
        printing_enabled = True
        for line in output.split('\n'):
            if "PARSING STEPS" in line:
                printing_enabled = False
                print("... [Parsing Steps Omitted for Brevity] ...")
            elif "PARSING SUMMARY:" in line or "PARSE TREE (ASCII Art)" in line or "Lexical errors found:" in line:
                printing_enabled = True
                
            if printing_enabled:
                print(line)

    # 4. Clean up the generated test files so they don't clutter your directory
    print(f"\n{'='*60}")
    print(" Cleaning up test files...")
    for filename in test_cases.keys():
        if os.path.exists(filename):
            os.remove(filename)
            
    # Clean up any generated .dot files
    for filename in test_cases.keys():
        dot_file = filename.replace('.pymini', '.dot')
        if os.path.exists(dot_file):
            os.remove(dot_file)
            
    print(" Done!")

if __name__ == "__main__":
    main()
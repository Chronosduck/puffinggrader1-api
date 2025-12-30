#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Puffing Language Interpreter
Usage: python main.py <filename.pf>
"""

import sys
import os
import io

# Force UTF-8 encoding for stdout/stderr to handle emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import LexerError, ParserError, RuntimeError as PuffingRuntimeError


def run_puffing_file(filepath):
    """
    Execute a Puffing language file and return the result
    """
    try:
        # Read the source code
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Lexical analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpretation
        interpreter = Interpreter()
        result = interpreter.run(ast)
        
        return {
            'success': True,
            'result': result,
            'output': 'Execution completed successfully'
        }
        
    except LexerError as e:
        return {
            'success': False,
            'error': 'Lexer Error',
            'message': str(e)
        }
    except ParserError as e:
        return {
            'success': False,
            'error': 'Parser Error',
            'message': str(e)
        }
    except PuffingRuntimeError as e:
        return {
            'success': False,
            'error': 'Runtime Error',
            'message': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Unknown Error',
            'message': str(e)
        }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.pf>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    result = run_puffing_file(filepath)
    
    if result['success']:
        print(f"[SUCCESS] {result['output']}")
        if result['result'] is not None:
            print(f"Result: {result['result']}")
    else:
        print(f"[ERROR] {result['error']}: {result['message']}")
        sys.exit(1)
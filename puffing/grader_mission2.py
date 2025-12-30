#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 2 Grader - The Calculator Conspiracy (IMPROVED VERSION)
More flexible output checking - focuses on structure + correct calculations

Usage: python grader_mission2.py <filepath.pf>
"""

import sys
import os
import re
from io import StringIO

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from src.lexer import Lexer
    from src.parser import Parser
    from src.interpreter import Interpreter
except ImportError as e:
    print(f"ERROR: Cannot import Puffing modules: {e}")
    sys.exit(1)

try:
    from src.errors import LexerError, ParserError, PuffingRuntimeError
except ImportError:
    try:
        from src.errors import LexerError, ParserError
        PuffingRuntimeError = Exception
    except ImportError:
        LexerError = Exception
        ParserError = Exception
        PuffingRuntimeError = Exception


def run_student_code(filepath, timeout_seconds=30):
    """Execute student's code and capture output"""
    import signal
    import traceback
    
    class TimeoutException(Exception):
        pass
    
    def timeout_handler(signum, frame):
        raise TimeoutException("Code execution timed out")
    
    captured_output = StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        if not os.path.exists(filepath):
            return {
                'success': False,
                'error': f"File not found: {filepath}",
                'output': '',
                'variables': {}
            }
        
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        sys.stdout = captured_output
        
        try:
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
            
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            interpreter = Interpreter()
            result = interpreter.run(ast)
            
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            output = captured_output.getvalue()
            variables = interpreter.variables
            
            return {
                'success': True,
                'output': output,
                'variables': variables,
                'result': result,
                'source_code': source_code
            }
            
        except TimeoutException:
            return {
                'success': False,
                'error': f"Timeout after {timeout_seconds} seconds",
                'output': captured_output.getvalue(),
                'variables': {},
                'source_code': source_code
            }
        except (LexerError, ParserError) as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'output': captured_output.getvalue(),
                'variables': {},
                'source_code': source_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'traceback': traceback.format_exc(),
                'output': captured_output.getvalue(),
                'variables': {},
                'source_code': source_code
            }
            
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        if hasattr(signal, 'SIGALRM'):
            try:
                signal.alarm(0)
            except:
                pass
        
        try:
            captured_output.close()
        except:
            pass


def extract_all_numbers(output):
    """Extract all numeric values from output in order"""
    pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    matches = re.findall(pattern, output)
    numbers = []
    for match in matches:
        try:
            numbers.append(float(match))
        except ValueError:
            continue
    return numbers


def compare_values(expected, actual, tolerance=0.01):
    """Compare two values with tolerance"""
    if actual is None:
        return False
    try:
        expected_float = float(expected)
        actual_float = float(actual)
        return abs(expected_float - actual_float) < tolerance
    except (ValueError, TypeError):
        return False


def check_expression_in_code(source_code, expression):
    """Check if an expression appears in the code (for verification)"""
    # Remove spaces for comparison
    expr_normalized = expression.replace(" ", "")
    code_normalized = source_code.replace(" ", "").replace("\n", "")
    return expr_normalized in code_normalized


def analyze_code_structure(source_code):
    """Analyze code structure"""
    results = {
        'has_investigate_expression': False,
        'has_solve_the_case': False,
        'has_execute_operation': False,
        'has_determine_priority': False,
        'has_handle_function': False,
        'has_set_variable': False,
        'has_get_variable': False,
        'has_is_operator': False,
        'has_tokenization_helpers': 0,
        'has_stack_operations': False,
        'has_priority_system': False,
        'has_variable_storage': False,
        'has_math_lib_import': False,
        'implements_shunting_yard': False,
        'handles_parentheses': False,
        'handles_functions': False,
        'handles_comparison_ops': False,
        'test_expressions': {}
    }
    
    # Check for required functions
    if 'fun investigate_expression' in source_code:
        results['has_investigate_expression'] = True
    if 'fun solve_the_case' in source_code:
        results['has_solve_the_case'] = True
    if 'fun execute_operation' in source_code:
        results['has_execute_operation'] = True
    if 'fun determine_priority' in source_code:
        results['has_determine_priority'] = True
    if 'fun handle_function' in source_code:
        results['has_handle_function'] = True
    if 'fun set_variable' in source_code:
        results['has_set_variable'] = True
    if 'fun get_variable' in source_code:
        results['has_get_variable'] = True
    if 'fun is_operator' in source_code:
        results['has_is_operator'] = True
    
    # Check tokenization helpers
    helpers = ['is_letter', 'is_alpha_or_underscore', 'is_number']
    results['has_tokenization_helpers'] = sum(1 for h in helpers if f'fun {h}' in source_code)
    
    # Check for stack operations
    if 'push(' in source_code and 'pop(' in source_code:
        results['has_stack_operations'] = True
    
    # Check for priority system
    if 'determine_priority' in source_code:
        results['has_priority_system'] = True
    
    # Check for variable storage
    if 'var_names' in source_code and 'var_values' in source_code:
        results['has_variable_storage'] = True
    
    # Check for math library
    if 'lib $math' in source_code or 'import $math' in source_code:
        results['has_math_lib_import'] = True
    
    # Check for Shunting Yard implementation
    if 'value_vault' in source_code and 'operation_queue' in source_code:
        results['implements_shunting_yard'] = True
    
    # Check for parentheses handling
    if '"("' in source_code and '")"' in source_code:
        results['handles_parentheses'] = True
    
    # Check for function handling
    if 'sqrt' in source_code or 'abs' in source_code or 'max' in source_code:
        results['handles_functions'] = True
    
    # Check for comparison operators
    if ('>=' in source_code or '<=' in source_code or '==' in source_code or 
        '!=' in source_code or '">"' in source_code or '"<"' in source_code):
        results['handles_comparison_ops'] = True
    
    # Check which test expressions are present
    test_cases = {
        'basic_arithmetic': [
            ('2 + 3', 5),
            ('10 - 4', 6),
            ('6 * 7', 42),
            ('2 + 3 * 4', 14),
            ('(2 + 3) * 4', 20),
            ('2 ^ 3 + 1', 9)
        ],
        'math_functions': [
            ('sqrt(16) + 4', 8),
            ('abs(-5) * 2', 10),
            ('max(10, 20) + min(5, 3)', 23)
        ],
        'variables': [
            ('x = 5', None),
            ('y = 10', None),
            ('x + y * 2', 25),
        ],
        'advanced': [
            ('max(sqrt(16), min(10, 5))', 5),
            ('((2 + 3) * 4 - 6) / 2 + 10', 17),
            ('sqrt(max(16, 9)) + min(abs(-5), 3)', 7),
        ]
    }
    
    for category, tests in test_cases.items():
        results['test_expressions'][category] = []
        for expr, expected in tests:
            if check_expression_in_code(source_code, expr):
                results['test_expressions'][category].append((expr, expected))
    
    return results


def grade_mission_2(execution_result):
    """Grade Mission 2 with balanced structure and output checking"""
    total_score = 0
    max_score = 100
    
    print("=" * 69)
    print(" MISSION 2: THE CALCULATOR CONSPIRACY")
    print(" FLEXIBLE GRADING (Structure + Expression Validation)")
    print(" NOTE: Checks if expressions are computed, not output format")
    print("=" * 69)
    print()
    
    if not execution_result['success']:
        print("❌ EXECUTION ERROR")
        print()
        print(f"Error: {execution_result.get('error', 'Unknown error')}")
        print()
        if 'traceback' in execution_result:
            print("Details:")
            print(execution_result['traceback'])
        print()
    
    variables = execution_result.get('variables', {})
    output = execution_result.get('output', '')
    source_code = execution_result.get('source_code', '')
    
    # Analyze code structure
    structure = analyze_code_structure(source_code)
    
    # Extract all numbers from output
    output_numbers = extract_all_numbers(output)
    
    print(f"📊 Found {len(output_numbers)} numeric values in output")
    print()
    
    # ========== PART 1: MAIN TASK (40 points) ==========
    print("📝 PART 1: MAIN TASK - Core Implementation (40 points)")
    print("-" * 70)
    
    main_score = 0
    
    # Test 1.1: Core Functions Structure (12 points)
    print("Test 1.1: Core Function Structure (12 points)")
    core_funcs_score = 0
    
    if structure['has_investigate_expression']:
        print("  ✓ investigate_expression() implemented (+4)")
        core_funcs_score += 4
    else:
        print("  ✗ Missing investigate_expression()")
    
    if structure['has_solve_the_case']:
        print("  ✓ solve_the_case() implemented (+4)")
        core_funcs_score += 4
    else:
        print("  ✗ Missing solve_the_case()")
    
    if structure['has_execute_operation']:
        print("  ✓ execute_operation() implemented (+4)")
        core_funcs_score += 4
    else:
        print("  ✗ Missing execute_operation()")
    
    main_score += core_funcs_score
    print(f"  Score: {core_funcs_score}/12")
    print()
    
    # Test 1.2: Algorithm Implementation (10 points)
    print("Test 1.2: Shunting Yard Algorithm (10 points)")
    algo_score = 0
    
    if structure['implements_shunting_yard']:
        print("  ✓ Uses value_vault and operation_queue (+5)")
        algo_score += 5
    else:
        print("  ✗ Missing Shunting Yard stacks")
    
    if structure['has_stack_operations']:
        print("  ✓ Implements push/pop operations (+5)")
        algo_score += 5
    else:
        print("  ✗ Missing stack operations")
    
    main_score += algo_score
    print(f"  Score: {algo_score}/10")
    print()
    
    # Test 1.3: Basic Arithmetic - Check expressions present and values in output (18 points)
    print("Test 1.3: Basic Arithmetic Validation (18 points)")
    basic_tests = [
        ('2 + 3', 5),
        ('10 - 4', 6),
        ('6 * 7', 42),
        ('2 + 3 * 4', 14),
        ('(2 + 3) * 4', 20),
        ('2 ^ 3 + 1', 9)
    ]
    
    basic_score = 0
    
    for expr, expected in basic_tests:
        expr_in_code = check_expression_in_code(source_code, expr)
        value_in_output = any(compare_values(expected, num) for num in output_numbers)
        
        if expr_in_code and value_in_output:
            print(f"  ✓ Expression '{expr}' computed correctly (result {expected} found) (+3)")
            basic_score += 3
        elif expr_in_code:
            print(f"  ⚠ Expression '{expr}' present but result {expected} not found in output (+1)")
            basic_score += 1
        else:
            print(f"  ✗ Expression '{expr}' not found in code")
    
    main_score += basic_score
    print(f"  Score: {basic_score}/18")
    print()
    
    total_score += main_score
    print(f"PART 1 Score: {main_score}/40")
    print()
    
    # ========== PART 2: SUBTASK 2A (20 points) ==========
    print("📝 PART 2: SUBTASK 2A - Mathematical Functions (20 points)")
    print("-" * 70)
    
    subtask_2a_score = 0
    
    # Test 2.1: Function System Structure (8 points)
    print("Test 2.1: Function System Structure (8 points)")
    func_structure_score = 0
    
    if structure['has_handle_function']:
        print("  ✓ handle_function() implemented (+4)")
        func_structure_score += 4
    else:
        print("  ✗ Missing handle_function()")
    
    if structure['has_math_lib_import']:
        print("  ✓ Math library imported (+4)")
        func_structure_score += 4
    else:
        print("  ✗ Math library not imported")
    
    subtask_2a_score += func_structure_score
    print(f"  Score: {func_structure_score}/8")
    print()
    
    # Test 2.2: Math Functions (12 points)
    print("Test 2.2: Math Functions Validation (12 points)")
    math_tests = [
        ('sqrt(16) + 4', 8),
        ('abs(-5) * 2', 10),
        ('max(10, 20) + min(5, 3)', 23)
    ]
    
    math_score = 0
    
    for expr, expected in math_tests:
        expr_in_code = check_expression_in_code(source_code, expr)
        value_in_output = any(compare_values(expected, num, tolerance=0.5) for num in output_numbers)
        
        if expr_in_code and value_in_output:
            print(f"  ✓ Expression '{expr}' computed correctly (result {expected} found) (+4)")
            math_score += 4
        elif expr_in_code:
            print(f"  ⚠ Expression '{expr}' present but result {expected} not found (+1)")
            math_score += 1
        else:
            print(f"  ✗ Expression '{expr}' not found in code")
    
    subtask_2a_score += math_score
    print(f"  Score: {math_score}/12")
    print()
    
    total_score += subtask_2a_score
    print(f"PART 2 Score: {subtask_2a_score}/20")
    print()
    
    # ========== PART 3: SUBTASK 2B (20 points) ==========
    print("📝 PART 3: SUBTASK 2B - Variable System (20 points)")
    print("-" * 70)
    
    subtask_2b_score = 0
    
    # Test 3.1: Variable System Structure (8 points)
    print("Test 3.1: Variable System Structure (8 points)")
    var_structure_score = 0
    
    if structure['has_set_variable']:
        print("  ✓ set_variable() implemented (+4)")
        var_structure_score += 4
    else:
        print("  ✗ Missing set_variable()")
    
    if structure['has_get_variable']:
        print("  ✓ get_variable() implemented (+4)")
        var_structure_score += 4
    else:
        print("  ✗ Missing get_variable()")
    
    subtask_2b_score += var_structure_score
    print(f"  Score: {var_structure_score}/8")
    print()
    
    # Test 3.2: Variable Storage (4 points)
    print("Test 3.2: Variable Storage Arrays (4 points)")
    storage_score = 0
    
    if structure['has_variable_storage']:
        print("  ✓ var_names and var_values arrays (+4)")
        storage_score += 4
    else:
        print("  ✗ Missing variable storage arrays")
    
    subtask_2b_score += storage_score
    print(f"  Score: {storage_score}/4")
    print()
    
    # Test 3.3: Variable Usage (8 points)
    print("Test 3.3: Variable Usage Validation (8 points)")
    
    var_score = 0
    has_x_assignment = check_expression_in_code(source_code, "x=5") or check_expression_in_code(source_code, "x = 5")
    has_y_assignment = check_expression_in_code(source_code, "y=10") or check_expression_in_code(source_code, "y = 10")
    has_var_expression = check_expression_in_code(source_code, "x+y*2")
    
    if has_x_assignment and has_y_assignment:
        print("  ✓ Variable assignments (x=5, y=10) present (+3)")
        var_score += 3
    else:
        print("  ✗ Missing variable assignments")
    
    if has_var_expression:
        print("  ✓ Variable usage expression present (+2)")
        var_score += 2
        # Check if result 25 is in output
        if any(compare_values(25, num, tolerance=1.0) for num in output_numbers):
            print("  ✓ Correct result (25) found in output (+3)")
            var_score += 3
        else:
            print("  ⚠ Expression present but result not verified")
    else:
        print("  ✗ Variable usage expression not found")
    
    subtask_2b_score += var_score
    print(f"  Score: {var_score}/8")
    print()
    
    total_score += subtask_2b_score
    print(f"PART 3 Score: {subtask_2b_score}/20")
    print()
    
    # ========== PART 4: SUBTASK 2C (20 points) ==========
    print("📝 PART 4: SUBTASK 2C - Advanced Features (20 points)")
    print("-" * 70)
    
    subtask_2c_score = 0
    
    # Test 4.1: Priority System Structure (8 points)
    print("Test 4.1: Priority System Structure (8 points)")
    priority_score = 0
    
    if structure['has_determine_priority']:
        print("  ✓ determine_priority() implemented (+4)")
        priority_score += 4
    else:
        print("  ✗ Missing determine_priority()")
    
    if structure['has_is_operator']:
        print("  ✓ is_operator() implemented (+4)")
        priority_score += 4
    else:
        print("  ✗ Missing is_operator()")
    
    subtask_2c_score += priority_score
    print(f"  Score: {priority_score}/8")
    print()
    
    # Test 4.2: Advanced Features Structure (4 points)
    print("Test 4.2: Advanced Features Structure (4 points)")
    advanced_structure_score = 0
    
    if structure['handles_parentheses']:
        print("  ✓ Parentheses handling (+2)")
        advanced_structure_score += 2
    else:
        print("  ✗ Missing parentheses handling")
    
    if structure['handles_comparison_ops']:
        print("  ✓ Comparison operators present (+2)")
        advanced_structure_score += 2
    else:
        print("  ⚠ Comparison operators not found")
    
    subtask_2c_score += advanced_structure_score
    print(f"  Score: {advanced_structure_score}/4")
    print()
    
    # Test 4.3: Advanced Expressions (8 points)
    print("Test 4.3: Advanced Expression Validation (8 points)")
    advanced_tests = [
        ('max(sqrt(16), min(10, 5))', 5),
        ('((2 + 3) * 4 - 6) / 2 + 10', 17),
        ('sqrt(max(16, 9)) + min(abs(-5), 3)', 7),
        ('sqrt(a^2 + b^2)', 5)
    ]
    
    advanced_output_score = 0
    
    for expr, expected in advanced_tests:
        expr_in_code = check_expression_in_code(source_code, expr)
        value_in_output = any(compare_values(expected, num, tolerance=0.5) for num in output_numbers)
        
        if expr_in_code and value_in_output:
            print(f"  ✓ Expression '{expr[:30]}...' computed correctly (+2)")
            advanced_output_score += 2
        elif expr_in_code:
            print(f"  ⚠ Expression present but result not verified (+0.5)")
            advanced_output_score += 0.5
        else:
            print(f"  ✗ Expression not found")
    
    advanced_output_score = int(advanced_output_score)
    subtask_2c_score += advanced_output_score
    print(f"  Score: {advanced_output_score}/8")
    print()
    
    total_score += subtask_2c_score
    print(f"PART 4 Score: {subtask_2c_score}/20")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 69)
    print(" FINAL RESULTS")
    print("=" * 69)
    print()
    print(f"Part 1 (Core Implementation):     {main_score:>3}/40")
    print(f"Part 2 (Math Functions):          {subtask_2a_score:>3}/20")
    print(f"Part 3 (Variables):               {subtask_2b_score:>3}/20")
    print(f"Part 4 (Advanced):                {subtask_2c_score:>3}/20")
    print("-" * 70)
    print(f"TOTAL SCORE:                      {total_score:>3}/{max_score}")
    print()
    
    # Grading scale
    if total_score >= 95:
        grade_letter, message = "A+", "🏆 EXCEPTIONAL! Outstanding work!"
    elif total_score >= 90:
        grade_letter, message = "A", "🌟 EXCELLENT! Very strong implementation"
    elif total_score >= 85:
        grade_letter, message = "A-", "⭐ VERY GOOD! Solid understanding"
    elif total_score >= 80:
        grade_letter, message = "B+", "✅ GOOD! Good grasp of concepts"
    elif total_score >= 75:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Decent work"
    elif total_score >= 70:
        grade_letter, message = "B-", "✓ PASSING! Meets requirements"
    elif total_score >= 65:
        grade_letter, message = "C+", "⚠ BELOW AVERAGE! Some gaps"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ NEEDS IMPROVEMENT! Review core concepts"
    else:
        grade_letter, message = "F", "❌ INSUFFICIENT! Major work needed"
    
    print(f"Grade: {grade_letter}")
    print()
    print(message)
    print()
    
    # Pass threshold: 70/100
    passed = total_score >= 70
    
    if not passed:
        print("=" * 69)
        print("⚠️  REQUIREMENT: You need at least 70/100 to pass Mission 2")
        print()
        if main_score < 25:
            print("   Focus Area: Core implementation (Part 1)")
            print("   → Implement investigate_expression() correctly")
            print("   → Implement solve_the_case() with Shunting Yard")
            print("   → Ensure basic arithmetic works")
        elif subtask_2a_score < 12:
            print("   Focus Area: Math functions (Part 2)")
            print("   → Implement handle_function()")
            print("   → Import math library")
            print("   → Test sqrt, abs, max, min")
        elif subtask_2b_score < 12:
            print("   Focus Area: Variables (Part 3)")
            print("   → Implement set_variable() and get_variable()")
            print("   → Create var_names and var_values arrays")
            print("   → Test variable usage")
        else:
            print("   Focus Area: Advanced features (Part 4)")
            print("   → Implement operator priority correctly")
            print("   → Test complex nested expressions")
    else:
        print("=" * 69)
        print("✅ PASSED! Your implementation meets the requirements")
        
        if total_score < 90:
            print()
            print("💡 Tips for improvement:")
            if main_score < 38:
                print("   → Test more edge cases in basic arithmetic")
            if subtask_2a_score < 18:
                print("   → Add more math functions (sin, cos, log)")
            if subtask_2b_score < 18:
                print("   → Improve variable handling reliability")
            if subtask_2c_score < 18:
                print("   → Polish advanced features and nested expressions")
    
    print("=" * 69)
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': passed,
        'grade_letter': grade_letter,
        'breakdown': {
            'part1': main_score,
            'part2': subtask_2a_score,
            'part3': subtask_2b_score,
            'part4': subtask_2c_score
        }
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission2.py <filepath.pf>")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 2: The Calculator Conspiracy\n")
        print(f"File: {filepath}\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_2(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
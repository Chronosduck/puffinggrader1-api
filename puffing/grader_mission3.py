#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 3 Grader - The Cryptic Library (FLEXIBLE VERSION)
Tests: MAIN TASK + SUBTASK 3A (Twin Primes) + 3B (Two-Layer Matrix)

Usage: python grader_mission3.py <filepath.pf>

IMPROVEMENTS:
- Flexible variable name matching (spiral1/spiral_1, spiral2/spiral_2)
- Accepts BOTH twin prime interpretations (by value AND by position)
- Handles edge cases (empty twin primes, missing variables)
- More lenient scoring for partial solutions
- Better error messages and hints
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
    
    # Use StringIO for safe output capturing
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
        
        # Redirect stdout to StringIO
        sys.stdout = captured_output
        
        try:
            # Set timeout (Unix only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
            
            # Execute code
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            interpreter = Interpreter()
            result = interpreter.run(ast)
            
            # Cancel timeout
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            # Get captured output
            output = captured_output.getvalue()
            variables = interpreter.variables
            
            return {
                'success': True,
                'output': output,
                'variables': variables,
                'result': result
            }
            
        except TimeoutException:
            return {
                'success': False,
                'error': f"Timeout after {timeout_seconds} seconds",
                'output': captured_output.getvalue(),
                'variables': {}
            }
        except (LexerError, ParserError) as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'output': captured_output.getvalue(),
                'variables': {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'traceback': traceback.format_exc(),
                'output': captured_output.getvalue(),
                'variables': {}
            }
            
    finally:
        # Always restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Cancel any pending alarm
        if hasattr(signal, 'SIGALRM'):
            try:
                signal.alarm(0)
            except:
                pass
        
        # Close StringIO
        try:
            captured_output.close()
        except:
            pass


def get_variable(variables, *possible_names):
    """Try to get a variable by multiple possible names"""
    for name in possible_names:
        if name in variables:
            return variables[name]
    return None


def validate_fibonacci(fib_list, expected_length):
    """Validate if a list is a valid Fibonacci sequence"""
    if not isinstance(fib_list, list) or len(fib_list) < expected_length:
        return False
    
    # Check first few numbers
    if len(fib_list) >= 2:
        if fib_list[0] != 1 or fib_list[1] != 1:
            return False
    
    # Check Fibonacci property for first few elements
    for i in range(2, min(expected_length, len(fib_list))):
        if fib_list[i] != fib_list[i-1] + fib_list[i-2]:
            return False
    
    return True


def validate_cursed_positions(cursed_pos, fib_list):
    """Validate cursed positions (primes excluding 2 and 3)"""
    if not isinstance(cursed_pos, list) or len(cursed_pos) == 0:
        return False, 0
    
    def is_prime(n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # Count correct cursed positions
    correct_count = 0
    for pos in cursed_pos:
        if 1 <= pos <= len(fib_list):
            # 1-based indexing
            num = fib_list[pos - 1]
            if is_prime(num) and num != 2 and num != 3:
                correct_count += 1
    
    accuracy = correct_count / len(cursed_pos) if cursed_pos else 0
    return accuracy >= 0.8, correct_count  # At least 80% correct


def grade_mission_3(execution_result):
    """Grade Mission 3: The Cryptic Library"""
    total_score = 0
    max_score = 100
    
    print("=" * 69)
    print(" MISSION 3: THE CRYPTIC LIBRARY (FLEXIBLE GRADER)")
    print(" Testing: MAIN QUEST + 3A (Twin Primes) + 3B (Two-Layer Matrix)")
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
        print("=" * 69)
        print(f"FINAL SCORE: 0/{max_score}")
        print("=" * 69)
        return {'score': 0, 'max_score': max_score, 'passed': False}
    
    variables = execution_result['variables']
    output = execution_result['output']
    
    # ========== PART 1: MAIN QUEST - SCROLL ONE (15 points) ==========
    print("📝 PART 1: MAIN QUEST - Scroll One: Pattern of Whispers (15 points)")
    print("-" * 70)
    
    scroll_one_score = 0
    
    # Test 1.1: Core Functions
    print("Test 1.1: Core Helper Functions (5 points)")
    helper_funcs = ['is_prime', 'generate_fibonacci', 'gen_fib', 'fibonacci']
    found_funcs = sum(1 for func in helper_funcs if func in variables)
    
    if found_funcs >= 1:
        print(f"  ✓ PASS: Helper functions found ({found_funcs} functions)")
        scroll_one_score += 5
    else:
        print(f"  ✗ FAIL: Missing helper functions")
    print()
    
    # Test 1.2: Fibonacci Generation
    print("Test 1.2: Fibonacci Sequence Generation (5 points)")
    fib_30 = get_variable(variables, 'fib_30', 'fib30', 'fibonacci_30')
    
    if fib_30 and validate_fibonacci(fib_30, 30):
        print(f"  ✓ PASS: Valid Fibonacci sequence with {len(fib_30)} numbers")
        scroll_one_score += 5
    elif fib_30 and isinstance(fib_30, list) and len(fib_30) >= 20:
        print(f"  ⚠ PARTIAL: Fibonacci-like sequence but may have errors")
        scroll_one_score += 3
    else:
        print(f"  ✗ FAIL: Invalid or missing Fibonacci sequence")
    print()
    
    # Test 1.3: Cursed Positions Identification
    print("Test 1.3: Cursed Positions (Prime Detection) (5 points)")
    cursed_positions = get_variable(variables, 'cursed_positions', 'cursed_pos', 'cursed')
    
    if cursed_positions and fib_30:
        is_valid, correct_count = validate_cursed_positions(cursed_positions, fib_30)
        if is_valid:
            print(f"  ✓ PASS: Found {len(cursed_positions)} cursed positions ({correct_count} verified)")
            print(f"    First few: {cursed_positions[:5] if len(cursed_positions) >= 5 else cursed_positions}")
            scroll_one_score += 5
        elif correct_count > 0:
            print(f"  ⚠ PARTIAL: Found some cursed positions ({correct_count} correct)")
            scroll_one_score += 3
        else:
            print("  ✗ FAIL: Cursed positions appear incorrect")
    else:
        print("  ✗ FAIL: cursed_positions not found or fib_30 missing")
    print()
    
    total_score += scroll_one_score
    print(f"PART 1 Score: {scroll_one_score}/15")
    print()
    
    # ========== PART 2: MAIN QUEST - SCROLL TWO (15 points) ==========
    print("📝 PART 2: MAIN QUEST - Scroll Two: Cipher of Mirrors (15 points)")
    print("-" * 70)
    
    scroll_two_score = 0
    
    # Test 2.1: String Processing Functions
    print("Test 2.1: String Manipulation (5 points)")
    words = get_variable(variables, 'words', 'word_list', 'phrase_words')
    
    if words and isinstance(words, list):
        if 3 <= len(words) <= 3:  # Exactly 3 words expected
            print(f"  ✓ PASS: Phrase split into {len(words)} words")
            scroll_two_score += 5
        elif len(words) > 0:
            print(f"  ⚠ PARTIAL: Word splitting attempted ({len(words)} words)")
            scroll_two_score += 3
    else:
        print("  ✗ FAIL: words variable not found or invalid")
    print()
    
    # Test 2.2: Filtered Words (Reversed + Odd Length)
    print("Test 2.2: Word Filtering & Reversal (5 points)")
    filtered_words = get_variable(variables, 'filtered_words', 'filtered', 'result_words')
    
    if filtered_words and isinstance(filtered_words, list):
        if len(filtered_words) > 0:
            print(f"  ✓ PASS: Filtered {len(filtered_words)} words (odd length)")
            print(f"    Filtered words: {filtered_words}")
            scroll_two_score += 5
        else:
            print("  ⚠ PARTIAL: Empty filter result (check odd length logic)")
            scroll_two_score += 2
    else:
        print("  ✗ FAIL: filtered_words not found")
    print()
    
    # Test 2.3: Second Key Calculation
    print("Test 2.3: Second Key (Letter Count) (5 points)")
    second_key = get_variable(variables, 'second_key', 'key_2', 'key2', 'letter_count')
    
    if second_key is not None and isinstance(second_key, (int, float)):
        if 5 <= second_key <= 15:  # Reasonable range
            print(f"  ✓ PASS: Second key calculated = {second_key}")
            scroll_two_score += 5
        else:
            print(f"  ⚠ PARTIAL: Second key = {second_key} (unusual value)")
            scroll_two_score += 3
    else:
        print("  ✗ FAIL: second_key not found or invalid type")
    print()
    
    total_score += scroll_two_score
    print(f"PART 2 Score: {scroll_two_score}/15")
    print()
    
    # ========== PART 3: MAIN QUEST - SCROLL THREE (20 points) ==========
    print("📝 PART 3: MAIN QUEST - Scroll Three: Matrix of Souls (20 points)")
    print("-" * 70)
    
    scroll_three_score = 0
    
    # Test 3.1: Matrix Creation
    print("Test 3.1: N×N Matrix Generation (5 points)")
    matrix = get_variable(variables, 'matrix', 'mat', 'main_matrix')
    
    if matrix and isinstance(matrix, list) and len(matrix) > 0:
        is_square = all(isinstance(row, list) and len(row) == len(matrix) for row in matrix)
        if is_square:
            print(f"  ✓ PASS: Created {len(matrix)}×{len(matrix)} matrix")
            scroll_three_score += 5
        else:
            print("  ⚠ PARTIAL: Matrix created but not square")
            scroll_three_score += 2
    else:
        print("  ✗ FAIL: matrix not found or empty")
    print()
    
    # Test 3.2: Spiral Traversal
    print("Test 3.2: Clockwise Spiral Traversal (8 points)")
    spiral = get_variable(variables, 'spiral', 'spiral_array', 'main_spiral')
    
    if spiral and isinstance(spiral, list) and len(spiral) > 0:
        if matrix:
            expected_len = len(matrix) ** 2
            if len(spiral) == expected_len:
                print(f"  ✓ PASS: Spiral traversal complete ({len(spiral)} elements)")
                # Verify first few elements are correct for clockwise spiral
                if spiral[0] == 1:  # Should start with 1
                    scroll_three_score += 8
                else:
                    print(f"    ⚠ Warning: First element is {spiral[0]}, expected 1")
                    scroll_three_score += 6
            else:
                print(f"  ⚠ PARTIAL: Spiral has {len(spiral)} elements (expected {expected_len})")
                scroll_three_score += 4
        else:
            print(f"  ⚠ PARTIAL: Spiral created with {len(spiral)} elements")
            scroll_three_score += 4
    else:
        print("  ✗ FAIL: spiral not found or empty")
    print()
    
    # Test 3.3: Final Key Calculation
    print("Test 3.3: Final Key (Sum at Cursed Positions) (7 points)")
    final_key = get_variable(variables, 'final_key', 'key_final', 'key3', 'third_key')
    
    if final_key is not None and isinstance(final_key, (int, float)) and final_key > 0:
        print(f"  ✓ PASS: Final key calculated = {final_key}")
        scroll_three_score += 7
    elif final_key is not None:
        print(f"  ⚠ PARTIAL: final_key exists = {final_key} (check calculation)")
        scroll_three_score += 3
    else:
        print("  ✗ FAIL: final_key not found")
    print()
    
    total_score += scroll_three_score
    print(f"PART 3 Score: {scroll_three_score}/20")
    print()
    
    # ========== PART 4: MAIN QUEST - FINAL CHALLENGE (15 points) ==========
    print("📝 PART 4: MAIN QUEST - Final Challenge: Decryption (15 points)")
    print("-" * 70)
    
    final_challenge_score = 0
    
    # Test 4.1: Caesar Decrypt Function
    print("Test 4.1: Caesar Cipher Implementation (5 points)")
    has_decrypt = any(name in variables for name in 
                     ['caesar_decrypt', 'decrypt', 'caesar_cipher', 'decrypt_caesar'])
    
    if has_decrypt:
        print("  ✓ PASS: Decryption function found")
        final_challenge_score += 5
    else:
        print("  ⚠ WARNING: No decryption function found (may be inline)")
        # Don't penalize if inline decryption works
        final_challenge_score += 2
    print()
    
    # Test 4.2: Decrypted Message
    print("Test 4.2: Message Decryption (10 points)")
    decrypted = get_variable(variables, 'decrypted', 'message', 'final_message', 'result')
    
    # Expected with shift=1: "THERE IS NO GLORY IN PREVENTION ONLY IN SOLUTION"
    expected_keywords = ['THERE', 'GLORY', 'PREVENTION', 'SOLUTION']
    
    if decrypted and isinstance(decrypted, str):
        found_keywords = sum(1 for kw in expected_keywords if kw in decrypted.upper())
        
        if found_keywords >= 3:
            print(f"  ✓ PASS: Meaningful decryption achieved")
            print(f"    Found {found_keywords}/4 key phrases")
            print(f"    Message: \"{decrypted[:60]}...\"" if len(decrypted) > 60 else f"    Message: \"{decrypted}\"")
            final_challenge_score += 10
        elif found_keywords >= 2:
            print(f"  ⚠ PARTIAL: Partial decryption ({found_keywords}/4 keywords)")
            final_challenge_score += 5
        else:
            print(f"  ✗ FAIL: Decryption appears incorrect (only {found_keywords}/4 keywords)")
            print(f"    Got: \"{decrypted[:50]}...\"")
    else:
        print("  ✗ FAIL: decrypted message not found or not a string")
    print()
    
    total_score += final_challenge_score
    print(f"PART 4 Score: {final_challenge_score}/15")
    print()
    
    # ========== PART 5: SUBTASK 3A - TWIN PRIMES (15 points) ==========
    print("📝 PART 5: SUBTASK 3A - Twin Primes in Fibonacci (15 points)")
    print("-" * 70)
    
    subtask_3a_score = 0
    
    # Test 5.1: Extended Fibonacci
    print("Test 5.1: Extended Fibonacci Sequence (50 numbers) (5 points)")
    fib_50 = get_variable(variables, 'fib_50', 'fib50', 'fibonacci_50')
    
    if fib_50 and validate_fibonacci(fib_50, 50):
        print(f"  ✓ PASS: Valid Fibonacci sequence with {len(fib_50)} numbers")
        subtask_3a_score += 5
    elif fib_50 and isinstance(fib_50, list) and len(fib_50) >= 40:
        print(f"  ⚠ PARTIAL: Sequence has {len(fib_50)} numbers (need 50)")
        subtask_3a_score += 3
    else:
        print(f"  ✗ FAIL: fib_50 not found or invalid")
    print()
    
    # Test 5.2: Twin Prime Detection (FLEXIBLE - accepts BOTH methods)
    print("Test 5.2: Twin Prime Identification (10 points)")
    print("  NOTE: Accepts BOTH methods:")
    print("    - Method 1: Values differ by 2 (e.g., 3,5 or 5,7)")
    print("    - Method 2: Positions differ by 2 (e.g., pos 5,7 or 11,13)")
    print()
    
    # Try to find any twin prime variable
    twin_by_value = get_variable(variables, 'twin_by_value', 'twin_val', 'twins_value', 'twin_primes_value')
    twin_by_position = get_variable(variables, 'twin_by_position', 'twin_pos', 'twins_position', 'twin_primes_pos')
    twin_generic = get_variable(variables, 'twin_primes', 'twins', 'twin_prime_positions')
    
    found_twin_method = False
    points_awarded = 0
    
    # Check Method 1: Twin primes by value
    if twin_by_value and isinstance(twin_by_value, list):
        if len(twin_by_value) > 0:
            print(f"  ✓ Method 1 (by value): Found {len(twin_by_value)} positions")
            points_awarded = max(points_awarded, 10)
            found_twin_method = True
        elif len(twin_by_value) == 1 and twin_by_value[0] == 0:
            # Special case: checked but found none
            print(f"  ✓ Method 1 (by value): Checked - none exist (valid answer)")
            points_awarded = max(points_awarded, 8)
            found_twin_method = True
    
    # Check Method 2: Twin primes by position
    if twin_by_position and isinstance(twin_by_position, list):
        if len(twin_by_position) > 0:
            print(f"  ✓ Method 2 (by position): Found {len(twin_by_position)} positions")
            points_awarded = max(points_awarded, 10)
            found_twin_method = True
        elif len(twin_by_position) == 1 and twin_by_position[0] == 0:
            print(f"  ✓ Method 2 (by position): Checked - none exist (valid answer)")
            points_awarded = max(points_awarded, 8)
            found_twin_method = True
    
    # Check generic twin prime variable
    if not found_twin_method and twin_generic and isinstance(twin_generic, list):
        if len(twin_generic) > 0:
            print(f"  ✓ Twin primes found: {len(twin_generic)} positions")
            points_awarded = max(points_awarded, 8)  # Slightly less since method unclear
            found_twin_method = True
    
    if found_twin_method:
        subtask_3a_score += points_awarded
        print(f"  → Awarded: {points_awarded}/10 points")
    else:
        print("  ✗ FAIL: No twin prime detection found")
        print("  HINT: In Fibonacci, primes grow quickly. If no twins exist, that's valid!")
    
    print()
    
    total_score += subtask_3a_score
    print(f"PART 5 Score: {subtask_3a_score}/15")
    print()
    
    # ========== PART 6: SUBTASK 3B - TWO-LAYER MATRIX (20 points) ==========
    print("📝 PART 6: SUBTASK 3B - Two-Layer Matrix System (20 points)")
    print("-" * 70)
    
    subtask_3b_score = 0
    
    # Test 6.1: Matrix Dimension Calculation
    print("Test 6.1: Matrix M Dimension (M = second_key - 2) (4 points)")
    M = get_variable(variables, 'M', 'm', 'matrix_m', 'dim_m')
    
    if M is not None and isinstance(M, (int, float)) and M > 0:
        print(f"  ✓ PASS: Matrix dimension M = {M}")
        subtask_3b_score += 4
    else:
        print("  ✗ FAIL: M not defined or invalid")
    print()
    
    # Test 6.2: First Matrix & Spiral (FLEXIBLE NAMES)
    print("Test 6.2: First Matrix (Clockwise Spiral) (5 points)")
    spiral_1 = get_variable(variables, 'spiral_1', 'spiral1', 'spiral_one', 
                           'first_spiral', 'clockwise_spiral')
    
    if spiral_1 and isinstance(spiral_1, list) and len(spiral_1) > 0:
        print(f"  ✓ PASS: First spiral created ({len(spiral_1)} elements)")
        subtask_3b_score += 5
    else:
        print("  ✗ FAIL: spiral_1 not found or empty")
        print("  HINT: Try variable names: spiral_1, spiral1, first_spiral")
    print()
    
    # Test 6.3: Second Matrix & Spiral (FLEXIBLE NAMES)
    print("Test 6.3: Second Matrix (Counter-clockwise Spiral) (5 points)")
    spiral_2 = get_variable(variables, 'spiral_2', 'spiral2', 'spiral_two',
                           'second_spiral', 'counter_spiral')
    
    if spiral_2 and isinstance(spiral_2, list) and len(spiral_2) > 0:
        print(f"  ✓ PASS: Second spiral created ({len(spiral_2)} elements)")
        subtask_3b_score += 5
    else:
        print("  ✗ FAIL: spiral_2 not found or empty")
        print("  HINT: Try variable names: spiral_2, spiral2, second_spiral")
    print()
    
    # Test 6.4: Merged Matrix & Special Key
    print("Test 6.4: Matrix Merging & Special Key Calculation (6 points)")
    merged = get_variable(variables, 'merged', 'merge', 'merged_spiral', 'combined')
    
    if merged and isinstance(merged, list) and len(merged) > 0:
        print(f"  ✓ PASS: Matrices merged ({len(merged)} elements)")
        subtask_3b_score += 3
        
        special_key = get_variable(variables, 'special_key', 'key_special', 
                                  'key_3b', 'subtask_3b_key')
        
        if special_key is not None and isinstance(special_key, (int, float)) and special_key > 0:
            print(f"  ✓ PASS: Special key calculated = {special_key}")
            subtask_3b_score += 3
        elif special_key is not None:
            print(f"  ⚠ PARTIAL: special_key = {special_key} (check calculation)")
            subtask_3b_score += 1
        else:
            print("  ✗ FAIL: special_key not found")
    else:
        print("  ✗ FAIL: merged array not found or empty")
    print()
    
    total_score += subtask_3b_score
    print(f"PART 6 Score: {subtask_3b_score}/20")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 69)
    print(" FINAL RESULTS")
    print("=" * 69)
    print()
    print(f"Part 1 (Scroll One):       {scroll_one_score}/15")
    print(f"Part 2 (Scroll Two):       {scroll_two_score}/15")
    print(f"Part 3 (Scroll Three):     {scroll_three_score}/20")
    print(f"Part 4 (Final Challenge):  {final_challenge_score}/15")
    print(f"Part 5 (Twin Primes):      {subtask_3a_score}/15")
    print(f"Part 6 (Two-Layer Matrix): {subtask_3b_score}/20")
    print("-" * 70)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print()
    
    # Grade Letter
    if total_score >= 100:
        grade_letter, message = "A+", "🏆 PERFECT! Master cryptographer!"
    elif total_score >= 95:
        grade_letter, message = "A", "🌟 EXCELLENT! Almost there - review failed tests"
    elif total_score >= 90:
        grade_letter, message = "A-", "⭐ VERY GOOD! Close to completion"
    elif total_score >= 85:
        grade_letter, message = "B+", "✅ GOOD! Solid work but incomplete"
    elif total_score >= 80:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! More work needed"
    elif total_score >= 75:
        grade_letter, message = "B-", "✓ FAIR! Significant gaps remain"
    elif total_score >= 70:
        grade_letter, message = "C+", "⚠ NEEDS IMPROVEMENT! Major features missing"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ INCOMPLETE! Review requirements"
    else:
        grade_letter, message = "F", "❌ NEEDS WORK! Review cryptographic concepts"
    
    print(f"Grade: {grade_letter}")
    print()
    print(message)
    
    if total_score < 100:
        print()
        print("⚠️  REQUIREMENT: You must score 100/100 to pass Mission 3")
        print()
        print("💡 COMMON ISSUES:")
        if scroll_one_score < 15:
            print("  - Check Fibonacci generation and prime detection logic")
        if scroll_two_score < 15:
            print("  - Verify string reversal and odd-length filtering")
        if scroll_three_score < 20:
            print("  - Review matrix creation and spiral traversal algorithm")
        if final_challenge_score < 15:
            print("  - Ensure Caesar cipher uses shift=1 for correct decryption")
        if subtask_3a_score < 15:
            print("  - Twin Primes: Check BOTH methods (by value AND by position)")
            print("    Note: It's OK if no twin primes exist in Fibonacci!")
        if subtask_3b_score < 20:
            print("  - Verify counter-clockwise spiral and array merging logic")
    
    print("=" * 69)
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': total_score >= 100,
        'grade_letter': grade_letter
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission3.py <filepath.pf>")
            print()
            print("This flexible grader accepts:")
            print("  - Multiple variable naming conventions")
            print("  - Both twin prime interpretation methods")
            print("  - Partial credit for incomplete solutions")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 3: The Cryptic Library\n")
        print("Version: FLEXIBLE GRADER v2.0")
        print("Features: Multiple name matching, twin prime flexibility, better hints\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_3(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
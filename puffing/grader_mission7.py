#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 7 Grader - Caesar Cipher Encryption/Decryption
Tests encryption, decryption, and verification logic

Usage: python grader_mission7.py <filepath.pf>
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


def caesar_encrypt(text, key):
    """Reference Caesar cipher encryption"""
    result = ""
    for char in text:
        if char.isupper():
            result += chr((ord(char) - ord('A') + key) % 26 + ord('A'))
        elif char.islower():
            result += chr((ord(char) - ord('a') + key) % 26 + ord('a'))
        else:
            result += char
    return result


def caesar_decrypt(text, key):
    """Reference Caesar cipher decryption"""
    return caesar_encrypt(text, -key)


def analyze_code_structure(source_code):
    """Analyze code structure for required elements"""
    results = {
        'has_encrypt_function': False,
        'has_decrypt_function': False,
        'has_char_processing': False,
        'has_uppercase_handling': False,
        'has_lowercase_handling': False,
        'has_non_alpha_preservation': False,
        'has_modulo_operation': False,
        'has_verification': False,
        'has_for_loops': 0,
        'has_conditionals': 0,
        'uses_string_lib': False,
        'has_helper_functions': 0,
        'has_multiple_test_cases': False
    }
    
    # Check for encryption function
    if 'fun encrypt' in source_code or 'encrypt_char' in source_code or 'encrypt_message' in source_code:
        results['has_encrypt_function'] = True
    
    # Check for decryption function
    if 'fun decrypt' in source_code or 'decrypt_char' in source_code or 'decrypt_message' in source_code:
        results['has_decrypt_function'] = True
    
    # Check for character processing
    if 'char_at' in source_code:
        results['has_char_processing'] = True
    
    # Check for uppercase handling
    if 'is_upper' in source_code or 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' in source_code:
        results['has_uppercase_handling'] = True
    
    # Check for lowercase handling
    if 'is_lower' in source_code or 'abcdefghijklmnopqrstuvwxyz' in source_code:
        results['has_lowercase_handling'] = True
    
    # Check for non-alphabetic preservation
    if 'is_alpha' in source_code or ('if' in source_code and 'else' in source_code):
        results['has_non_alpha_preservation'] = True
    
    # Check for modulo operation (wrapping)
    if '%' in source_code and '26' in source_code:
        results['has_modulo_operation'] = True
    
    # Check for verification logic
    if '=' in source_code and ('ถูกต้อง' in source_code or 'correct' in source_code.lower() or 'verify' in source_code.lower()):
        results['has_verification'] = True
    
    # Count for loops
    results['has_for_loops'] = source_code.count('for ')
    
    # Count conditionals
    results['has_conditionals'] = source_code.count('if ')
    
    # Check for string library usage
    if 'lib $string' in source_code:
        results['uses_string_lib'] = True
    
    # Count helper functions
    results['has_helper_functions'] = source_code.count('fun ')
    
    # Check for multiple test cases
    if source_code.count('let message') > 1 or source_code.count('let msg') > 1:
        results['has_multiple_test_cases'] = True
    
    return results


def extract_encrypted_message(output):
    """Extract encrypted message from output"""
    patterns = [
        r'เข้ารหัสแล้ว[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
        r'encrypted[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
        r'Encrypted[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1).strip()
    return None


def extract_decrypted_message(output):
    """Extract decrypted message from output"""
    patterns = [
        r'ถอดรหัสแล้ว[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
        r'decrypted[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
        r'Decrypted[:\s]+([A-Za-z\s!@#$%^&*(),.?":{}|<>]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1).strip()
    return None


def check_verification_message(output):
    """Check if verification message is present"""
    success_indicators = ['✓', '✅', 'ถูกต้อง', 'correct', 'success', 'verified']
    return any(indicator in output for indicator in success_indicators)


def grade_mission_7(execution_result):
    """Grade Mission 7 - Caesar Cipher"""
    total_score = 0
    max_score = 100
    
    print("=" * 70)
    print(" MISSION 7: CAESAR CIPHER ENCRYPTION/DECRYPTION")
    print(" ข้อความจากคนในใจ - Secret Message Encoding")
    print("=" * 70)
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
        print("⚠️  Fix the errors before grading can proceed")
        print("=" * 70)
        return {
            'score': 0,
            'max_score': max_score,
            'passed': False,
            'grade_letter': 'F',
            'breakdown': {}
        }
    
    variables = execution_result.get('variables', {})
    output = execution_result.get('output', '')
    source_code = execution_result.get('source_code', '')
    
    # Analyze code structure
    structure = analyze_code_structure(source_code)
    
    print(f"📊 Code Analysis:")
    print(f"   Functions detected: {structure['has_helper_functions']}")
    print(f"   For loops: {structure['has_for_loops']}")
    print(f"   Conditionals: {structure['has_conditionals']}")
    print(f"   Uses string library: {structure['uses_string_lib']}")
    print()
    
    # ========== PART 1: CODE STRUCTURE & FUNCTIONS (30 points) ==========
    print("📝 PART 1: Code Structure & Functions (30 points)")
    print("-" * 70)
    
    part1_score = 0
    
    # Test 1.1: Function Definitions (10 points)
    print("Test 1.1: Function Definitions (10 points)")
    func_score = 0
    
    if structure['has_encrypt_function']:
        print("  ✓ Encryption function defined (+5)")
        func_score += 5
    else:
        print("  ✗ Missing encryption function")
    
    if structure['has_decrypt_function']:
        print("  ✓ Decryption function defined (+5)")
        func_score += 5
    else:
        print("  ✗ Missing decryption function")
    
    part1_score += func_score
    print(f"  Score: {func_score}/10")
    print()
    
    # Test 1.2: Character Processing Logic (12 points)
    print("Test 1.2: Character Processing Logic (12 points)")
    char_score = 0
    
    if structure['has_char_processing']:
        print("  ✓ Character-by-character processing (+3)")
        char_score += 3
    else:
        print("  ✗ Missing character processing")
    
    if structure['has_uppercase_handling']:
        print("  ✓ Uppercase letter handling (+3)")
        char_score += 3
    else:
        print("  ✗ Missing uppercase handling")
    
    if structure['has_lowercase_handling']:
        print("  ✓ Lowercase letter handling (+3)")
        char_score += 3
    else:
        print("  ✗ Missing lowercase handling")
    
    if structure['has_non_alpha_preservation']:
        print("  ✓ Non-alphabetic character preservation (+3)")
        char_score += 3
    else:
        print("  ✗ Missing non-alpha preservation")
    
    part1_score += char_score
    print(f"  Score: {char_score}/12")
    print()
    
    # Test 1.3: Alphabet Wrapping (8 points)
    print("Test 1.3: Alphabet Wrapping Logic (8 points)")
    wrap_score = 0
    
    if structure['has_modulo_operation']:
        print("  ✓ Modulo 26 operation for wrapping (+5)")
        wrap_score += 5
    else:
        print("  ✗ Missing modulo wrapping")
    
    if structure['has_for_loops'] >= 2:
        print("  ✓ Loop structures for string traversal (+3)")
        wrap_score += 3
    else:
        print("  ⚠ Insufficient loop structures")
    
    part1_score += wrap_score
    print(f"  Score: {wrap_score}/8")
    print()
    
    total_score += part1_score
    print(f"PART 1 Score: {part1_score}/30")
    print()
    
    # ========== PART 2: ENCRYPTION CORRECTNESS (25 points) ==========
    print("📝 PART 2: Encryption Correctness (25 points)")
    print("-" * 70)
    
    part2_score = 0
    
    # Test 2.1: Basic Encryption Test (15 points)
    print("Test 2.1: 'Hello World!' with key=3 → 'Khoor Zruog!' (15 points)")
    
    test_message = "Hello World!"
    test_key = 3
    expected_encrypted = "Khoor Zruog!"
    
    encrypted_output = extract_encrypted_message(output)
    
    encrypt_score = 0
    
    if encrypted_output:
        print(f"  Found encrypted output: '{encrypted_output}'")
        
        # Check exact match
        if encrypted_output == expected_encrypted:
            print(f"  ✓ Perfect match! (+15)")
            encrypt_score = 15
        else:
            # Partial credit for close matches
            correct_chars = sum(1 for a, b in zip(encrypted_output, expected_encrypted) if a == b)
            accuracy = correct_chars / len(expected_encrypted) if expected_encrypted else 0
            
            if accuracy >= 0.9:
                print(f"  ⚠ Almost correct ({accuracy*100:.0f}% match) (+12)")
                encrypt_score = 12
            elif accuracy >= 0.7:
                print(f"  ⚠ Mostly correct ({accuracy*100:.0f}% match) (+9)")
                encrypt_score = 9
            elif accuracy >= 0.5:
                print(f"  ⚠ Partially correct ({accuracy*100:.0f}% match) (+6)")
                encrypt_score = 6
            else:
                print(f"  ✗ Incorrect encryption ({accuracy*100:.0f}% match) (+3)")
                encrypt_score = 3
    else:
        print("  ✗ No encrypted message found in output")
    
    part2_score += encrypt_score
    print(f"  Score: {encrypt_score}/15")
    print()
    
    # Test 2.2: Case Preservation (5 points)
    print("Test 2.2: Case Preservation Check (5 points)")
    case_score = 0
    
    if encrypted_output:
        # Check if uppercase stays uppercase, lowercase stays lowercase
        has_upper = any(c.isupper() for c in encrypted_output if c.isalpha())
        has_lower = any(c.islower() for c in encrypted_output if c.isalpha())
        
        if has_upper and has_lower:
            print("  ✓ Mixed case preserved correctly (+5)")
            case_score = 5
        else:
            print("  ⚠ Case preservation issue")
    else:
        print("  ✗ Cannot verify case preservation")
    
    part2_score += case_score
    print(f"  Score: {case_score}/5")
    print()
    
    # Test 2.3: Special Character Preservation (5 points)
    print("Test 2.3: Special Character Preservation (5 points)")
    special_score = 0
    
    if encrypted_output:
        # Check if space and ! are preserved
        if ' ' in encrypted_output and '!' in encrypted_output:
            print("  ✓ Space and punctuation preserved (+5)")
            special_score = 5
        elif ' ' in encrypted_output or '!' in encrypted_output:
            print("  ⚠ Partial preservation (+3)")
            special_score = 3
        else:
            print("  ✗ Special characters not preserved")
    else:
        print("  ✗ Cannot verify special characters")
    
    part2_score += special_score
    print(f"  Score: {special_score}/5")
    print()
    
    total_score += part2_score
    print(f"PART 2 Score: {part2_score}/25")
    print()
    
    # ========== PART 3: DECRYPTION CORRECTNESS (25 points) ==========
    print("📝 PART 3: Decryption Correctness (25 points)")
    print("-" * 70)
    
    part3_score = 0
    
    # Test 3.1: Basic Decryption Test (15 points)
    print("Test 3.1: 'Khoor Zruog!' with key=3 → 'Hello World!' (15 points)")
    
    decrypted_output = extract_decrypted_message(output)
    
    decrypt_score = 0
    
    if decrypted_output:
        print(f"  Found decrypted output: '{decrypted_output}'")
        
        # Check exact match
        if decrypted_output == test_message:
            print(f"  ✓ Perfect decryption! (+15)")
            decrypt_score = 15
        else:
            # Partial credit
            correct_chars = sum(1 for a, b in zip(decrypted_output, test_message) if a == b)
            accuracy = correct_chars / len(test_message) if test_message else 0
            
            if accuracy >= 0.9:
                print(f"  ⚠ Almost correct ({accuracy*100:.0f}% match) (+12)")
                decrypt_score = 12
            elif accuracy >= 0.7:
                print(f"  ⚠ Mostly correct ({accuracy*100:.0f}% match) (+9)")
                decrypt_score = 9
            elif accuracy >= 0.5:
                print(f"  ⚠ Partially correct ({accuracy*100:.0f}% match) (+6)")
                decrypt_score = 6
            else:
                print(f"  ✗ Incorrect decryption ({accuracy*100:.0f}% match) (+3)")
                decrypt_score = 3
    else:
        print("  ✗ No decrypted message found in output")
    
    part3_score += decrypt_score
    print(f"  Score: {decrypt_score}/15")
    print()
    
    # Test 3.2: Reversibility Check (10 points)
    print("Test 3.2: Encryption → Decryption Reversibility (10 points)")
    reverse_score = 0
    
    if encrypted_output and decrypted_output:
        if decrypted_output == test_message:
            print("  ✓ Perfect reversibility: Original = Decrypted (+10)")
            reverse_score = 10
        else:
            print("  ⚠ Reversibility issue: Original ≠ Decrypted (+5)")
            reverse_score = 5
    else:
        print("  ✗ Cannot verify reversibility")
    
    part3_score += reverse_score
    print(f"  Score: {reverse_score}/10")
    print()
    
    total_score += part3_score
    print(f"PART 3 Score: {part3_score}/25")
    print()
    
    # ========== PART 4: VERIFICATION & OUTPUT (20 points) ==========
    print("📝 PART 4: Verification & Output Quality (20 points)")
    print("-" * 70)
    
    part4_score = 0
    
    # Test 4.1: Verification Logic (10 points)
    print("Test 4.1: Verification Logic Implementation (10 points)")
    verify_score = 0
    
    if structure['has_verification']:
        print("  ✓ Verification logic present (+5)")
        verify_score += 5
    else:
        print("  ✗ Missing verification logic")
    
    has_success_msg = check_verification_message(output)
    if has_success_msg:
        print("  ✓ Success verification message displayed (+5)")
        verify_score += 5
    else:
        print("  ⚠ No verification message found")
    
    part4_score += verify_score
    print(f"  Score: {verify_score}/10")
    print()
    
    # Test 4.2: Output Format & Clarity (10 points)
    print("Test 4.2: Output Format & Clarity (10 points)")
    output_score = 0
    
    # Check for clear output structure
    has_original = 'ต้นฉบับ' in output or 'original' in output.lower() or 'message' in output.lower()
    has_key_display = 'key' in output.lower() or 'กุญแจ' in output
    has_encrypted_label = 'เข้ารหัส' in output or 'encrypted' in output.lower()
    has_decrypted_label = 'ถอดรหัส' in output or 'decrypted' in output.lower()
    
    clarity_points = 0
    if has_original:
        clarity_points += 2
    if has_key_display:
        clarity_points += 2
    if has_encrypted_label:
        clarity_points += 3
    if has_decrypted_label:
        clarity_points += 3
    
    if clarity_points >= 9:
        print(f"  ✓ Excellent output formatting (+10)")
        output_score = 10
    elif clarity_points >= 6:
        print(f"  ✓ Good output formatting (+7)")
        output_score = 7
    elif clarity_points >= 4:
        print(f"  ⚠ Basic output formatting (+5)")
        output_score = 5
    else:
        print(f"  ⚠ Poor output formatting (+3)")
        output_score = 3
    
    part4_score += output_score
    print(f"  Score: {output_score}/10")
    print()
    
    total_score += part4_score
    print(f"PART 4 Score: {part4_score}/20")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 70)
    print(" FINAL RESULTS")
    print("=" * 70)
    print()
    print(f"Part 1 (Code Structure & Functions):  {part1_score:>3}/30")
    print(f"Part 2 (Encryption Correctness):      {part2_score:>3}/25")
    print(f"Part 3 (Decryption Correctness):      {part3_score:>3}/25")
    print(f"Part 4 (Verification & Output):       {part4_score:>3}/20")
    print("-" * 70)
    print(f"TOTAL SCORE:                          {total_score:>3}/{max_score}")
    print()
    
    # Grading scale
    if total_score >= 95:
        grade_letter, message = "A+", "🏆 EXCEPTIONAL! Perfect Caesar Cipher implementation!"
    elif total_score >= 90:
        grade_letter, message = "A", "🌟 EXCELLENT! Outstanding encryption/decryption!"
    elif total_score >= 85:
        grade_letter, message = "A-", "⭐ VERY GOOD! Strong cryptography skills!"
    elif total_score >= 80:
        grade_letter, message = "B+", "✅ GOOD! Solid cipher implementation!"
    elif total_score >= 75:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Good work!"
    elif total_score >= 70:
        grade_letter, message = "B-", "✓ PASSING! Meets requirements!"
    elif total_score >= 65:
        grade_letter, message = "C+", "⚠ BELOW AVERAGE! Some issues remain"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ NEEDS IMPROVEMENT! Review concepts"
    else:
        grade_letter, message = "F", "❌ INSUFFICIENT! Major work needed"
    
    print(f"Grade: {grade_letter}")
    print()
    print(message)
    print()
    
    # Pass threshold: 70/100
    passed = total_score >= 70
    
    if not passed:
        print("=" * 70)
        print("⚠️  REQUIREMENT: You need at least 70/100 to pass Mission 7")
        print()
        if part1_score < 20:
            print("   Focus Area: Code Structure & Functions (Part 1)")
            print("   → Define separate encryption and decryption functions")
            print("   → Implement character-by-character processing")
            print("   → Handle uppercase, lowercase, and special characters")
        elif part2_score < 17:
            print("   Focus Area: Encryption Correctness (Part 2)")
            print("   → Test with 'Hello World!' and key=3")
            print("   → Expected output: 'Khoor Zruog!'")
            print("   → Preserve case and special characters")
        elif part3_score < 17:
            print("   Focus Area: Decryption Correctness (Part 3)")
            print("   → Ensure decryption reverses encryption")
            print("   → Use negative key or reverse shift")
            print("   → Verify original message is restored")
        else:
            print("   Focus Area: Verification & Output (Part 4)")
            print("   → Add verification logic to check correctness")
            print("   → Display clear, formatted output")
            print("   → Show original, encrypted, and decrypted messages")
    else:
        print("=" * 70)
        print("✅ PASSED! Your Caesar Cipher works correctly!")
        
        if total_score == 100:
            print()
            print("🎉 PERFECT SCORE! Your implementation is flawless!")
            print("   You've mastered:")
            print("   ✓ String manipulation and character processing")
            print("   ✓ Modular arithmetic and alphabet wrapping")
            print("   ✓ Function design and code organization")
            print("   ✓ Encryption/decryption reversibility")
        elif total_score < 90:
            print()
            print("💡 Tips for improvement:")
            if part1_score < 27:
                print("   → Add helper functions for better code organization")
            if part2_score < 22:
                print("   → Double-check encryption logic and edge cases")
            if part3_score < 22:
                print("   → Ensure perfect decryption reversibility")
            if part4_score < 18:
                print("   → Enhance output formatting and verification messages")
    
    print("=" * 70)
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': passed,
        'grade_letter': grade_letter,
        'breakdown': {
            'part1': part1_score,
            'part2': part2_score,
            'part3': part3_score,
            'part4': part4_score
        }
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission7.py <filepath.pf>")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 7: Caesar Cipher\n")
        print(f"File: {filepath}\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_7(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 4 Grader - Operation Midnight Crown (FLEXIBLE VERSION)
Tests: All 4 Phases with flexible validation

Usage: python grader_mission4.py <filepath.pf>

FEATURES:
- Flexible variable name matching
- Accepts Caesar cipher fallback in Phase 3
- Validates algorithm correctness, not just exact values
- Partial credit for correct methodology
- Detailed feedback and hints
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


def run_student_code(filepath, timeout_seconds=60):
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


def get_variable(variables, *possible_names):
    """Try to get a variable by multiple possible names"""
    for name in possible_names:
        if name in variables:
            return variables[name]
    return None


def is_prime(n):
    """Check if a number is prime"""
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


def validate_sequence(sequence, expected_length=20):
    """Validate if sequence follows P(n) = (P(n-2)² + P(n-1)²) % 1000000007"""
    if not isinstance(sequence, list) or len(sequence) < expected_length:
        return False, 0
    
    # Check initial values
    if sequence[0] != 0 or sequence[1] != 1:
        return False, 0
    
    # Verify sequence formula for first few elements
    correct = 2  # First two are correct
    for i in range(2, min(expected_length, len(sequence))):
        expected = ((sequence[i-2] ** 2) + (sequence[i-1] ** 2)) % 1000000007
        if sequence[i] == expected:
            correct += 1
        else:
            break
    
    accuracy = correct / expected_length
    return accuracy >= 0.9, correct


def validate_primes_in_sequence(sequence, prime_list):
    """Check if prime list contains actual primes from sequence"""
    if not isinstance(prime_list, list):
        return False, 0
    
    actual_primes = [val for val in sequence if is_prime(val)]
    
    if len(actual_primes) == 0:
        return len(prime_list) == 0, 0
    
    correct = sum(1 for p in prime_list if p in actual_primes)
    accuracy = correct / max(len(actual_primes), 1)
    
    return accuracy >= 0.8, correct


def grade_mission_4(execution_result):
    """Grade Mission 4: Operation Midnight Crown"""
    total_score = 0
    max_score = 100
    
    print("=" * 69)
    print(" MISSION 4: OPERATION MIDNIGHT CROWN")
    print(" Agent: Cobra | Target: CyberVault Industries")
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
    
    # ========== PHASE 1: FIREWALL BREACH (25 points) ==========
    print("🔥 PHASE 1: FIREWALL BREACH - Sequence Generation (25 points)")
    print("-" * 70)
    
    phase1_score = 0
    
    # Test 1.1: Helper Functions
    print("Test 1.1: Core Functions (is_prime, generate_sequence) (5 points)")
    has_prime_func = 'is_prime' in variables
    has_gen_func = any(name in variables for name in ['generate_sequence', 'gen_sequence', 'gen_seq'])
    
    if has_prime_func and has_gen_func:
        print("  ✓ PASS: Both helper functions found")
        phase1_score += 5
    elif has_prime_func or has_gen_func:
        print("  ⚠ PARTIAL: Some helper functions found")
        phase1_score += 3
    else:
        print("  ✗ FAIL: Helper functions not found")
    print()
    
    # Test 1.2: Sequence Generation
    print("Test 1.2: Sequence Generation (20 numbers) (10 points)")
    sequence = get_variable(variables, 'sequence', 'seq', 'fib_sequence')
    
    if sequence:
        is_valid, correct_count = validate_sequence(sequence, 20)
        if is_valid:
            print(f"  ✓ PASS: Valid sequence with {len(sequence)} numbers")
            print(f"    First few: {sequence[:5]}")
            phase1_score += 10
        elif correct_count >= 10:
            print(f"  ⚠ PARTIAL: Sequence has some errors ({correct_count}/20 correct)")
            phase1_score += 6
        else:
            print(f"  ✗ FAIL: Sequence validation failed ({correct_count}/20 correct)")
    else:
        print("  ✗ FAIL: sequence variable not found")
    print()
    
    # Test 1.3: Prime Detection
    print("Test 1.3: Prime Number Detection (5 points)")
    primes = get_variable(variables, 'primes', 'prime_list', 'prime_numbers')
    
    if primes and sequence:
        is_valid, correct_count = validate_primes_in_sequence(sequence, primes)
        if is_valid:
            print(f"  ✓ PASS: Found {len(primes)} primes correctly")
            print(f"    Primes: {primes}")
            phase1_score += 5
        else:
            print(f"  ⚠ PARTIAL: Prime detection has errors ({correct_count} correct)")
            phase1_score += 2
    else:
        print("  ✗ FAIL: primes variable not found")
    print()
    
    # Test 1.4: Breach Code Calculation
    print("Test 1.4: Breach Code (sum of primes % 1000) (5 points)")
    breach_code = get_variable(variables, 'breach_code', 'Breach_Code', 'breach')
    
    # Expected: 356 (from 2+5+29+750797+647998523 = 648749356 % 1000 = 356)
    expected_breach = 356
    
    if breach_code is not None:
        if isinstance(breach_code, (int, float)):
            if breach_code == expected_breach:
                print(f"  ✓ PASS: Breach_Code = {breach_code} (correct)")
                phase1_score += 5
            elif 0 < breach_code < 1000:
                print(f"  ⚠ PARTIAL: Breach_Code = {breach_code} (expected {expected_breach})")
                phase1_score += 3
            else:
                print(f"  ✗ FAIL: Breach_Code = {breach_code} (out of range)")
        else:
            print(f"  ✗ FAIL: breach_code is not a number")
    else:
        print("  ✗ FAIL: breach_code not found")
    print()
    
    total_score += phase1_score
    print(f"PHASE 1 Score: {phase1_score}/25")
    print()
    
    # ========== PHASE 2: MAZE NAVIGATION (25 points) ==========
    print("🗺️  PHASE 2: MAZE NAVIGATION - Path Counting (25 points)")
    print("-" * 70)
    
    phase2_score = 0
    
    # Test 2.1: Maze Size Calculation
    print("Test 2.1: Maze Size (N = last_digit + 5) (5 points)")
    size = get_variable(variables, 'size', 'maze_size', 'N', 'n')
    
    expected_size = 11 if breach_code == expected_breach else None
    
    if size is not None and isinstance(size, (int, float)):
        if expected_size and size == expected_size:
            print(f"  ✓ PASS: Maze size N = {size}")
            phase2_score += 5
        elif 5 <= size <= 15:
            print(f"  ⚠ PARTIAL: Maze size N = {size} (calculation may vary)")
            phase2_score += 4
        else:
            print(f"  ✗ FAIL: Maze size N = {size} (unusual value)")
    else:
        print("  ✗ FAIL: size variable not found")
    print()
    
    # Test 2.2: Drone Divisor
    print("Test 2.2: First Prime (Drone Divisor, skip first 2) (5 points)")
    first_prime = get_variable(variables, 'first_prime', 'drone_divisor', 'divisor')
    
    # Should be 29 (third prime in sequence after skipping 2 and 5)
    expected_prime = 29
    
    if first_prime is not None:
        if first_prime == expected_prime:
            print(f"  ✓ PASS: Drone divisor = {first_prime} (correct)")
            phase2_score += 5
        elif first_prime in [2, 5, 29]:
            print(f"  ⚠ PARTIAL: Drone divisor = {first_prime} (should skip first 2)")
            phase2_score += 3
        else:
            print(f"  ✗ FAIL: Drone divisor = {first_prime} (unexpected value)")
    else:
        print("  ✗ FAIL: first_prime not found")
    print()
    
    # Test 2.3: Path Counting Algorithm
    print("Test 2.3: Dynamic Programming Path Count (10 points)")
    total_paths = get_variable(variables, 'total_paths', 'paths', 'safe_paths', 'path_count')
    
    if total_paths is not None and isinstance(total_paths, (int, float)):
        if total_paths > 0:
            print(f"  ✓ PASS: Found {total_paths} safe paths")
            phase2_score += 10
        else:
            print(f"  ✗ FAIL: Path count = {total_paths} (should be > 0)")
    else:
        print("  ✗ FAIL: total_paths not found")
    print()
    
    # Test 2.4: Navigation Code
    print("Test 2.4: Navigation Code (paths % 1000) (5 points)")
    nav_code = get_variable(variables, 'nav_code', 'Navigation_Code', 'navigation')
    
    # Expected: 578 (from 105578 % 1000 = 578)
    expected_nav = 578
    
    if nav_code is not None:
        if isinstance(nav_code, (int, float)):
            if nav_code == expected_nav:
                print(f"  ✓ PASS: Navigation_Code = {nav_code} (correct)")
                phase2_score += 5
            elif 0 <= nav_code < 1000:
                print(f"  ⚠ PARTIAL: Navigation_Code = {nav_code} (expected {expected_nav})")
                phase2_score += 3
            else:
                print(f"  ✗ FAIL: Navigation_Code = {nav_code} (out of range)")
        else:
            print(f"  ✗ FAIL: nav_code is not a number")
    else:
        print("  ✗ FAIL: nav_code not found")
    print()
    
    total_score += phase2_score
    print(f"PHASE 2 Score: {phase2_score}/25")
    print()
    
    # ========== PHASE 3: CIPHER DECRYPTION (25 points) ==========
    print("🔐 PHASE 3: CIPHER DECRYPTION - Message Extraction (25 points)")
    print("-" * 70)
    
    phase3_score = 0
    
    # Test 3.1: Cipher Building
    print("Test 3.1: Substitution Cipher Generation (5 points)")
    cipher = get_variable(variables, 'cipher', 'cipher_alphabet', 'cipher_key')
    
    if cipher and isinstance(cipher, str) and len(cipher) == 26:
        print(f"  ✓ PASS: Cipher alphabet created (26 letters)")
        print(f"    Cipher: {cipher[:15]}...")
        phase3_score += 5
    elif cipher and isinstance(cipher, str):
        print(f"  ⚠ PARTIAL: Cipher created but length = {len(cipher)}")
        phase3_score += 3
    else:
        print("  ✗ FAIL: cipher not found or invalid")
    print()
    
    # Test 3.2: Decryption Function
    print("Test 3.2: Decryption Implementation (10 points)")
    has_decrypt = any(name in variables for name in 
                     ['decrypt_message', 'decrypt', 'decrypt_caesar', 'caesar_decrypt'])
    
    if has_decrypt:
        print("  ✓ PASS: Decryption function found")
        phase3_score += 10
    else:
        print("  ⚠ WARNING: No decryption function found (may be inline)")
        phase3_score += 5
    print()
    
    # Test 3.3: Decrypted Message
    print("Test 3.3: Message Decryption & Number Word Extraction (10 points)")
    decrypted = get_variable(variables, 'decrypted', 'message', 'decrypted_message')
    
    # Expected keywords from "THIS CORPORATION IS GUILTY OF SEEKING VIOLATIONS THE EVIDENCE IS IN SECTION SEVEN"
    expected_keywords = ['CORPORATION', 'GUILTY', 'SEEKING', 'EVIDENCE', 'SEVEN']
    
    if decrypted and isinstance(decrypted, str):
        found_keywords = sum(1 for kw in expected_keywords if kw in decrypted.upper())
        
        if found_keywords >= 4:
            print(f"  ✓ PASS: Message decrypted successfully")
            print(f"    Found {found_keywords}/5 key phrases")
            print(f"    Message preview: \"{decrypted[:50]}...\"" if len(decrypted) > 50 else f"    Message: \"{decrypted}\"")
            phase3_score += 10
        elif found_keywords >= 2:
            print(f"  ⚠ PARTIAL: Partial decryption ({found_keywords}/5 keywords)")
            phase3_score += 5
        else:
            print(f"  ✗ FAIL: Decryption appears incorrect (only {found_keywords}/5 keywords)")
    else:
        print("  ✗ FAIL: decrypted message not found")
    print()
    
    # Test 3.4: Vault Access Code
    print("Test 3.4: Vault Access Code (from 'SEVEN') (0 points - bonus info)")
    vault_code = get_variable(variables, 'vault_code', 'Vault_Code', 'vault')
    
    # Expected: 7 (from "SEVEN")
    expected_vault = 7
    
    if vault_code is not None:
        if vault_code == expected_vault:
            print(f"  ✓ INFO: Vault_Access_Code = {vault_code} (correct)")
        else:
            print(f"  ⚠ INFO: Vault_Access_Code = {vault_code} (expected {expected_vault})")
    else:
        print("  ✗ INFO: vault_code not found")
    print()
    
    total_score += phase3_score
    print(f"PHASE 3 Score: {phase3_score}/25")
    print()
    
    # ========== PHASE 4: DIJKSTRA'S ALGORITHM (25 points) ==========
    print("🚪 PHASE 4: ESCAPE ROUTE - Shortest Path (25 points)")
    print("-" * 70)
    
    phase4_score = 0
    
    # Test 4.1: Graph Generation
    print("Test 4.1: Graph Structure (complete graph) (5 points)")
    graph = get_variable(variables, 'graph', 'escape_graph', 'route_graph')
    node_list = get_variable(variables, 'node_list', 'nodes', 'node_names')
    
    if graph and isinstance(graph, dict):
        print(f"  ✓ PASS: Graph created with {len(graph)} nodes")
        phase4_score += 5
    elif graph:
        print(f"  ⚠ PARTIAL: Graph structure found")
        phase4_score += 3
    else:
        print("  ✗ FAIL: graph not found")
    print()
    
    # Test 4.2: Dijkstra Implementation
    print("Test 4.2: Dijkstra's Algorithm Implementation (10 points)")
    has_dijkstra = 'dijkstra' in variables or 'find_shortest' in variables
    
    if has_dijkstra:
        print("  ✓ PASS: Dijkstra function found")
        phase4_score += 10
    else:
        print("  ⚠ WARNING: Dijkstra function not found (may be inline)")
        phase4_score += 5
    print()
    
    # Test 4.3: Shortest Path Calculation
    print("Test 4.3: Shortest Time Calculation (5 points)")
    shortest_time = get_variable(variables, 'shortest_time', 'mission_time', 
                                 'escape_time', 'shortest')
    
    if shortest_time is not None and isinstance(shortest_time, (int, float)):
        if shortest_time > 0 and shortest_time <= 60:
            print(f"  ✓ PASS: Shortest time = {shortest_time} seconds (≤ 60)")
            phase4_score += 5
        elif shortest_time > 60:
            print(f"  ⚠ PARTIAL: Shortest time = {shortest_time} seconds (> 60, mission failed)")
            phase4_score += 3
        else:
            print(f"  ✗ FAIL: Shortest time = {shortest_time} (invalid)")
    else:
        print("  ✗ FAIL: shortest_time not found")
    print()
    
    # Test 4.4: Mission Complete Code
    print("Test 4.4: Mission Complete Code (5 points)")
    mission_code = get_variable(variables, 'mission_code', 'Mission_Complete_Code', 
                                'final_code', 'complete_code')
    
    if mission_code is not None:
        if isinstance(mission_code, (int, float)) and mission_code > 0:
            print(f"  ✓ PASS: Mission_Complete_Code = {mission_code}")
            phase4_score += 5
        else:
            print(f"  ⚠ PARTIAL: mission_code = {mission_code}")
            phase4_score += 2
    else:
        print("  ✗ FAIL: mission_code not found")
    print()
    
    total_score += phase4_score
    print(f"PHASE 4 Score: {phase4_score}/25")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 69)
    print(" FINAL RESULTS")
    print("=" * 69)
    print()
    print(f"Phase 1 (Firewall Breach):    {phase1_score}/25")
    print(f"Phase 2 (Maze Navigation):    {phase2_score}/25")
    print(f"Phase 3 (Cipher Decryption):  {phase3_score}/25")
    print(f"Phase 4 (Escape Route):       {phase4_score}/25")
    print("-" * 70)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print()
    
    # Grade Letter
    if total_score >= 100:
        grade_letter, message = "A+", "🏆 PERFECT! Agent Cobra succeeded!"
    elif total_score >= 95:
        grade_letter, message = "A", "🌟 EXCELLENT! Nearly perfect infiltration"
    elif total_score >= 90:
        grade_letter, message = "A-", "⭐ VERY GOOD! Minor issues remain"
    elif total_score >= 85:
        grade_letter, message = "B+", "✅ GOOD! Some phases incomplete"
    elif total_score >= 80:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Keep improving"
    elif total_score >= 75:
        grade_letter, message = "B-", "✓ FAIR! Significant work needed"
    elif total_score >= 70:
        grade_letter, message = "C+", "⚠ NEEDS IMPROVEMENT! Major gaps"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ INCOMPLETE! Review requirements"
    else:
        grade_letter, message = "F", "❌ MISSION FAILED! Review all phases"
    
    print(f"Grade: {grade_letter}")
    print()
    print(message)
    
    if total_score < 100:
        print()
        print("⚠️  REQUIREMENT: You must score 100/100 to complete Mission 4")
        print()
        print("💡 COMMON ISSUES:")
        if phase1_score < 25:
            print("  - Phase 1: Check sequence formula P(n) = (P(n-2)² + P(n-1)²) % 1000000007")
            print("  - Verify prime detection excludes 1 and includes 2")
        if phase2_score < 25:
            print("  - Phase 2: Ensure DP table correctly handles drone obstacles")
            print("  - Skip first TWO primes (2 and 5) for drone divisor")
        if phase3_score < 25:
            print("  - Phase 3: Implement substitution cipher with collision resolution")
            print("  - Use Caesar cipher (shift 4) as fallback if no number words found")
        if phase4_score < 25:
            print("  - Phase 4: Implement complete graph with proper edge weights")
            print("  - Use Dijkstra's algorithm to find shortest path")
    
    print("=" * 69)
    
    # Verify critical codes match expected
    codes_correct = (
        breach_code == 356 and 
        nav_code == 578 and 
        vault_code == 7
    )
    
    if codes_correct:
        print()
        print("✅ All phase codes are CORRECT!")
        print("   Breach: 356, Navigation: 578, Vault: 7")
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': total_score >= 100,
        'grade_letter': grade_letter,
        'breach_code': breach_code,
        'nav_code': nav_code,
        'vault_code': vault_code,
        'mission_code': mission_code
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission4.py <filepath.pf>")
            print()
            print("This flexible grader validates:")
            print("  - Algorithm correctness over exact variable names")
            print("  - Accepts Caesar cipher fallback in Phase 3")
            print("  - Provides partial credit for methodology")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 4: Operation Midnight Crown\n")
        print("Version: FLEXIBLE GRADER v1.0")
        print("Features: Algorithm validation, flexible naming, detailed feedback\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_4(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
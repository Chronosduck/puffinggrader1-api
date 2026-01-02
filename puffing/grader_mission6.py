#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 6 Grader - Smart Task Manager
Flexible grading that checks for correct logic and task management

Usage: python grader_mission6.py <filepath.pf>
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


def extract_task_names_from_output(output):
    """Extract task names from output"""
    # Look for task names between quotes or in specific patterns
    task_names = []
    
    # Pattern 1: "Task_Name" or Task_Name in output
    patterns = [
        r'(\w+_\w+)',  # Snake_case names
        r'"([^"]+)"',   # Quoted strings
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output)
        task_names.extend(matches)
    
    return task_names


def analyze_code_structure(source_code):
    """Analyze code structure for required elements"""
    results = {
        'has_tasks_array': False,
        'has_dictionaries': False,
        'has_filter_function': False,
        'has_sort_function': False,
        'has_urgent_detection': False,
        'has_loops': 0,
        'has_nested_loops': False,
        'has_status_check': False,
        'has_days_left_comparison': False,
        'has_priority_comparison': False,
        'uses_get_function': False,
        'has_display_function': False,
        'function_count': 0,
        'has_proper_sorting_logic': False
    }
    
    # Check for tasks array with dictionaries
    if 'let tasks as [' in source_code or 'let tasks as[' in source_code:
        results['has_tasks_array'] = True
    
    # Check for dictionary usage
    dict_count = source_code.count('"name"') + source_code.count('"priority"') + \
                 source_code.count('"days_left"') + source_code.count('"status"')
    if dict_count >= 4:
        results['has_dictionaries'] = True
    
    # Check for filter function
    if 'filter' in source_code.lower() and 'pending' in source_code:
        results['has_filter_function'] = True
    
    # Check for sort function
    if 'sort' in source_code.lower():
        results['has_sort_function'] = True
    
    # Check for urgent detection
    if 'urgent' in source_code.lower() and ('days_left' in source_code and 'priority' in source_code):
        results['has_urgent_detection'] = True
    
    # Count loops
    results['has_loops'] = source_code.count('for ') + source_code.count('while ')
    
    # Check for nested loops (sorting logic)
    if 'for i in' in source_code and 'for j in' in source_code:
        results['has_nested_loops'] = True
        results['has_proper_sorting_logic'] = True
    
    # Check for status filtering
    if '"status"' in source_code and 'pending' in source_code:
        results['has_status_check'] = True
    
    # Check for comparison logic
    if 'days_left' in source_code and ('<' in source_code or '>' in source_code):
        results['has_days_left_comparison'] = True
    
    if 'priority' in source_code and ('<' in source_code or '>' in source_code):
        results['has_priority_comparison'] = True
    
    # Check for get() function usage
    if 'get(' in source_code:
        results['uses_get_function'] = True
    
    # Check for display/output function
    if 'display' in source_code.lower() or 'show' in source_code.lower():
        results['has_display_function'] = True
    
    # Count functions
    results['function_count'] = source_code.count('fun ')
    
    return results


def check_task_order_in_output(output):
    """Check if tasks appear in correct order in output"""
    # Expected order: Deploy_API (1 day) -> Fix_login_bug (2 days) -> Prepare_pitch_deck (4 days)
    deploy_pos = output.find('Deploy_API')
    fix_pos = output.find('Fix_login_bug')
    prepare_pos = output.find('Prepare_pitch_deck')
    
    if deploy_pos == -1 or fix_pos == -1 or prepare_pos == -1:
        return False, "Not all pending tasks found in output"
    
    # Check order
    if deploy_pos < fix_pos < prepare_pos:
        return True, "Tasks correctly ordered"
    else:
        return False, f"Tasks in wrong order (positions: Deploy={deploy_pos}, Fix={fix_pos}, Prepare={prepare_pos})"


def check_urgent_tasks_in_output(output):
    """Check if urgent tasks are correctly identified"""
    # Deploy_API: days_left=1, priority=5 -> URGENT
    # Fix_login_bug: days_left=2, priority=5 -> URGENT
    # Prepare_pitch_deck: days_left=4, priority=4 -> NOT URGENT
    
    has_deploy = 'Deploy_API' in output
    has_fix = 'Fix_login_bug' in output
    has_prepare_in_urgent = False
    
    # Check if Prepare_pitch_deck appears in urgent section
    # (it shouldn't, as it's 4 days away)
    urgent_section_start = output.find('เร่งด่วน')
    if urgent_section_start == -1:
        urgent_section_start = output.find('urgent')
    if urgent_section_start == -1:
        urgent_section_start = output.find('🚨')
    
    if urgent_section_start != -1:
        urgent_section = output[urgent_section_start:]
        has_prepare_in_urgent = 'Prepare_pitch_deck' in urgent_section
    
    return {
        'has_deploy_urgent': has_deploy,
        'has_fix_urgent': has_fix,
        'has_prepare_in_urgent': has_prepare_in_urgent,
        'found_urgent_section': urgent_section_start != -1
    }


def grade_mission_6(execution_result):
    """Grade Mission 6 - Smart Task Manager"""
    total_score = 0
    max_score = 100
    
    print("=" * 70)
    print(" MISSION 6: SMART TASK MANAGER")
    print(" กอบกู้ความโกลาหลในสตาร์ทอัพ")
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
        return {
            'score': 0,
            'max_score': max_score,
            'passed': False,
            'grade_letter': 'F'
        }
    
    variables = execution_result.get('variables', {})
    output = execution_result.get('output', '')
    source_code = execution_result.get('source_code', '')
    
    # Analyze code structure
    structure = analyze_code_structure(source_code)
    
    print(f"📊 Code Analysis:")
    print(f"   - Functions defined: {structure['function_count']}")
    print(f"   - Loops used: {structure['has_loops']}")
    print(f"   - Uses dictionaries: {structure['has_dictionaries']}")
    print()
    
    # ========== PART 1: DATA STRUCTURE & INITIALIZATION (20 points) ==========
    print("📝 PART 1: Data Structure & Initialization (20 points)")
    print("-" * 70)
    
    part1_score = 0
    
    # Test 1.1: Tasks Array with Dictionaries (10 points)
    print("Test 1.1: Tasks Array with Dictionary Objects (10 points)")
    
    if structure['has_tasks_array']:
        print("  ✓ Tasks array initialized (+4)")
        part1_score += 4
    else:
        print("  ✗ Missing tasks array")
    
    if structure['has_dictionaries']:
        print("  ✓ Tasks contain dictionary objects with required fields (+6)")
        part1_score += 6
    else:
        print("  ✗ Tasks missing dictionary structure or required fields")
    
    print(f"  Score: {part1_score}/10")
    print()
    
    # Test 1.2: Dictionary Field Usage (10 points)
    print("Test 1.2: Dictionary Field Access (10 points)")
    
    fields_score = 0
    
    if structure['uses_get_function']:
        print("  ✓ Uses get() function to access dictionary fields (+5)")
        fields_score += 5
    else:
        print("  ✗ Missing get() function usage")
    
    if '"name"' in source_code and '"status"' in source_code:
        print("  ✓ Accesses name and status fields (+3)")
        fields_score += 3
    else:
        print("  ✗ Missing name/status field access")
    
    if '"days_left"' in source_code and '"priority"' in source_code:
        print("  ✓ Accesses days_left and priority fields (+2)")
        fields_score += 2
    else:
        print("  ✗ Missing days_left/priority field access")
    
    part1_score += fields_score
    print(f"  Score: {fields_score}/10")
    print()
    
    total_score += part1_score
    print(f"PART 1 Score: {part1_score}/20")
    print()
    
    # ========== PART 2: FILTER PENDING TASKS (20 points) ==========
    print("📝 PART 2: Filter Pending Tasks (20 points)")
    print("-" * 70)
    
    part2_score = 0
    
    # Test 2.1: Filter Function Implementation (12 points)
    print("Test 2.1: Filter Function Logic (12 points)")
    
    filter_score = 0
    
    if structure['has_filter_function']:
        print("  ✓ Filter function defined (+5)")
        filter_score += 5
    else:
        print("  ✗ Missing filter function")
    
    if structure['has_status_check']:
        print("  ✓ Checks status = 'pending' (+4)")
        filter_score += 4
    else:
        print("  ✗ Missing status check logic")
    
    if 'push(' in source_code and 'pending' in source_code:
        print("  ✓ Collects pending tasks into new array (+3)")
        filter_score += 3
    else:
        print("  ✗ Missing task collection logic")
    
    part2_score += filter_score
    print(f"  Score: {filter_score}/12")
    print()
    
    # Test 2.2: Filter Output Verification (8 points)
    print("Test 2.2: Filter Results in Output (8 points)")
    
    output_score = 0
    
    # Check that only pending tasks appear (not "Add_dark_mode")
    has_deploy = 'Deploy_API' in output
    has_fix = 'Fix_login_bug' in output
    has_prepare = 'Prepare_pitch_deck' in output
    has_dark_mode = 'Add_dark_mode' in output
    
    if has_deploy and has_fix and has_prepare:
        print("  ✓ All pending tasks appear in output (+5)")
        output_score += 5
    else:
        print("  ✗ Missing some pending tasks in output")
    
    if not has_dark_mode:
        print("  ✓ Completed tasks filtered out correctly (+3)")
        output_score += 3
    else:
        print("  ⚠ Warning: 'Add_dark_mode' (done) appears in output")
    
    part2_score += output_score
    print(f"  Score: {output_score}/8")
    print()
    
    total_score += part2_score
    print(f"PART 2 Score: {part2_score}/20")
    print()
    
    # ========== PART 3: SORT TASKS (30 points) ==========
    print("📝 PART 3: Sort Tasks by Priority (30 points)")
    print("-" * 70)
    
    part3_score = 0
    
    # Test 3.1: Sort Function Structure (15 points)
    print("Test 3.1: Sort Function Implementation (15 points)")
    
    sort_struct_score = 0
    
    if structure['has_sort_function']:
        print("  ✓ Sort function defined (+4)")
        sort_struct_score += 4
    else:
        print("  ✗ Missing sort function")
    
    if structure['has_nested_loops']:
        print("  ✓ Uses nested loops for sorting (bubble sort) (+5)")
        sort_struct_score += 5
    else:
        print("  ✗ Missing nested loop structure")
    
    if structure['has_days_left_comparison']:
        print("  ✓ Compares days_left values (+3)")
        sort_struct_score += 3
    else:
        print("  ✗ Missing days_left comparison")
    
    if structure['has_priority_comparison']:
        print("  ✓ Compares priority values (+3)")
        sort_struct_score += 3
    else:
        print("  ✗ Missing priority comparison")
    
    part3_score += sort_struct_score
    print(f"  Score: {sort_struct_score}/15")
    print()
    
    # Test 3.2: Correct Sort Order in Output (15 points)
    print("Test 3.2: Correct Task Ordering (15 points)")
    
    order_score = 0
    
    is_correct_order, order_message = check_task_order_in_output(output)
    
    if is_correct_order:
        print("  ✓ Tasks ordered by days_left (ascending) (+10)")
        order_score += 10
        print("  ✓ Tasks with same days_left ordered by priority (desc) (+5)")
        order_score += 5
    else:
        print(f"  ✗ Incorrect task order: {order_message}")
        # Partial credit if tasks are present
        if 'Deploy_API' in output and 'Fix_login_bug' in output:
            print("  ⚠ Partial credit: Tasks present but wrong order (+5)")
            order_score += 5
    
    part3_score += order_score
    print(f"  Score: {order_score}/15")
    print()
    
    total_score += part3_score
    print(f"PART 3 Score: {part3_score}/30")
    print()
    
    # ========== PART 4: URGENT TASK DETECTION (30 points) ==========
    print("📝 PART 4: Urgent Task Detection (30 points)")
    print("-" * 70)
    
    part4_score = 0
    
    # Test 4.1: Urgent Detection Logic (18 points)
    print("Test 4.1: Urgent Task Detection Function (18 points)")
    
    urgent_logic_score = 0
    
    if structure['has_urgent_detection']:
        print("  ✓ Urgent detection function defined (+6)")
        urgent_logic_score += 6
    else:
        print("  ✗ Missing urgent detection function")
    
    # Check for conditions: days_left <= 2 and priority >= 4
    if '<=2' in source_code.replace(' ', '') or '<= 2' in source_code:
        print("  ✓ Checks days_left <= 2 (+6)")
        urgent_logic_score += 6
    else:
        print("  ✗ Missing days_left <= 2 condition")
    
    if '>=4' in source_code.replace(' ', '') or '>= 4' in source_code:
        print("  ✓ Checks priority >= 4 (+6)")
        urgent_logic_score += 6
    else:
        print("  ✗ Missing priority >= 4 condition")
    
    part4_score += urgent_logic_score
    print(f"  Score: {urgent_logic_score}/18")
    print()
    
    # Test 4.2: Urgent Tasks Output (12 points)
    print("Test 4.2: Correct Urgent Tasks Identified (12 points)")
    
    urgent_output_score = 0
    urgent_check = check_urgent_tasks_in_output(output)
    
    if urgent_check['found_urgent_section']:
        print("  ✓ Urgent tasks section present in output (+3)")
        urgent_output_score += 3
    else:
        print("  ✗ Missing urgent tasks section")
    
    if urgent_check['has_deploy_urgent']:
        print("  ✓ Deploy_API identified as urgent (+4)")
        urgent_output_score += 4
    else:
        print("  ✗ Deploy_API not in urgent section")
    
    if urgent_check['has_fix_urgent']:
        print("  ✓ Fix_login_bug identified as urgent (+4)")
        urgent_output_score += 4
    else:
        print("  ✗ Fix_login_bug not in urgent section")
    
    if not urgent_check['has_prepare_in_urgent']:
        print("  ✓ Prepare_pitch_deck correctly NOT urgent (+1)")
        urgent_output_score += 1
    else:
        print("  ⚠ Prepare_pitch_deck incorrectly marked as urgent")
    
    part4_score += urgent_output_score
    print(f"  Score: {urgent_output_score}/12")
    print()
    
    total_score += part4_score
    print(f"PART 4 Score: {part4_score}/30")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 70)
    print(" FINAL RESULTS")
    print("=" * 70)
    print()
    print(f"Part 1 (Data Structure):          {part1_score:>3}/20")
    print(f"Part 2 (Filter Pending):          {part2_score:>3}/20")
    print(f"Part 3 (Sort Tasks):              {part3_score:>3}/30")
    print(f"Part 4 (Urgent Detection):        {part4_score:>3}/30")
    print("-" * 70)
    print(f"TOTAL SCORE:                      {total_score:>3}/{max_score}")
    print()
    
    # Grading scale
    if total_score >= 95:
        grade_letter, message = "A+", "🏆 EXCEPTIONAL! Perfect task management system!"
    elif total_score >= 90:
        grade_letter, message = "A", "🌟 EXCELLENT! Outstanding implementation!"
    elif total_score >= 85:
        grade_letter, message = "A-", "⭐ VERY GOOD! Strong task manager!"
    elif total_score >= 80:
        grade_letter, message = "B+", "✅ GOOD! Solid work!"
    elif total_score >= 75:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Good effort!"
    elif total_score >= 70:
        grade_letter, message = "B-", "✓ PASSING! Meets requirements!"
    elif total_score >= 65:
        grade_letter, message = "C+", "⚠ BELOW AVERAGE! Needs improvement"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ MINIMAL PASS! Review concepts"
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
        print("⚠️  REQUIREMENT: You need at least 70/100 to pass Mission 6")
        print()
        if part1_score < 14:
            print("   Focus Area: Data Structure (Part 1)")
            print("   → Use proper dictionary format with quoted keys")
            print("   → Initialize tasks array with all required fields")
            print("   → Use get() function to access dictionary values")
        if part2_score < 14:
            print("   Focus Area: Filter Pending Tasks (Part 2)")
            print("   → Create filter function to check status")
            print("   → Only collect tasks with status = 'pending'")
            print("   → Verify completed tasks are excluded")
        if part3_score < 21:
            print("   Focus Area: Sort Tasks (Part 3)")
            print("   → Implement nested loops for bubble sort")
            print("   → Sort by days_left first (ascending)")
            print("   → Then by priority (descending) for ties")
        if part4_score < 21:
            print("   Focus Area: Urgent Detection (Part 4)")
            print("   → Check days_left <= 2 AND priority >= 4")
            print("   → Create separate urgent tasks list")
            print("   → Display urgent tasks clearly")
    else:
        print("=" * 70)
        print("✅ PASSED! Startup chaos solved! 🚀")
        
        if total_score == 100:
            print()
            print("💯 PERFECT SCORE! You've mastered:")
            print("   ✓ Dictionary data structures")
            print("   ✓ Array filtering algorithms")
            print("   ✓ Multi-criteria sorting")
            print("   ✓ Conditional logic for urgency detection")
            print()
            print("🎉 The startup team can now stay organized!")
        elif total_score < 90:
            print()
            print("💡 Tips for perfection:")
            if part1_score < 20:
                print("   → Ensure all dictionary fields are properly quoted")
            if part2_score < 20:
                print("   → Double-check filter logic for edge cases")
            if part3_score < 30:
                print("   → Verify sorting handles ties correctly")
            if part4_score < 30:
                print("   → Test urgent detection with boundary conditions")
    
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
            print("Usage: python grader_mission6.py <filepath.pf>")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 6: Smart Task Manager\n")
        print(f"File: {filepath}\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_6(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

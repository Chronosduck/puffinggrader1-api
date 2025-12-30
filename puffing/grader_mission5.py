#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 5 Grader - Café Algorithm Analysis
Flexible grading that checks for correct logic and calculations

Usage: python grader_mission5.py <filepath.pf>
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


def compare_values(expected, actual, tolerance=1.0):
    """Compare two values with tolerance"""
    if actual is None:
        return False
    try:
        expected_float = float(expected)
        actual_float = float(actual)
        return abs(expected_float - actual_float) <= tolerance
    except (ValueError, TypeError):
        return False


def find_value_in_numbers(expected, numbers, tolerance=1.0):
    """Check if expected value exists in list of numbers"""
    return any(compare_values(expected, num, tolerance) for num in numbers)


def analyze_code_structure(source_code):
    """Analyze code structure for required elements"""
    results = {
        'has_orders_array': False,
        'has_order_generation': False,
        'has_hour_stats': False,
        'has_peak_hour_detection': False,
        'has_stress_score_calc': False,
        'has_inventory_items': False,
        'has_waste_calculation': False,
        'has_optimal_qty_calc': False,
        'has_customer_data': False,
        'has_critical_periods': False,
        'has_menu_items': False,
        'has_profit_margin_calc': False,
        'has_while_loops': 0,
        'has_dictionaries': 0,
        'has_nested_structures': False,
        'uses_mathematical_operations': False,
        'section_headers': []
    }
    
    # Check for orders array
    if 'let orders as [' in source_code or 'let orders as[' in source_code:
        results['has_orders_array'] = True
    
    # Check for order generation loop
    if 'while' in source_code and 'random' in source_code and 'push(orders' in source_code:
        results['has_order_generation'] = True
    
    # Check for hour statistics
    if 'hour_stats' in source_code or 'hour_data' in source_code:
        results['has_hour_stats'] = True
    
    # Check for peak hour detection
    if 'peak_hour' in source_code and 'max_stress' in source_code:
        results['has_peak_hour_detection'] = True
    
    # Check for stress score calculation
    if 'stress_score' in source_code:
        results['has_stress_score_calc'] = True
    
    # Check for inventory items
    if 'inventory_items' in source_code:
        results['has_inventory_items'] = True
    
    # Check for waste calculation
    if 'waste' in source_code and 'cost' in source_code:
        results['has_waste_calculation'] = True
    
    # Check for optimal quantity calculation
    if 'optimal' in source_code:
        results['has_optimal_qty_calc'] = True
    
    # Check for customer data
    if 'customer_data' in source_code:
        results['has_customer_data'] = True
    
    # Check for critical periods
    if 'critical_periods' in source_code:
        results['has_critical_periods'] = True
    
    # Check for menu items
    if 'menu_items' in source_code:
        results['has_menu_items'] = True
    
    # Check for profit margin calculation
    if 'profit_margin' in source_code or 'profit_per_unit' in source_code:
        results['has_profit_margin_calc'] = True
    
    # Count while loops
    results['has_while_loops'] = source_code.count('while')
    
    # Count dictionary usage
    results['has_dictionaries'] = source_code.count('{') - source_code.count('{{')
    
    # Check for nested structures
    if 'while' in source_code and ('if' in source_code or 'elif' in source_code):
        results['has_nested_structures'] = True
    
    # Check for mathematical operations
    if any(op in source_code for op in ['*', '/', '+', '-', '%']):
        results['uses_mathematical_operations'] = True
    
    # Detect section headers (Thai text)
    thai_headers = re.findall(r'print\(".*ภารกิจ.*"\)', source_code)
    results['section_headers'] = thai_headers
    
    return results


def grade_mission_5(execution_result):
    """Grade Mission 5 with flexible checking"""
    total_score = 0
    max_score = 100
    
    print("=" * 69)
    print(" MISSION 5: CAFÉ ALGORITHM ANALYSIS")
    print(" FLEXIBLE GRADING (Logic + Calculations)")
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
    print(f"📝 Detected {len(structure['section_headers'])} section headers")
    print(f"🔁 Found {structure['has_while_loops']} while loops")
    print()
    
    # ========== PART 1: MISSION 1 - PEAK HOUR ANALYSIS (25 points) ==========
    print("📝 PART 1: MISSION 1 - Peak Hour Analysis (25 points)")
    print("-" * 70)
    
    mission1_score = 0
    
    # Test 1.1: Data Structure Setup (8 points)
    print("Test 1.1: Data Structure Setup (8 points)")
    data_score = 0
    
    if structure['has_orders_array']:
        print("  ✓ Orders array initialized (+3)")
        data_score += 3
    else:
        print("  ✗ Missing orders array")
    
    if structure['has_order_generation']:
        print("  ✓ Order generation loop implemented (+3)")
        data_score += 3
    else:
        print("  ✗ Missing order generation")
    
    if structure['has_hour_stats']:
        print("  ✓ Hour statistics structure created (+2)")
        data_score += 2
    else:
        print("  ✗ Missing hour statistics")
    
    mission1_score += data_score
    print(f"  Score: {data_score}/8")
    print()
    
    # Test 1.2: Hour Statistics Calculation (9 points)
    print("Test 1.2: Hour Statistics Processing (9 points)")
    stats_score = 0
    
    if structure['has_stress_score_calc']:
        print("  ✓ Stress score calculation implemented (+4)")
        stats_score += 4
    else:
        print("  ✗ Missing stress score calculation")
    
    if structure['has_while_loops'] >= 3:
        print("  ✓ Multiple while loops for processing (+3)")
        stats_score += 3
    else:
        print("  ⚠ Insufficient loops for processing")
    
    if structure['uses_mathematical_operations']:
        print("  ✓ Mathematical operations present (+2)")
        stats_score += 2
    else:
        print("  ✗ Missing mathematical operations")
    
    mission1_score += stats_score
    print(f"  Score: {stats_score}/9")
    print()
    
    # Test 1.3: Peak Hour Detection (8 points)
    print("Test 1.3: Peak Hour Detection & Output (8 points)")
    peak_score = 0
    
    if structure['has_peak_hour_detection']:
        print("  ✓ Peak hour detection logic present (+4)")
        peak_score += 4
    else:
        print("  ✗ Missing peak hour detection")
    
    # Check for peak_code in output (should be sum of 3 peak hours)
    # Expected range: 30-60 (e.g., 8+12+14=34, or similar combinations)
    peak_code_found = any(30 <= num <= 60 and num == int(num) for num in output_numbers)
    
    if peak_code_found:
        print("  ✓ Peak Hour Code calculated and displayed (+4)")
        peak_score += 4
    else:
        print("  ⚠ Peak Hour Code not found or incorrect")
    
    mission1_score += peak_score
    print(f"  Score: {peak_score}/8")
    print()
    
    total_score += mission1_score
    print(f"PART 1 Score: {mission1_score}/25")
    print()
    
    # ========== PART 2: MISSION 2 - INVENTORY OPTIMIZATION (25 points) ==========
    print("📝 PART 2: MISSION 2 - Inventory Optimization (25 points)")
    print("-" * 70)
    
    mission2_score = 0
    
    # Test 2.1: Inventory Data Structure (8 points)
    print("Test 2.1: Inventory Data Structure (8 points)")
    inv_struct_score = 0
    
    if structure['has_inventory_items']:
        print("  ✓ Inventory items array created (+4)")
        inv_struct_score += 4
    else:
        print("  ✗ Missing inventory items array")
    
    if 'shelf_life' in source_code and 'avg_daily_sales' in source_code:
        print("  ✓ Complete item properties defined (+4)")
        inv_struct_score += 4
    else:
        print("  ✗ Missing item properties")
    
    mission2_score += inv_struct_score
    print(f"  Score: {inv_struct_score}/8")
    print()
    
    # Test 2.2: Waste & Optimization Calculation (10 points)
    print("Test 2.2: Waste & Optimization Calculations (10 points)")
    waste_score = 0
    
    if structure['has_waste_calculation']:
        print("  ✓ Waste cost calculation implemented (+4)")
        waste_score += 4
    else:
        print("  ✗ Missing waste calculation")
    
    if structure['has_optimal_qty_calc']:
        print("  ✓ Optimal quantity calculation present (+3)")
        waste_score += 3
    else:
        print("  ✗ Missing optimal quantity calculation")
    
    # Check for savings calculation (should see savings values in output)
    if 'savings' in source_code.lower() or 'ประหยัด' in source_code:
        print("  ✓ Savings calculation implemented (+3)")
        waste_score += 3
    else:
        print("  ✗ Missing savings calculation")
    
    mission2_score += waste_score
    print(f"  Score: {waste_score}/10")
    print()
    
    # Test 2.3: Inventory Code Output (7 points)
    print("Test 2.3: Total Waste Cost & Inventory Code (7 points)")
    inv_output_score = 0
    
    # Expected total_waste_cost for given data: ~861 baht
    # Expected inventory_code: ~258
    waste_cost_found = find_value_in_numbers(861, output_numbers, tolerance=50)
    inventory_code_found = find_value_in_numbers(258, output_numbers, tolerance=30)
    
    if waste_cost_found:
        print("  ✓ Total waste cost calculated correctly (+3)")
        inv_output_score += 3
    else:
        print("  ⚠ Total waste cost not found or incorrect")
    
    if inventory_code_found:
        print("  ✓ Inventory Code calculated and displayed (+4)")
        inv_output_score += 4
    else:
        print("  ⚠ Inventory Code not found or incorrect")
    
    mission2_score += inv_output_score
    print(f"  Score: {inv_output_score}/7")
    print()
    
    total_score += mission2_score
    print(f"PART 2 Score: {mission2_score}/25")
    print()
    
    # ========== PART 3: MISSION 3 - CUSTOMER PATTERN ANALYSIS (25 points) ==========
    print("📝 PART 3: MISSION 3 - Customer Pattern Analysis (25 points)")
    print("-" * 70)
    
    mission3_score = 0
    
    # Test 3.1: Customer Data Structure (8 points)
    print("Test 3.1: Customer Data Structure (8 points)")
    cust_struct_score = 0
    
    if structure['has_customer_data']:
        print("  ✓ Customer data array created (+4)")
        cust_struct_score += 4
    else:
        print("  ✗ Missing customer data array")
    
    if 'wait_time' in source_code and 'customers' in source_code:
        print("  ✓ Customer and wait time data present (+4)")
        cust_struct_score += 4
    else:
        print("  ✗ Missing customer/wait time fields")
    
    mission3_score += cust_struct_score
    print(f"  Score: {cust_struct_score}/8")
    print()
    
    # Test 3.2: Critical Period Detection (10 points)
    print("Test 3.2: Critical Period Detection Logic (10 points)")
    critical_score = 0
    
    if structure['has_critical_periods']:
        print("  ✓ Critical periods detection implemented (+5)")
        critical_score += 5
    else:
        print("  ✗ Missing critical periods detection")
    
    # Check for conditions: customers > 15 and wait_time > 10
    if '>15' in source_code.replace(' ', '') and '>10' in source_code.replace(' ', ''):
        print("  ✓ Correct threshold conditions (>15 customers, >10 min) (+5)")
        critical_score += 5
    else:
        print("  ⚠ Threshold conditions not found or incorrect")
    
    mission3_score += critical_score
    print(f"  Score: {critical_score}/10")
    print()
    
    # Test 3.3: Pattern Code Output (7 points)
    print("Test 3.3: Critical Periods Count & Pattern Code (7 points)")
    pattern_score = 0
    
    # Expected critical_periods: 6
    # Expected pattern_code: 3 (max critical count per day)
    critical_count_found = find_value_in_numbers(6, output_numbers, tolerance=1)
    pattern_code_found = find_value_in_numbers(3, output_numbers, tolerance=1)
    
    if critical_count_found:
        print("  ✓ Critical periods count correct (+3)")
        pattern_score += 3
    else:
        print("  ⚠ Critical periods count not found")
    
    if pattern_code_found:
        print("  ✓ Pattern Code calculated correctly (+4)")
        pattern_score += 4
    else:
        print("  ⚠ Pattern Code not found")
    
    mission3_score += pattern_score
    print(f"  Score: {pattern_score}/7")
    print()
    
    total_score += mission3_score
    print(f"PART 3 Score: {mission3_score}/25")
    print()
    
    # ========== PART 4: MISSION 4 - MENU OPTIMIZATION (25 points) ==========
    print("📝 PART 4: MISSION 4 - Menu Optimization (25 points)")
    print("-" * 70)
    
    mission4_score = 0
    
    # Test 4.1: Menu Data Structure (8 points)
    print("Test 4.1: Menu Data Structure (8 points)")
    menu_struct_score = 0
    
    if structure['has_menu_items']:
        print("  ✓ Menu items array created (+4)")
        menu_struct_score += 4
    else:
        print("  ✗ Missing menu items array")
    
    if structure['has_profit_margin_calc']:
        print("  ✓ Profit margin calculation present (+4)")
        menu_struct_score += 4
    else:
        print("  ✗ Missing profit margin calculation")
    
    mission4_score += menu_struct_score
    print(f"  Score: {menu_struct_score}/8")
    print()
    
    # Test 4.2: Menu Categorization (10 points)
    print("Test 4.2: Menu Categorization Logic (10 points)")
    category_score = 0
    
    # Check for star items logic (high sales + high rating + high margin)
    if '⭐' in source_code or 'star' in source_code.lower() or 'ดาวเด่น' in source_code:
        print("  ✓ Star items categorization implemented (+5)")
        category_score += 5
    else:
        print("  ✗ Missing star items logic")
    
    # Check for cash cow logic (high sales, price increase)
    if '💰' in source_code or 'cash' in source_code.lower() or 'แหล่งเงิน' in source_code:
        print("  ✓ Cash cow categorization implemented (+5)")
        category_score += 5
    else:
        print("  ✗ Missing cash cow logic")
    
    mission4_score += category_score
    print(f"  Score: {category_score}/10")
    print()
    
    # Test 4.3: Signature Drink & Menu Code (7 points)
    print("Test 4.3: Signature Drink Calculation & Menu Code (7 points)")
    signature_score = 0
    
    # Check for signature drink calculation
    if 'signature' in source_code.lower() or 'ซิกเนเจอร์' in source_code:
        print("  ✓ Signature drink calculation present (+3)")
        signature_score += 3
    else:
        print("  ⚠ Signature drink calculation not found")
    
    # Menu code should be calculated from peak_code + inventory_code
    # Expected range: 200-400
    menu_code_found = any(200 <= num <= 400 and num % 5 == 0 for num in output_numbers)
    
    if menu_code_found:
        print("  ✓ Menu Code calculated and displayed (+4)")
        signature_score += 4
    else:
        print("  ⚠ Menu Code not found or incorrect format")
    
    mission4_score += signature_score
    print(f"  Score: {signature_score}/7")
    print()
    
    total_score += mission4_score
    print(f"PART 4 Score: {mission4_score}/25")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 69)
    print(" FINAL RESULTS")
    print("=" * 69)
    print()
    print(f"Part 1 (Peak Hour Analysis):      {mission1_score:>3}/25")
    print(f"Part 2 (Inventory Optimization):  {mission2_score:>3}/25")
    print(f"Part 3 (Customer Patterns):       {mission3_score:>3}/25")
    print(f"Part 4 (Menu Optimization):       {mission4_score:>3}/25")
    print("-" * 70)
    print(f"TOTAL SCORE:                      {total_score:>3}/{max_score}")
    print()
    
    # Grading scale
    if total_score >= 95:
        grade_letter, message = "A+", "🏆 EXCEPTIONAL! Outstanding café analysis!"
    elif total_score >= 90:
        grade_letter, message = "A", "🌟 EXCELLENT! Very strong implementation"
    elif total_score >= 85:
        grade_letter, message = "A-", "⭐ VERY GOOD! Solid data analysis"
    elif total_score >= 80:
        grade_letter, message = "B+", "✅ GOOD! Good algorithmic thinking"
    elif total_score >= 75:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Decent work"
    elif total_score >= 70:
        grade_letter, message = "B-", "✓ PASSING! Meets requirements"
    elif total_score >= 65:
        grade_letter, message = "C+", "⚠ BELOW AVERAGE! Some gaps"
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
        print("=" * 69)
        print("⚠️  REQUIREMENT: You need at least 70/100 to pass Mission 5")
        print()
        if mission1_score < 18:
            print("   Focus Area: Peak Hour Analysis (Part 1)")
            print("   → Initialize orders array properly")
            print("   → Implement hour statistics calculation")
            print("   → Calculate and display peak_code")
        elif mission2_score < 18:
            print("   Focus Area: Inventory Optimization (Part 2)")
            print("   → Set up inventory items with all properties")
            print("   → Calculate waste costs correctly")
            print("   → Compute optimal quantities and savings")
        elif mission3_score < 18:
            print("   Focus Area: Customer Pattern Analysis (Part 3)")
            print("   → Create customer data structure")
            print("   → Implement critical period detection")
            print("   → Calculate pattern_code correctly")
        else:
            print("   Focus Area: Menu Optimization (Part 4)")
            print("   → Categorize menu items (stars vs cash cows)")
            print("   → Calculate profit margins")
            print("   → Generate signature drink recommendation")
    else:
        print("=" * 69)
        print("✅ PASSED! Your café analysis is comprehensive")
        
        if total_score < 90:
            print()
            print("💡 Tips for improvement:")
            if mission1_score < 23:
                print("   → Add more detailed stress score analysis")
            if mission2_score < 23:
                print("   → Include more inventory optimization metrics")
            if mission3_score < 23:
                print("   → Enhance customer pattern detection")
            if mission4_score < 23:
                print("   → Add more sophisticated menu categorization")
    
    print("=" * 69)
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': passed,
        'grade_letter': grade_letter,
        'breakdown': {
            'part1': mission1_score,
            'part2': mission2_score,
            'part3': mission3_score,
            'part4': mission4_score
        }
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission5.py <filepath.pf>")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 5: Café Algorithm Analysis\n")
        print(f"File: {filepath}\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_5(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
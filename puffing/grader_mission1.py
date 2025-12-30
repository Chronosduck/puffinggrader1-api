#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission 1 Grader - Pathfinding & Backtracking (Production Version)
Tests functionality with maximum flexibility for correct solutions

Usage: python grader_mission1.py <filepath.pf>
"""

import sys
import os
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


def convert_puffing_array_to_python(arr):
    """Convert Puffing 1-indexed array to Python 0-indexed list"""
    if not isinstance(arr, (list, dict)):
        return arr
    
    if isinstance(arr, dict):
        result = []
        i = 1
        while i in arr:
            result.append(convert_puffing_array_to_python(arr[i]))
            i += 1
        return result
    
    return [convert_puffing_array_to_python(item) for item in arr]


def find_maze_by_size(variables, rows, cols):
    """Find a maze variable with specific dimensions"""
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if isinstance(converted, list) and len(converted) == rows:
                if all(isinstance(row, list) and len(row) == cols for row in converted):
                    return name, converted
    return None, None


def find_all_2d_paths(variables):
    """Find ALL variables that could be 2D paths"""
    paths = []
    
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if isinstance(converted, list) and len(converted) > 0:
                # Check if it's an array of coordinate pairs
                is_path = True
                for item in converted[:min(5, len(converted))]:
                    if not (isinstance(item, list) and len(item) == 2):
                        is_path = False
                        break
                    if not (isinstance(item[0], int) and isinstance(item[1], int)):
                        is_path = False
                        break
                    # Coordinates should be reasonable (1-50 range)
                    if not (1 <= item[0] <= 50 and 1 <= item[1] <= 50):
                        is_path = False
                        break
                
                if is_path:
                    paths.append((name, converted))
    
    return paths


def find_paths_collection(variables):
    """Find variable containing multiple paths"""
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if isinstance(converted, list) and len(converted) > 1:
                valid_paths = 0
                for path in converted[:min(3, len(converted))]:
                    if isinstance(path, list) and len(path) > 0:
                        if isinstance(path[0], list) and len(path[0]) == 2:
                            if isinstance(path[0][0], int) and isinstance(path[0][1], int):
                                valid_paths += 1
                
                if valid_paths >= 2:
                    return name, converted
    return None, None


def check_maze_has_treasures(maze):
    """Check if maze contains treasure cells (value 3)"""
    for row in maze:
        for cell in row:
            if cell == 3:
                return True
    return False


def check_maze_is_3d(maze):
    """Check if maze is 3D structure"""
    if not isinstance(maze, list) or len(maze) < 3:
        return False
    for floor in maze:
        if not isinstance(floor, list):
            return False
        for row in floor:
            if not isinstance(row, list):
                return False
    return True


def validate_path_reaches_goal(maze, path):
    """Check if path reaches goal (value 2)"""
    if not path or len(path) == 0:
        return False
    
    last_pos = path[-1]
    if not isinstance(last_pos, list) or len(last_pos) < 2:
        return False
    
    # Convert from 1-indexed to 0-indexed
    x, y = last_pos[0] - 1, last_pos[1] - 1
    
    if x < 0 or x >= len(maze) or y < 0 or y >= len(maze[0]):
        return False
    
    return maze[x][y] == 2


def count_functions_in_variables(variables):
    """Count how many callable functions exist"""
    count = 0
    for value in variables.values():
        if callable(value):
            count += 1
    return count


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


def grade_mission_1(execution_result):
    """Grade Mission 1: Pathfinding with Backtracking"""
    total_score = 0
    max_score = 100
    
    print("=" * 69)
    print(" MISSION 1: PATHFINDING WITH BACKTRACKING")
    print(" Testing: MAIN + 1A (Shortest) + 1B (Treasures) + 1C (3D Maze)")
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
    
    # ========== PART 1: MAIN TASK (30 points) ==========
    print("📝 PART 1: MAIN TASK - Basic Pathfinding (30 points)")
    print("-" * 70)
    
    main_score = 0
    
    # Test 1.1: Core Functions
    print("Test 1.1: Core Functions (8 points)")
    func_count = count_functions_in_variables(variables)
    if func_count >= 2:
        print(f"  ✓ PASS: Found {func_count} functions (pathfinding logic present)")
        main_score += 8
    else:
        print(f"  ✗ FAIL: Only {func_count} functions found (need at least 2)")
    print()
    
    # Test 1.2: Maze Definition
    print("Test 1.2: Maze Definition (7 points)")
    maze_name, maze = find_maze_by_size(variables, 5, 5)
    if maze:
        print(f"  ✓ PASS: Found 5x5 maze (variable: {maze_name})")
        main_score += 7
    else:
        print("  ✗ FAIL: No 5x5 maze found")
        maze = None
    print()
    
    # Test 1.3: Path Found (Improved - checks ALL paths)
    print("Test 1.3: Path Discovery (15 points)")
    all_paths = find_all_2d_paths(variables)
    
    best_path = None
    best_path_name = None
    
    if all_paths:
        # Try to find a path that reaches the goal
        for name, path in all_paths:
            # Prefer paths with reasonable length for a 5x5 maze
            if 5 <= len(path) <= 20:
                if maze and validate_path_reaches_goal(maze, path):
                    best_path = path
                    best_path_name = name
                    print(f"  ✓ PASS: Valid path found (variable: {best_path_name}, {len(path)} steps)")
                    print(f"  ✓ BONUS: Path correctly reaches goal")
                    main_score += 15
                    break
        
        # If no perfect path, give partial credit
        if not best_path:
            # Just find any reasonable-length path
            for name, path in all_paths:
                if 5 <= len(path) <= 20:
                    best_path = path
                    best_path_name = name
                    print(f"  ✓ PASS: Path found (variable: {best_path_name}, {len(path)} steps)")
                    print(f"  ⚠ Note: Goal validation could not be confirmed")
                    main_score += 10
                    break
    
    if not best_path:
        print("  ✗ FAIL: No valid path found")
    print()
    
    total_score += main_score
    print(f"PART 1 Score: {main_score}/30")
    print()
    
    # ========== PART 2: SUBTASK 1A (20 points) ==========
    print("📝 PART 2: SUBTASK 1A - Finding Shortest Path (20 points)")
    print("-" * 70)
    
    subtask_1a_score = 0
    
    print("Test 2.1: Maze 1A Definition (5 points)")
    maze_1a_name, maze_1a = find_maze_by_size(variables, 6, 6)
    if maze_1a:
        print(f"  ✓ PASS: Found 6x6 maze (variable: {maze_1a_name})")
        subtask_1a_score += 5
    else:
        print("  ✗ FAIL: No 6x6 maze found")
    print()
    
    print("Test 2.2: Multiple Path Finding (8 points)")
    paths_name, all_paths_collection = find_paths_collection(variables)
    
    if all_paths_collection and len(all_paths_collection) > 1:
        print(f"  ✓ PASS: Found {len(all_paths_collection)} paths (variable: {paths_name})")
        subtask_1a_score += 8
    else:
        print("  ✗ FAIL: No multiple paths collection found")
    print()
    
    print("Test 2.3: Shortest Path Analysis (7 points)")
    if all_paths_collection and len(all_paths_collection) > 1:
        lengths = [len(p) for p in all_paths_collection]
        min_len = min(lengths)
        max_len = max(lengths)
        
        # Check if output mentions path comparison
        has_comparison = any(keyword in output.lower() for keyword in 
                           ['shortest', 'longest', 'path', 'steps', 'route', 'found'])
        
        if has_comparison:
            print(f"  ✓ PASS: Path analysis present (range: {min_len}-{max_len} steps)")
            subtask_1a_score += 7
        else:
            print("  ⚠ PARTIAL: Paths found but no analysis output")
            subtask_1a_score += 3
    print()
    
    total_score += subtask_1a_score
    print(f"PART 2 Score: {subtask_1a_score}/20")
    print()
    
    # ========== PART 3: SUBTASK 1B (25 points) ==========
    print("📝 PART 3: SUBTASK 1B - Treasure Collection (25 points)")
    print("-" * 70)
    
    subtask_1b_score = 0
    
    print("Test 3.1: Treasure Maze Definition (5 points)")
    treasure_maze = None
    treasure_maze_name = None
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if isinstance(converted, list) and len(converted) == 6:
                if all(isinstance(row, list) and len(row) == 6 for row in converted):
                    if check_maze_has_treasures(converted):
                        treasure_maze = converted
                        treasure_maze_name = name
                        print(f"  ✓ PASS: Found 6x6 maze with treasures (variable: {name})")
                        subtask_1b_score += 5
                        break
    
    if not treasure_maze:
        print("  ✗ FAIL: No 6x6 treasure maze found")
    print()
    
    print("Test 3.2: Treasure Counting (5 points)")
    if treasure_maze:
        treasure_count = sum(1 for row in treasure_maze for cell in row if cell == 3)
        print(f"  ✓ PASS: {treasure_count} treasures detected in maze")
        subtask_1b_score += 5
    else:
        print("  ✗ FAIL: No treasure maze to analyze")
    print()
    
    print("Test 3.3: State Space Tracking (7 points)")
    if func_count >= 5:
        print(f"  ✓ PASS: Sufficient functions ({func_count}) for state tracking")
        subtask_1b_score += 7
    elif func_count >= 3:
        print(f"  ⚠ PARTIAL: Some functions ({func_count}) but may lack full tracking")
        subtask_1b_score += 3
    else:
        print("  ✗ FAIL: Insufficient functions for state tracking")
    print()
    
    print("Test 3.4: Complete Treasure Collection (8 points)")
    success_indicators = ['collected', 'treasure', 'success', '✓', 'complete', 'gather']
    has_success = any(indicator in output.lower() for indicator in success_indicators)
    
    # Check for treasure collection path
    treasure_path_found = False
    for name, path in find_all_2d_paths(variables):
        if len(path) > 10:  # Treasure paths are typically longer
            treasure_path_found = True
            break
    
    if has_success and treasure_path_found:
        print("  ✓ PASS: Treasure collection completed successfully")
        subtask_1b_score += 8
    elif treasure_path_found:
        print("  ⚠ PARTIAL: Path exists but completion unclear")
        subtask_1b_score += 4
    else:
        print("  ✗ FAIL: No treasure collection path found")
    print()
    
    total_score += subtask_1b_score
    print(f"PART 3 Score: {subtask_1b_score}/25")
    print()
    
    # ========== PART 4: SUBTASK 1C (25 points) ==========
    print("📝 PART 4: SUBTASK 1C - 3D Maze Navigation (25 points)")
    print("-" * 70)
    
    subtask_1c_score = 0
    
    print("Test 4.1: 3D Maze Structure (5 points)")
    maze_3d = None
    maze_3d_name = None
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if check_maze_is_3d(converted):
                maze_3d = converted
                maze_3d_name = name
                print(f"  ✓ PASS: Found 3D maze with {len(converted)} floors (variable: {name})")
                subtask_1c_score += 5
                break
    
    if not maze_3d:
        print("  ✗ FAIL: No 3D maze structure found")
    print()
    
    print("Test 4.2: 3D Movement Functions (7 points)")
    if func_count >= 7:
        print(f"  ✓ PASS: Sufficient functions ({func_count}) for 3D navigation")
        subtask_1c_score += 7
    elif func_count >= 5:
        print(f"  ⚠ PARTIAL: Some functions ({func_count}) but may lack full 3D support")
        subtask_1c_score += 3
    else:
        print("  ✗ FAIL: Insufficient functions for 3D maze")
    print()
    
    print("Test 4.3: 3D Path Discovery (8 points)")
    path_3d = None
    path_3d_name = None
    
    for name, value in variables.items():
        if isinstance(value, (list, dict)):
            converted = convert_puffing_array_to_python(value)
            if isinstance(converted, list) and len(converted) > 0:
                valid_3d = True
                for item in converted[:min(5, len(converted))]:
                    if not (isinstance(item, list) and len(item) == 3):
                        valid_3d = False
                        break
                    if not (isinstance(item[0], int) and isinstance(item[1], int) and isinstance(item[2], int)):
                        valid_3d = False
                        break
                    # Check reasonable coordinate range
                    if not (1 <= item[0] <= 10 and 1 <= item[1] <= 10 and 1 <= item[2] <= 10):
                        valid_3d = False
                        break
                
                if valid_3d and len(converted) >= 3:
                    path_3d = converted
                    path_3d_name = name
                    print(f"  ✓ PASS: 3D path found with {len(converted)} steps (variable: {name})")
                    subtask_1c_score += 8
                    break
    
    if not path_3d:
        print("  ✗ FAIL: No 3D path found")
    print()
    
    print("Test 4.4: Multi-Floor Navigation (5 points)")
    if path_3d:
        floor_changes = 0
        for i in range(1, len(path_3d)):
            if path_3d[i][0] != path_3d[i-1][0]:
                floor_changes += 1
        
        if floor_changes > 0:
            print(f"  ✓ PASS: Path uses stairs ({floor_changes} floor changes)")
            subtask_1c_score += 5
        else:
            print("  ⚠ PARTIAL: 3D path exists but no floor changes")
            subtask_1c_score += 2
    else:
        print("  ✗ FAIL: Cannot verify floor navigation")
    print()
    
    total_score += subtask_1c_score
    print(f"PART 4 Score: {subtask_1c_score}/25")
    print()
    
    # ========== FINAL RESULTS ==========
    print("=" * 69)
    print(" FINAL RESULTS")
    print("=" * 69)
    print()
    print(f"Part 1 (MAIN TASK):        {main_score}/30")
    print(f"Part 2 (Shortest Path):    {subtask_1a_score}/20")
    print(f"Part 3 (Treasures):        {subtask_1b_score}/25")
    print(f"Part 4 (3D Maze):          {subtask_1c_score}/25")
    print("-" * 70)
    print(f"TOTAL SCORE: {total_score}/{max_score}")
    print()
    
    # Grade Letter
    if total_score >= 95:
        grade_letter, message = "A+", "🏆 PERFECT! Outstanding implementation!"
    elif total_score >= 90:
        grade_letter, message = "A", "🌟 EXCELLENT! Nearly flawless work!"
    elif total_score >= 85:
        grade_letter, message = "A-", "⭐ VERY GOOD! Strong performance!"
    elif total_score >= 80:
        grade_letter, message = "B+", "✅ GOOD! Solid implementation!"
    elif total_score >= 75:
        grade_letter, message = "B", "👍 ABOVE AVERAGE! Keep going!"
    elif total_score >= 70:
        grade_letter, message = "B-", "✓ SATISFACTORY! Room for improvement"
    elif total_score >= 65:
        grade_letter, message = "C+", "⚠ ACCEPTABLE! Review key concepts"
    elif total_score >= 60:
        grade_letter, message = "C", "⚠ PASSING! Significant work needed"
    else:
        grade_letter, message = "F", "❌ NEEDS WORK! Review backtracking algorithms"
    
    print(f"Grade: {grade_letter}")
    print()
    print(message)
    print("=" * 69)
    
    return {
        'score': total_score,
        'max_score': max_score,
        'passed': total_score >= 60,
        'grade_letter': grade_letter
    }


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: python grader_mission1.py <filepath.pf>")
            sys.exit(1)
        
        filepath = sys.argv[1]
        
        print(f"\n🔍 Grading Mission 1: Pathfinding & Backtracking\n")
        
        execution_result = run_student_code(filepath)
        grade_result = grade_mission_1(execution_result)
        
        sys.exit(0 if grade_result['passed'] else 1)
    
    except Exception as e:
        print(f"\n❌ GRADER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
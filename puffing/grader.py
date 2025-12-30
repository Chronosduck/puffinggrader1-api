#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Grader Dispatcher
Routes grading requests to specific mission graders

Usage: python grader.py <mission_id> <filepath.pf>
Example: python grader.py 1 uploads/mission1.pf
"""

import sys
import os
import io
import importlib.util

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
grader_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, grader_dir)


def load_mission_grader(mission_id):
    """
    Dynamically load the grader module for a specific mission
    
    Args:
        mission_id: Mission number (1-7)
        
    Returns:
        The grader module or None if not found
    """
    grader_file = os.path.join(grader_dir, f'grader_mission{mission_id}.py')
    
    if not os.path.exists(grader_file):
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(f"grader_mission{mission_id}", grader_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading grader for mission {mission_id}: {e}")
        return None


def main():
    """Main entry point"""
    
    # Check arguments
    if len(sys.argv) < 3:
        print("Usage: python grader.py <mission_id> <filepath.pf>")
        print()
        print("Examples:")
        print("  python grader.py 1 uploads/mission1.pf")
        print("  python grader.py 2 uploads/mission2.pf")
        sys.exit(1)
    
    try:
        mission_id = int(sys.argv[1])
        filepath = sys.argv[2]
    except ValueError:
        print("Error: Mission ID must be a number")
        sys.exit(1)
    
    # Validate mission ID
    if mission_id < 1 or mission_id > 7:
        print(f"Error: Invalid mission ID {mission_id}. Must be between 1 and 7.")
        sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Load the appropriate grader
    print(f"🔍 Loading grader for Mission {mission_id}...")
    grader_module = load_mission_grader(mission_id)
    
    if grader_module is None:
        print(f"❌ Error: Grader for mission {mission_id} not found")
        print(f"Expected file: grader_mission{mission_id}.py")
        sys.exit(1)
    
    # Run the student code
    try:
        print(f"📝 Executing student code: {filepath}")
        print()
        
        execution_result = grader_module.run_student_code(filepath)
        
        # Grade the result
        grade_function_name = f'grade_mission_{mission_id}'
        if hasattr(grader_module, grade_function_name):
            grade_function = getattr(grader_module, grade_function_name)
            grade_result = grade_function(execution_result)
            
            # Exit with appropriate code
            sys.exit(0 if grade_result['passed'] else 1)
        else:
            print(f"❌ Error: Grade function '{grade_function_name}' not found in grader module")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ GRADER ERROR: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
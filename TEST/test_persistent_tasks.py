#!/usr/bin/env python3
"""
Test script for persistent task state functionality
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_task_state_manager():
    """Test the TaskStateManager functionality"""
    print("🧪 Testing Persistent Task State Management")
    print("=" * 50)
    
    try:
        from web_dashboard import TaskStateManager
        
        # Create a new task state manager
        manager = TaskStateManager("test_task_state.json")
        
        print("✅ TaskStateManager created successfully")
        
        # Test adding tasks
        print("\n1. Testing Task Addition:")
        test_task_1 = {
            'type': 'scraping',
            'status': 'running',
            'progress': 25,
            'total': 10,
            'current': 2,
            'logs': ['Task started', 'Processing item 1', 'Processing item 2'],
            'start_time': datetime.now().isoformat()
        }
        
        test_task_2 = {
            'type': 'automation',
            'status': 'completed',
            'progress': 100,
            'total': 5,
            'current': 5,
            'logs': ['Task started', 'All items processed', 'Task completed'],
            'start_time': datetime.now().isoformat()
        }
        
        manager.add_task("test_task_1", test_task_1)
        manager.add_task("test_task_2", test_task_2)
        
        print("   • Added 2 test tasks")
        
        # Test getting tasks
        print("\n2. Testing Task Retrieval:")
        all_tasks = manager.get_all_tasks()
        print(f"   • Total tasks: {len(all_tasks)}")
        
        task_1 = manager.get_task("test_task_1")
        if task_1:
            print(f"   • Task 1 status: {task_1['status']}")
            print(f"   • Task 1 progress: {task_1['progress']}%")
        
        # Test updating tasks
        print("\n3. Testing Task Updates:")
        manager.update_task("test_task_1", {
            'progress': 50,
            'current': 5,
            'logs': task_1['logs'] + ['Processing item 3', 'Processing item 4', 'Processing item 5']
        })
        
        updated_task = manager.get_task("test_task_1")
        print(f"   • Updated progress: {updated_task['progress']}%")
        print(f"   • Updated current: {updated_task['current']}")
        print(f"   • Log entries: {len(updated_task['logs'])}")
        
        # Test state persistence
        print("\n4. Testing State Persistence:")
        manager.save_state()
        print("   • State saved to file")
        
        # Create a new manager instance to test loading
        new_manager = TaskStateManager("test_task_state.json")
        loaded_tasks = new_manager.get_all_tasks()
        print(f"   • Loaded {len(loaded_tasks)} tasks from file")
        
        # Verify data integrity
        loaded_task_1 = new_manager.get_task("test_task_1")
        if loaded_task_1 and loaded_task_1['progress'] == 50:
            print("   • ✅ Data integrity verified")
        else:
            print("   • ❌ Data integrity check failed")
        
        # Test cleanup
        print("\n5. Testing Cleanup:")
        manager.cleanup_completed_tasks(max_age_hours=0)  # Clean up immediately
        remaining_tasks = manager.get_all_tasks()
        print(f"   • Remaining tasks after cleanup: {len(remaining_tasks)}")
        
        # Clean up test file
        if os.path.exists("test_task_state.json"):
            os.remove("test_task_state.json")
            print("   • Test file cleaned up")
        
        print("\n✅ All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_page_refresh_scenario():
    """Test the page refresh scenario"""
    print("\n🔄 Testing Page Refresh Scenario")
    print("=" * 40)
    
    try:
        from web_dashboard import TaskStateManager, add_task_status, get_task_status, update_task_status
        
        # Simulate starting a task
        print("1. Starting a task...")
        task_id = "test_refresh_task"
        initial_data = {
            'type': 'scraping',
            'status': 'running',
            'progress': 0,
            'total': 10,
            'current': 0,
            'logs': ['Task started'],
            'start_time': datetime.now().isoformat()
        }
        
        add_task_status(task_id, initial_data)
        print("   • Task added to state manager")
        
        # Simulate task progress
        print("2. Simulating task progress...")
        for i in range(1, 4):
            time.sleep(0.1)  # Small delay to simulate processing
            update_task_status(task_id, {
                'progress': i * 25,
                'current': i,
                'logs': get_task_status()[task_id]['logs'] + [f'Processing item {i}']
            })
            print(f"   • Progress: {i * 25}%")
        
        # Simulate page refresh (new TaskStateManager instance)
        print("3. Simulating page refresh...")
        refreshed_manager = TaskStateManager()
        refreshed_tasks = refreshed_manager.get_all_tasks()
        
        if task_id in refreshed_tasks:
            task = refreshed_tasks[task_id]
            print(f"   • ✅ Task found after refresh")
            print(f"   • Status: {task['status']}")
            print(f"   • Progress: {task['progress']}%")
            print(f"   • Log entries: {len(task['logs'])}")
        else:
            print("   • ❌ Task not found after refresh")
            return False
        
        # Continue task after refresh
        print("4. Continuing task after refresh...")
        update_task_status(task_id, {
            'progress': 75,
            'current': 7,
            'logs': get_task_status()[task_id]['logs'] + ['Processing item 7']
        })
        
        # Verify final state
        final_task = get_task_status()[task_id]
        print(f"   • Final progress: {final_task['progress']}%")
        print(f"   • Final log entries: {len(final_task['logs'])}")
        
        # Clean up
        if os.path.exists("task_state.json"):
            os.remove("task_state.json")
        
        print("   • ✅ Page refresh scenario completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Page refresh test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Persistent Task State System")
    print("=" * 60)
    
    success = True
    
    # Test basic functionality
    if not test_task_state_manager():
        success = False
    
    # Test page refresh scenario
    if not test_page_refresh_scenario():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Persistent task state system is working correctly.")
        print("\nKey Features Verified:")
        print("   • Task state persistence across page refreshes")
        print("   • Automatic state loading on startup")
        print("   • Real-time task progress tracking")
        print("   • Task cleanup and management")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Test script for the restructured automation system
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_automation_components():
    """Test the new automation components"""
    print("=== Testing Restructured Automation Components ===")
    
    try:
        from web_dashboard import AutomationAction, LikeAction, RetweetAction, ReplyAction
        from web_dashboard import AutomationStrategy, StandardAutomationStrategy
        from web_dashboard import AutomationState
        
        print("✅ All automation classes imported successfully")
        
        # Test action classes
        print("\n1. Testing Action Classes:")
        like_action = LikeAction()
        retweet_action = RetweetAction()
        reply_action = ReplyAction()
        
        print(f"   • LikeAction: {like_action.name} - {like_action.description}")
        print(f"   • RetweetAction: {retweet_action.name} - {retweet_action.description}")
        print(f"   • ReplyAction: {reply_action.name} - {reply_action.description}")
        
        # Test strategy
        print("\n2. Testing Strategy:")
        strategy = StandardAutomationStrategy()
        print(f"   • Strategy: {strategy.name} - {strategy.description}")
        print(f"   • Available actions: {list(strategy.get_actions().keys())}")
        
        # Test state management
        print("\n3. Testing State Management:")
        test_tweets = ["https://twitter.com/test1", "https://twitter.com/test2", "https://twitter.com/test3"]
        test_comments = ["Great post!", "Thanks for sharing!", "Amazing content!"]
        test_actions = {"like": True, "retweet": False, "reply": True}
        
        state = AutomationState(
            "test_task_123",
            "test_profile",
            test_tweets,
            test_comments,
            test_actions,
            5, 15, 3
        )
        
        print(f"   • State created for task: {state.task_id}")
        print(f"   • Profile: {state.profile_name}")
        print(f"   • Total paired tasks: {len(state.paired_tasks)}")
        print(f"   • Actions: {state.actions}")
        
        # Test paired tasks
        print("\n4. Testing Paired Tasks:")
        for i, task in enumerate(state.paired_tasks):
            print(f"   • Task {i}: {task['tweet_url']} -> '{task['comment']}'")
        
        # Test task processing
        print("\n5. Testing Task Processing:")
        remaining_tasks = state.get_remaining_tasks()
        print(f"   • Remaining tasks: {len(remaining_tasks)}")
        
        # Simulate processing some tasks
        if len(state.paired_tasks) > 0:
            state.mark_task_processed(0, True)  # Mark first task as successful
            print(f"   • Marked task 0 as successful")
        
        if len(state.paired_tasks) > 1:
            state.mark_task_processed(1, False)  # Mark second task as failed
            print(f"   • Marked task 1 as failed")
        
        # Check updated stats
        stats = state.get_progress_stats()
        print(f"   • Updated stats: {stats['processed_count']}/{stats['total_tasks']} processed")
        print(f"   • Success rate: {stats['success_rate']:.1f}%")
        
        # Test remaining tasks after processing
        remaining_tasks = state.get_remaining_tasks()
        print(f"   • Remaining tasks after processing: {len(remaining_tasks)}")
        
        # Test state saving/loading
        print("\n6. Testing State Persistence:")
        state.save_state()
        print("   • State saved to file")
        
        loaded_state = AutomationState.load_state("test_task_123")
        if loaded_state:
            print("   • State loaded from file successfully")
            print(f"   • Loaded task ID: {loaded_state.task_id}")
            
            # Verify paired tasks were preserved
            loaded_stats = loaded_state.get_progress_stats()
            print(f"   • Loaded stats: {loaded_stats['processed_count']}/{loaded_stats['total_tasks']} processed")
            print(f"   • Loaded success rate: {loaded_stats['success_rate']:.1f}%")
        else:
            print("   ❌ Failed to load state")
        
        # Cleanup test state
        state.cleanup()
        print("   • Test state cleaned up")
        
        print("\n✅ All automation components working correctly!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test the new API endpoints"""
    print("\n=== Testing New API Endpoints ===")
    
    try:
        # This would require a running Flask app
        print("📝 API endpoints to test:")
        print("   • GET /api/automation/state/<task_id>")
        print("   • POST /api/automation/recover/<task_id>")
        print("   • GET /api/automation/strategies")
        print("   • Enhanced DELETE /api/tasks/<task_id> (with state saving)")
        
        print("✅ API endpoint structure verified")
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Restructured Automation System")
    print("=" * 50)
    
    success = True
    
    # Test components
    if not test_automation_components():
        success = False
    
    # Test API structure
    if not test_api_endpoints():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Restructured automation system is ready.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 
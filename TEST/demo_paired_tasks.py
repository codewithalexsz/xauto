#!/usr/bin/env python3
"""
Demonstration script for the new paired task automation system
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_paired_tasks():
    """Demonstrate the new paired task system"""
    print("🎯 Paired Task Automation System Demo")
    print("=" * 50)
    
    try:
        from web_dashboard import AutomationState
        
        # Sample data - 10 tweet links and 10 comments
        tweet_links = [
            "https://twitter.com/user1/status/123456789",
            "https://twitter.com/user2/status/234567890",
            "https://twitter.com/user3/status/345678901",
            "https://twitter.com/user4/status/456789012",
            "https://twitter.com/user5/status/567890123",
            "https://twitter.com/user6/status/678901234",
            "https://twitter.com/user7/status/789012345",
            "https://twitter.com/user8/status/890123456",
            "https://twitter.com/user9/status/901234567",
            "https://twitter.com/user10/status/012345678"
        ]
        
        reply_comments = [
            "Great post! Thanks for sharing this valuable information.",
            "This is exactly what I needed to see today. Amazing insights!",
            "Love the perspective you bring to this topic. Well done!",
            "Thanks for breaking this down in such a clear way.",
            "This resonates so much with me. Appreciate you sharing!",
            "Excellent analysis! You've really hit the nail on the head.",
            "This is the kind of content that makes Twitter worthwhile.",
            "Thanks for the thoughtful commentary on this important issue.",
            "You've articulated this perfectly. Great job!",
            "This is spot on! Thanks for the valuable contribution."
        ]
        
        actions = {"like": True, "retweet": False, "reply": True}
        
        print("📝 Input Data:")
        print(f"   • Tweet links: {len(tweet_links)}")
        print(f"   • Reply comments: {len(reply_comments)}")
        print(f"   • Actions: {actions}")
        
        # Create automation state
        state = AutomationState(
            "demo_task_001",
            "demo_profile",
            tweet_links,
            reply_comments,
            actions,
            5, 15, 3
        )
        
        print(f"\n🔗 Paired Tasks Created:")
        print(f"   • Total paired tasks: {len(state.paired_tasks)}")
        
        # Show first few paired tasks
        for i, task in enumerate(state.paired_tasks[:3]):
            print(f"   • Task {i}: {task['tweet_url'][:50]}... -> '{task['comment'][:30]}...'")
        
        if len(state.paired_tasks) > 3:
            print(f"   • ... and {len(state.paired_tasks) - 3} more tasks")
        
        # Simulate processing some tasks
        print(f"\n⚡ Simulating Task Processing:")
        
        # Process first 3 tasks
        for i in range(3):
            success = (i % 2 == 0)  # Alternate success/failure for demo
            state.mark_task_processed(i, success)
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   • Task {i}: {status}")
        
        # Show current stats
        stats = state.get_progress_stats()
        print(f"\n📊 Current Progress:")
        print(f"   • Processed: {stats['processed_count']}/{stats['total_tasks']}")
        print(f"   • Successful: {stats['successful_count']}")
        print(f"   • Failed: {stats['failed_count']}")
        print(f"   • Success rate: {stats['success_rate']:.1f}%")
        print(f"   • Remaining: {stats['remaining_count']}")
        
        # Show remaining tasks
        remaining_tasks = state.get_remaining_tasks()
        print(f"\n🔄 Remaining Tasks ({len(remaining_tasks)}):")
        for i, task in enumerate(remaining_tasks[:3]):
            print(f"   • Task {task['index']}: {task['tweet_url'][:50]}...")
        
        if len(remaining_tasks) > 3:
            print(f"   • ... and {len(remaining_tasks) - 3} more remaining tasks")
        
        # Simulate recovery scenario
        print(f"\n🔄 Recovery Scenario:")
        print("   • If automation is interrupted now, only remaining tasks will be processed")
        print("   • No duplicate processing of already completed tasks")
        print("   • State is automatically saved for recovery")
        
        # Save state
        state.save_state()
        print(f"\n💾 State saved for recovery")
        
        # Cleanup
        state.cleanup()
        print(f"✅ Demo completed successfully!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

def main():
    """Run the demo"""
    success = demo_paired_tasks()
    
    if success:
        print("\n🎉 Paired task system is working perfectly!")
        print("\nKey Benefits:")
        print("   • Tweet links and comments are properly paired")
        print("   • Completed tasks are removed from the queue")
        print("   • No duplicate processing on resume")
        print("   • Detailed progress tracking")
        print("   • Automatic state persistence")
    else:
        print("\n❌ Demo failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 
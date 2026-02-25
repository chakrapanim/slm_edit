"""
Monitoring script for JFLEG evaluation progress
Shows real-time progress, estimated time remaining, and current status
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta

def check_process_running():
    """Check if the evaluation process is still running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'python jfleg_evaluation.py'],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def get_process_info():
    """Get process information"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if 'python jfleg_evaluation.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 11:
                    return {
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'time': parts[9]
                    }
    except:
        pass
    return None

def load_checkpoint():
    """Load progress from checkpoint file"""
    checkpoint_file = 'jfleg_progress.json'
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def estimate_time_remaining(current_idx, total, start_time=None):
    """Estimate time remaining based on current progress"""
    if current_idx == 0:
        return "Calculating..."
    
    if start_time:
        elapsed = time.time() - start_time
        rate = current_idx / elapsed if elapsed > 0 else 0
        if rate > 0:
            remaining = (total - current_idx) / rate
            return str(timedelta(seconds=int(remaining)))
    
    return "Unknown"

def format_size(size_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def check_output_file():
    """Check if output Excel file exists and its size"""
    output_file = 'jfleg_evaluation_report.xlsx'
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        mtime = os.path.getmtime(output_file)
        return {
            'exists': True,
            'size': format_size(size),
            'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    return {'exists': False}

def monitor():
    """Main monitoring function"""
    print("=" * 80)
    print("JFLEG Evaluation Progress Monitor")
    print("=" * 80)
    print()
    
    # Check if process is running
    is_running = check_process_running()
    process_info = get_process_info()
    
    if is_running and process_info:
        print(f"✓ Process Status: RUNNING (PID: {process_info['pid']})")
        print(f"  CPU Usage: {process_info['cpu']}%")
        print(f"  Memory Usage: {process_info['mem']}%")
        print(f"  CPU Time: {process_info['time']}")
    elif is_running:
        print("✓ Process Status: RUNNING")
    else:
        print("✗ Process Status: NOT RUNNING")
        print("  (Evaluation may have completed or crashed)")
    
    print()
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    total_examples = 748  # JFLEG test set size
    
    if checkpoint:
        last_index = checkpoint.get('last_index', 0)
        results = checkpoint.get('results', [])
        completed = len(results)
        progress_pct = (completed / total_examples * 100) if total_examples > 0 else 0
        
        print("Progress Information:")
        print("-" * 80)
        print(f"  Completed Examples: {completed} / {total_examples}")
        print(f"  Progress: {progress_pct:.2f}%")
        print(f"  Last Processed Index: {last_index}")
        print()
        
        # Progress bar
        bar_width = 50
        filled = int(bar_width * progress_pct / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        print(f"  [{bar}] {progress_pct:.1f}%")
        print()
        
        # Calculate metrics if we have results
        if results and len(results) > 0:
            try:
                exact_matches = sum(1 for r in results if r.get('exact_match', False))
                exact_match_rate = (exact_matches / len(results) * 100) if results else 0
                
                print("Current Metrics (from completed examples):")
                print("-" * 80)
                print(f"  Exact Match Rate: {exact_match_rate:.2f}% ({exact_matches}/{len(results)})")
                
                if 'bleu_score' in results[0]:
                    avg_bleu = sum(r.get('bleu_score', 0) for r in results) / len(results)
                    print(f"  Average BLEU Score: {avg_bleu:.4f}")
                
                if 'rougeL' in results[0]:
                    avg_rouge = sum(r.get('rougeL', 0) for r in results) / len(results)
                    print(f"  Average ROUGE-L Score: {avg_rouge:.4f}")
                
                if 'normalized_edit_distance' in results[0]:
                    avg_edit = sum(r.get('normalized_edit_distance', 0) for r in results) / len(results)
                    print(f"  Average Normalized Edit Distance: {avg_edit:.4f}")
            except Exception as e:
                print(f"  Could not calculate metrics: {e}")
        
        print()
        
        # Time estimation
        if is_running:
            remaining = total_examples - completed
            if completed > 0:
                # Rough estimate: ~1-2 seconds per example
                avg_time_per_example = 1.5  # seconds
                estimated_seconds = remaining * avg_time_per_example
                estimated_time = str(timedelta(seconds=int(estimated_seconds)))
                print(f"Estimated Time Remaining: ~{estimated_time}")
                print(f"  (Based on average processing time)")
    else:
        print("Progress Information:")
        print("-" * 80)
        if is_running:
            print("  Waiting for first checkpoint...")
            print("  (Checkpoint is saved after 10 examples)")
        else:
            print("  No checkpoint file found.")
            print("  Evaluation may not have started or has completed.")
    
    print()
    
    # Check output file
    output_info = check_output_file()
    print("Output File Status:")
    print("-" * 80)
    if output_info['exists']:
        print(f"  ✓ jfleg_evaluation_report.xlsx exists")
        print(f"  Size: {output_info['size']}")
        print(f"  Last Modified: {output_info['modified']}")
        if not is_running:
            print()
            print("  🎉 Evaluation appears to be complete!")
    else:
        print("  ✗ jfleg_evaluation_report.xlsx not found yet")
        print("  (Will be created when evaluation completes)")
    
    print()
    print("=" * 80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def continuous_monitor(interval=30):
    """Continuously monitor progress at specified interval"""
    print("Starting continuous monitoring...")
    print(f"Update interval: {interval} seconds")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name != 'nt' else 'cls')
            
            monitor()
            
            # Check if process is done
            if not check_process_running():
                output_info = check_output_file()
                if output_info['exists']:
                    print()
                    print("🎉 Evaluation completed! Output file is ready.")
                    break
            
            print()
            print(f"Refreshing in {interval} seconds... (Ctrl+C to stop)")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print()
        print("Monitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        # Continuous monitoring mode
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        continuous_monitor(interval)
    else:
        # Single check mode
        monitor()
        print()
        print("Tip: Run with '--watch' for continuous monitoring:")
        print("  python monitor_jfleg.py --watch [interval_seconds]")
        print("  Example: python monitor_jfleg.py --watch 30")

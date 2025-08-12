"""
VNC checker utility for the Twitter automation app
"""

import os
import subprocess
from typing import Tuple, Optional

def check_vnc_running(display: str = ":1") -> Tuple[bool, Optional[str]]:
    """
    Check if VNC server is running on the specified display
    
    Args:
        display (str): VNC display number (e.g., ":1")
        
    Returns:
        Tuple[bool, Optional[str]]: (is_running, error_message)
    """
    if os.name != 'posix':
        return False, "VNC check only supported on Linux"
    
    try:
        # Method 1: Check using pgrep for various VNC server types
        vnc_patterns = [
            f'vncserver.*{display}',
            f'Xtightvnc.*{display}',
            f'tightvncserver.*{display}',
            f'tigervncserver.*{display}',
            f'x11vnc.*{display}'
        ]
        
        for pattern in vnc_patterns:
            try:
                result = subprocess.run(['pgrep', '-f', pattern], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return True, None
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
        
        # Method 2: Check using ps aux (fallback method)
        try:
            ps_output = subprocess.check_output(
                ["ps", "aux"],
                universal_newlines=True,
                timeout=5
            )
            
            # Look for common VNC server processes
            vnc_processes = [
                "tightvncserver",
                "Xtightvnc",
                "x11vnc",
                "vncserver",
                "tigervncserver"
            ]
            
            for line in ps_output.split('\n'):
                if any(proc in line.lower() for proc in vnc_processes) and display in line:
                    return True, None
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        # Method 3: Check if DISPLAY environment variable is set and X server is accessible
        if "DISPLAY" in os.environ and os.environ["DISPLAY"] == display:
            try:
                subprocess.check_call(
                    ["xdpyinfo"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                return True, None
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass
        
        return False, f"No VNC server found running on display {display}"
        
    except Exception as e:
        return False, f"Error checking VNC status: {str(e)}"

def check_vnc_running_simple(display: str = ":1") -> Tuple[bool, Optional[str]]:
    """
    Simple VNC check using pgrep (used by start_vnc function for consistency)
    
    Args:
        display (str): VNC display number (e.g., ":1")
        
    Returns:
        Tuple[bool, Optional[str]]: (is_running, error_message)
    """
    if os.name != 'posix':
        return False, "VNC check only supported on Linux"
    
    try:
        # Check for various VNC server types
        vnc_patterns = [
            f'vncserver.*{display}',
            f'Xtightvnc.*{display}',
            f'tightvncserver.*{display}',
            f'tigervncserver.*{display}',
            f'x11vnc.*{display}'
        ]
        
        for pattern in vnc_patterns:
            result = subprocess.run(['pgrep', '-f', pattern], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, None
        
        return False, f"No VNC server found running on display {display}"
    except subprocess.TimeoutExpired:
        return False, "VNC status check timed out"
    except Exception as e:
        return False, f"Error checking VNC status: {str(e)}"

def verify_vnc_environment(display: str = ":1") -> Tuple[bool, Optional[str]]:
    """
    Verify the VNC environment is properly set up
    
    Args:
        display (str): VNC display number (e.g., ":1")
        
    Returns:
        Tuple[bool, Optional[str]]: (is_ready, error_message)
    """
    if os.name != 'posix':
        return False, "VNC environment check only supported on Linux"
    
    try:
        # Check if XFCE is installed
        try:
            subprocess.check_call(
                ["which", "xfce4-session"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            return False, "XFCE desktop environment not found"
        
        # Check if VNC server is installed
        vnc_found = False
        for vnc_server in ["tightvncserver", "x11vnc", "vncserver", "tigervncserver"]:
            try:
                subprocess.check_call(
                    ["which", vnc_server],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                vnc_found = True
                break
            except subprocess.CalledProcessError:
                continue
        
        if not vnc_found:
            return False, "No VNC server found (tightvncserver, x11vnc, vncserver, or tigervncserver)"
        
        # Check if VNC is running using the simple method for consistency
        vnc_running, error = check_vnc_running_simple(display)
        if not vnc_running:
            return False, error
        
        return True, None
        
    except Exception as e:
        return False, f"Error verifying VNC environment: {str(e)}"

def get_vnc_status(display: str = ":1") -> dict:
    """
    Get comprehensive VNC status information
    
    Args:
        display (str): VNC display number (e.g., ":1")
        
    Returns:
        dict: Status information including running state, processes, and errors
    """
    status = {
        'running': False,
        'display': display,
        'processes': [],
        'errors': [],
        'environment_ready': False
    }
    
    if os.name != 'posix':
        status['errors'].append("VNC is only supported on Linux")
        return status
    
    # Check if VNC is running
    vnc_running, error = check_vnc_running_simple(display)
    status['running'] = vnc_running
    if error:
        status['errors'].append(error)
    
    # Get VNC processes if running
    if vnc_running:
        try:
            # Check for various VNC server types
            vnc_patterns = [
                f'vncserver.*{display}',
                f'Xtightvnc.*{display}',
                f'tightvncserver.*{display}',
                f'tigervncserver.*{display}',
                f'x11vnc.*{display}'
            ]
            
            for pattern in vnc_patterns:
                result = subprocess.run(['pgrep', '-f', pattern], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                ps_result = subprocess.run(['ps', '-p', pid, '-o', 'pid,ppid,cmd'], 
                                                         capture_output=True, text=True, timeout=5)
                                if ps_result.returncode == 0:
                                    status['processes'].append(ps_result.stdout.strip())
                            except Exception:
                                pass
                    break  # Found processes, no need to check other patterns
        except Exception as e:
            status['errors'].append(f"Error getting process info: {str(e)}")
    
    # Check environment
    env_ready, env_error = verify_vnc_environment(display)
    status['environment_ready'] = env_ready
    if env_error:
        status['errors'].append(env_error)
    
    return status

def cleanup_stale_vnc_processes(display: str = ":1") -> Tuple[bool, Optional[str]]:
    """
    Clean up any stale VNC processes that might be causing inconsistency
    
    Args:
        display (str): VNC display number (e.g., ":1")
        
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    if os.name != 'posix':
        return False, "VNC cleanup only supported on Linux"
    
    try:
        # Find VNC processes for the display
        vnc_patterns = [
            f'vncserver.*{display}',
            f'Xtightvnc.*{display}',
            f'tightvncserver.*{display}',
            f'tigervncserver.*{display}',
            f'x11vnc.*{display}'
        ]
        
        result = None
        for pattern in vnc_patterns:
            try:
                result = subprocess.run(['pgrep', '-f', pattern], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    break
            except Exception:
                continue
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            killed_count = 0
            
            for pid in pids:
                if pid.strip():
                    try:
                        # Kill the process
                        subprocess.run(['kill', '-9', pid.strip()], 
                                     capture_output=True, text=True, timeout=5)
                        killed_count += 1
                        print(f"Killed VNC process {pid}")
                    except Exception as e:
                        print(f"Failed to kill process {pid}: {e}")
            
            if killed_count > 0:
                return True, f"Cleaned up {killed_count} stale VNC processes"
            else:
                return True, "No stale VNC processes found"
        else:
            return True, "No VNC processes found to clean up"
            
    except subprocess.TimeoutExpired:
        return False, "VNC cleanup timed out"
    except Exception as e:
        return False, f"Error cleaning up VNC processes: {str(e)}"

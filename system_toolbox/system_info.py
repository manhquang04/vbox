import psutil

def get_disk_usage():
    """
    Returns a list of dictionaries containing disk usage information for each partition.
    """
    disk_info = []
    try:
        # Get all mounted disk partitions
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except PermissionError:
                # Skip partitions that we don't have access to
                continue
    except Exception as e:
        print(f"Error reading disk info: {e}")
    
    return disk_info

def get_ram_usage():
    """
    Returns a dictionary with RAM usage information.
    """
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "available": mem.available,
        "percent": mem.percent
    }

def get_process_list():
    """
    Returns a list of running processes with memory usage.
    """
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                # Get process info
                pinfo = proc.info
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "memory_percent": pinfo['memory_percent'] or 0.0,
                    "memory_rss": pinfo['memory_info'].rss if pinfo['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"Error getting process list: {e}")

    # Sort by memory usage (descending)
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return processes

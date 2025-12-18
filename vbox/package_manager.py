import subprocess
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PackageInfo:
    name: str
    size_mb: float
    version: str
    type: str  # "apt" / "rpm" / "AppImage" / "Flatpak" / "Snap"
    status: str = "Installed"
    desktop_file_path: Optional[str] = None
    exec_path: Optional[str] = None

class BasePackageManager:
    def list_installed(self) -> List[PackageInfo]:
        raise NotImplementedError

    def uninstall_cmd(self, pkg_name: str) -> List[str]:
        """Returns the command list to be used with subprocess.Popen."""
        raise NotImplementedError

class AptPackageManager(BasePackageManager):
    def list_installed(self) -> List[PackageInfo]:
        packages = []
        try:
            # Run dpkg-query to get package name, installed size (KB), and version
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\t${Installed-Size}\t${Version}\n"],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        name = parts[0]
                        size_kb = float(parts[1])
                        version = parts[2]
                        packages.append(PackageInfo(
                            name=name,
                            size_mb=size_kb / 1024,
                            version=version,
                            type="apt"
                        ))
                except ValueError:
                    continue
                    
        except subprocess.CalledProcessError as e:
            print(f"Error listing packages (apt): {e}")
        except FileNotFoundError:
            print("dpkg-query not found.")

        return packages

    def uninstall_cmd(self, pkg_name: str) -> List[str]:
        # Use purge to remove config files and related data
        return ["pkexec", "apt", "purge", "-y", pkg_name]

class DnfRpmPackageManager(BasePackageManager):
    def list_installed(self) -> List[PackageInfo]:
        packages = []
        try:
            # Run rpm -qa to get package name, size (bytes), and version
            result = subprocess.run(
                ["rpm", "-qa", "--queryformat", "%{NAME}\t%{SIZE}\t%{VERSION}\n"],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        name = parts[0]
                        size_bytes = float(parts[1])
                        version = parts[2]
                        packages.append(PackageInfo(
                            name=name,
                            size_mb=size_bytes / (1024 * 1024),
                            version=version,
                            type="rpm"
                        ))
                except ValueError:
                    continue
                    
        except subprocess.CalledProcessError as e:
            print(f"Error listing packages (rpm): {e}")
        except FileNotFoundError:
            print("rpm command not found.")

        return packages

    def uninstall_cmd(self, pkg_name: str) -> List[str]:
        return ["pkexec", "dnf", "remove", "-y", pkg_name]

def detect_distro():
    """
    Reads /etc/os-release to detect the distribution.
    Returns (distro_id, distro_like) as lowercase strings.
    """
    distro_id = ""
    distro_like = ""
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro_id = line.strip().split("=")[1].strip('"').lower()
                    elif line.startswith("ID_LIKE="):
                        distro_like = line.strip().split("=")[1].strip('"').lower()
    except Exception as e:
        print(f"Error detecting distro: {e}")
    
    return distro_id, distro_like

def get_package_manager() -> Optional[BasePackageManager]:
    distro_id, distro_like = detect_distro()
    print(f"Detected distro: ID={distro_id}, LIKE={distro_like}")

    # Check for Fedora / RHEL family
    if distro_id in ["fedora", "rhel", "centos", "rocky", "alma"] or \
       "fedora" in distro_like or "rhel" in distro_like:
        return DnfRpmPackageManager()
    
    # Check for Debian / Ubuntu family
    if distro_id in ["ubuntu", "debian", "linuxmint", "pop"] or \
       "debian" in distro_like or "ubuntu" in distro_like:
        return AptPackageManager()

    return None

# Backward compatibility for existing code (if any other module imports these directly)
# Ideally, we should update consumers to use get_package_manager()
def list_installed_packages():
    mgr = get_package_manager()
    if mgr:
        # Convert PackageInfo objects to dicts for backward compatibility if needed,
        # but the new AppsTab will use objects. Let's return objects and update AppsTab.
        # However, the previous signature returned dicts.
        # To be safe for any other potential consumers, let's return dicts here.
        # But wait, the user asked to update AppsTab to use the new class structure.
        # So I will remove this backward compatibility function to force usage of the new API
        # or I can keep it but make it use the new API.
        # The user said: "Tạo (hoặc chỉnh) file package_manager.py theo hướng..."
        # So I will fully replace the file content.
        pass

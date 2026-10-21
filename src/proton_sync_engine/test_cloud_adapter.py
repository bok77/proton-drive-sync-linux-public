"""Read-only pairing adapter: isolated test folder, account-independent."""
import json
from .cli_adapter import execute
from pathlib import Path
from .portable_paths import load_paths

class TestCloudAdapter:
    def __init__(self, config_path):
        self.config=load_paths(Path(config_path))
        if self.config.local_root.is_relative_to(Path("/mnt/example-drive")):
            raise PermissionError("Production sync roots are excluded")
        # An existing Proton account/CLI may be used for read-only inspection.
        # Exact allowlist: the only cloud inventory root is the synthetic test
        # folder. Never inspect other folders, even when configured.
        if tuple(self.config.managed_folders)!=("ProtonSync-Test",):
            raise PermissionError("Only the dedicated ProtonSync-Test cloud folder is allowed")
        if self.config.local_root.is_relative_to(Path.home()/".local/share"):
            raise PermissionError("Application state directories are excluded")

    @staticmethod
    def remote_digest(meta):
        return ((meta.get("activeRevision") or {}).get("claimedDigests") or {}).get("sha1")

    @staticmethod
    def meta_rev(meta):
        return (meta.get("activeRevision") or {}).get("uid")

    def scan(self):
        entries={}
        folders={""}
        errors=[]
        def walk(parts):
            result=execute(str(self.config.cli_executable),"filesystem","list",
                           "/my-files/"+"/".join(parts),"-j",timeout=45)
            if result.returncode:
                raise RuntimeError("CLI_"+(result.error_class.value if result.error_class else "UNKNOWN"))
            data=json.loads(result.stdout)
            if not isinstance(data,list):raise ValueError("Invalid cloud inventory")
            for item in data:
                if not isinstance(item,dict):raise ValueError("Invalid cloud record")
                title=item.get("name") or {}
                name=title.get("value") if title.get("ok") else None
                if (not isinstance(name,str) or not name or name in (".","..")
                    or any(ch in name for ch in ("/","\\","\x00"))):
                    raise ValueError("Unsupported cloud name")
                child=parts+[name]
                rel="/".join(child)
                if item.get("type")=="folder":
                    folders.add(rel)
                    walk(child)
                elif item.get("type")=="file":
                    if rel in entries:raise ValueError("Duplicate cloud entry")
                    entries[rel]=item
                else:raise ValueError("Unknown cloud entry type")
        try:
            for name in self.config.managed_folders:
                folders.add(name)
                walk([name])
        except (OSError,ValueError,RuntimeError,TimeoutError) as exc:
            errors.append({"path":"cloud_inventory","reason":str(exc)[:160]})
        return entries,folders,errors

def inspect(config_path):
    from .installer_pairing import review_pairing
    return review_pairing(Path(config_path),TestCloudAdapter(config_path))

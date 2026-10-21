"""Stage a Fedora candidate alongside an intact previous installation.

Never replace active executables, switch desktop launchers or user systemd
units, or remove the older package. Promotion requires a separate approval.
"""
import argparse,json
from pathlib import Path
try:
    from .install_fedora_mvp import verify,install
except ImportError:
    from install_fedora_mvp import verify,install


def stage_update(previous, candidate, destination):
    """Verify the old bundle and install a new immutable sibling only."""
    old=verify(previous)
    new=Path(destination).expanduser().absolute()
    if new.parent!=old.parent or new==old:
        raise ValueError('New version must be a distinct sibling of the old install')
    result=install(candidate,new)
    verify(old)
    verify(new)
    return {'status':'STAGED_NOT_ACTIVATED','previous':str(old),
            'candidate':str(new),'launcher_unchanged':True,
            'previous_preserved':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--previous',type=Path,required=True)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(stage_update(args.previous,args.bundle,args.destination),indent=2))

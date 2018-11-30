from pathlib import Path as PathClass
from functools import partial
import argparse
# pathlib helpers

__all__ = ['Path', 'EDir', 'EPath', 'NEPath', 'AutoDir']

def Path(s=None, exists=None, dir=None, prefix=None, **kargs ):
    if s is None:
        return partial(Path, exists=exists, dir=dir, prefix=prefix, **kargs)

    p = PathClass(s)
    if prefix is not None:
        p = PathClass(prefix) / p

    if exists is not None and exists != p.exists():
        raise argparse.ArgumentTypeError("%s %sexists."%(p, "does not " if exists else "") )
    if dir is not None and dir != p.is_dir():
        raise argparse.ArgumentTypeError("%s is%s a exsited directory."%(p, " not" if dir else "") )
    return p

EDir = partial(Path, dir=True)
EPath = partial(Path, exists=True)
NEPath = partial(Path, exists=False)

def AutoDir(s=None, prefix=None):
    if s is None:
        return partial(AutoDir, prefix=prefix)
    path = Path(s, prefix=prefix)
    if path.exists() and not path.is_dir():
        raise argparse.ArgumentError("%s existed and is not a directory."%s)
    if not path.exists():
        # recursive create the path
        for p in reversed( path.parents ):
            if not p.exists():
                p.mkdir()
    return path

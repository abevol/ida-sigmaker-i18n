import sys
import os


_loader_dir = os.path.dirname(os.path.abspath(__file__))
if _loader_dir not in sys.path:
    sys.path.insert(0, _loader_dir)


def PLUGIN_ENTRY():
    from sigmaker import SigMakerPlugin

    return SigMakerPlugin()

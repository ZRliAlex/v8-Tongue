# Ultralytics YOLO 🚀, AGPL-3.0 license

__version__ = "8.2.28"

import os

# Set ENV Variables (place before imports)
os.environ["OMP_NUM_THREADS"] = "1"  # reduce CPU utilization during training

from .data.explorer.explorer import Explorer
from .models import NAS, RTDETR, SAM, YL, FastSAM, YOLOWorld
from .utils import ASSETS, SETTINGS
from .utils.checks import check_yolo as checks
from .utils.downloads import download

settings = SETTINGS
__all__ = (
    "__version__",
    "ASSETS",
    "YL",
    "YOLOWorld",
    "NAS",
    "SAM",
    "FastSAM",
    "RTDETR",
    "checks",
    "download",
    "settings",
    "Explorer",
)

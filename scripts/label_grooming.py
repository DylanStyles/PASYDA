"""
label_grooming.py - PASYDA grooming labelling script

Labelling script PASYDA datasets.
Labels each conversation as:
- yes > grooming detected
- no > grooming not detected

Uses behvaioural metadata to generate labels.
"""

import pandas as pd
from pathlib import Path

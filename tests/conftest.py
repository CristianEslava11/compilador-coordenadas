import os
import sys

# Los módulos del compilador se importan como en Docker (desde src/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

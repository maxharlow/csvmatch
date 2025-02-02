import sys

try:
    from .cli import main as main
except KeyboardInterrupt:
    sys.exit(1)

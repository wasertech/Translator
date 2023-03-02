import sys
from translator.main import main

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(1)
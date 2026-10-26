"""Entry point of the program (also used by PyInstaller)."""
import multiprocessing

from magma_uplift.app import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

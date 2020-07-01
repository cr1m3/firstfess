from .fess import AutoFess
from .plugins import listeners

if __name__ == "__main__":
    AutoFess().start()
    listeners.Listeners().main()

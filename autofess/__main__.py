from autofess import fess, plugins

listeners = plugins.listeners.Listeners()
autofess = fess.AutoFess()
if __name__ == "__main__":
    autofess.start()
    listeners.main()

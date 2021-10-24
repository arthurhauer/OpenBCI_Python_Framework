import time
from application import Application

if __name__ == "__main__":
    app = Application()
    app.start()
    time.sleep(60)
    app.stop()

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import sideqr  # This ensures QRScanner is registered for QML

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Load QML file
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

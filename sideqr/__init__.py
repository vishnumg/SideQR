from .qr_scanner import QRScanner
from PySide6.QtQml import qmlRegisterType

# Register the QRScanner for QML
qmlRegisterType(QRScanner, "SideQR", 1, 0, "QRScanner")

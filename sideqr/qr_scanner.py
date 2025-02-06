from PySide6.QtCore import QObject, Signal, Property, QThread, QMutex, QDateTime, QAbstractListModel, Qt, QModelIndex
from PySide6.QtMultimedia import QVideoSink, QVideoFrame
from PySide6.QtGui import QImage
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import cv2


class BarcodeResult(QObject):
    def __init__(self, data_bytes, bbox, timestamp, parent=None):
        super().__init__(parent)
        self._data_bytes = data_bytes
        self._data = data_bytes.decode()
        self._bbox = bbox
        self._timestamp = timestamp

    @Property(bytes)
    def data_bytes(self):
        return self._data_bytes

    @Property(str)
    def data(self):
        return self._data

    @Property(tuple)
    def bbox(self):
        return self._bbox

    @bbox.setter
    def bbox(self, value):
        self._bbox = value

    @Property(float)
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value


class QRThread(QThread):
    decoded = Signal(object)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._active = True
        self._pending_frame = None

    def run(self):
        while self._active:
            self._mutex.lock()
            frame = self._pending_frame
            self._pending_frame = None
            self._mutex.unlock()

            if frame is not None and frame.size > 0:
                decoded = decode(frame, symbols=[ZBarSymbol.QRCODE])
                self.decoded.emit(decoded)

    def add_frame(self, frame):
        self._mutex.lock()
        self._pending_frame = frame
        self._mutex.unlock()

    def stop(self):
        self._active = False
        self.wait()


class BarcodeListModel(QAbstractListModel):
    DataRole = Qt.UserRole + 1
    BboxRole = Qt.UserRole + 2
    TimestampRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._barcodes = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._barcodes)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._barcodes):
            return None
        barcode = self._barcodes[index.row()]
        if role == self.DataRole:
            return barcode.data
        elif role == self.BboxRole:
            return barcode.bbox
        elif role == self.TimestampRole:
            return barcode.timestamp
        return None

    def roleNames(self):
        return {
            self.DataRole: b"data",
            self.BboxRole: b"bbox",
            self.TimestampRole: b"timestamp"
        }

    def updateBarcodes(self, barcodes):
        self.beginResetModel()
        self._barcodes = barcodes.copy()
        self.endResetModel()


class QRScanner(QObject):
    barcodesDetected = Signal(list) # Signal that emits a list of BarcodeResult objects

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_sink = QVideoSink(self)
        self._processed_sink = None
        self._video_sink.videoFrameChanged.connect(self._handle_frame)
        self._qr_thread = QRThread()
        self._qr_thread.decoded.connect(self._handle_results)
        self._qr_thread.start()
        self._highlight = True
        self._displayed_codes = []  # List of BarcodeResult objects
        self._debounce_period = 1000  # Default debounce period in milliseconds
        self._visible_barcodes_model = BarcodeListModel(self)

    @Property(QObject, constant=True)
    def videoSink(self):
        return self._video_sink

    @Property(QObject)
    def previewOutput(self):
        return self._processed_sink

    @previewOutput.setter
    def previewOutput(self, sink):
        self._processed_sink = sink

    @Property(bool)
    def highlightDetected(self):
        return self._highlight

    @highlightDetected.setter
    def highlightDetected(self, value):
        self._highlight = value

    @Property(int)
    def debouncePeriod(self):
        return self._debounce_period

    @debouncePeriod.setter
    def debouncePeriod(self, value):
        if value > 0:
            self._debounce_period = value

    @Property(QObject, constant=True)
    def visibleBarcodesModel(self):
        return self._visible_barcodes_model
    def _handle_frame(self, frame):
        if not frame.isValid():
            return

        try:
            image = frame.toImage()
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
            buffer = image.bits().tobytes()
            np_image = np.frombuffer(buffer, dtype=np.uint8).reshape((image.height(), image.width(), 4))
            opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGBA2BGRA)

            # Highlight detected QR codes
            if self._highlight and self._displayed_codes:
                overlay = opencv_image.copy()  # Create a copy for the overlay
                current_time = QDateTime.currentDateTime().toMSecsSinceEpoch()
                for code in self._displayed_codes:
                    elapsed_time = current_time - code.timestamp
                    if elapsed_time > self._debounce_period:
                        continue  # Skip codes that have expired

                    alpha = (self._debounce_period - elapsed_time) / self._debounce_period  # Alpha as a fraction (0 to 1)
                    left, top, width, height = code.bbox

                    # Draw the rectangle on the overlay
                    cv2.rectangle(
                        overlay,
                        (left, top),
                        (left + width, top + height),
                        (0, 255, 0),  # Green color (no alpha here)
                        5  # Filled rectangle
                    )

                    # Blend the overlay with the original image using the alpha value
                    cv2.addWeighted(overlay, alpha, opencv_image, 1 - alpha, 0, opencv_image)

            opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2RGBA)
            qimage = QImage(opencv_image.data, opencv_image.shape[1], opencv_image.shape[0], QImage.Format_RGBA8888)
            processed_frame = QVideoFrame(qimage)

            if self._processed_sink:
                self._processed_sink.setVideoFrame(processed_frame)

            self._qr_thread.add_frame(opencv_image)

        except Exception as e:
            print(f"Frame error: {e}")

    def _handle_results(self, decoded_objects):
        current_time = QDateTime.currentDateTime().toMSecsSinceEpoch()
        new_codes = []

        # Update displayed codes and add new ones
        for obj in decoded_objects:
            bbox = (obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height)
            data_bytes = obj.data
            existing_code = next((code for code in self._displayed_codes if code.data_bytes == data_bytes), None)

            if existing_code:
                # Update timestamp and bounding box for existing code
                existing_code.timestamp = current_time
                existing_code.bbox = bbox
            else:
                # Add new code
                new_code = BarcodeResult(data_bytes, bbox, current_time)
                self._displayed_codes.append(new_code)
                new_codes.append(new_code)

        # Remove expired codes
        self._displayed_codes = [
            code for code in self._displayed_codes
            if current_time - code.timestamp <= self._debounce_period
        ]

        self._visible_barcodes_model.updateBarcodes(self._displayed_codes)

        # Emit signal for new barcodes
        if new_codes:
            self.barcodesDetected.emit(new_codes)

    def __del__(self):
        self._qr_thread.stop()
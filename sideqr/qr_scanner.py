from PySide6.QtCore import QObject, Signal, Property, QThread, QMutex
from PySide6.QtMultimedia import QVideoSink, QVideoFrame
from PySide6.QtGui import QImage
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import cv2


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


class QRScanner(QObject):
    barcodeDetected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_sink = QVideoSink(self)
        self._processed_sink = None
        self._video_sink.videoFrameChanged.connect(self._handle_frame)
        self._qr_thread = QRThread()
        self._qr_thread.decoded.connect(self._handle_results)
        self._qr_thread.start()
        self._highlight = True
        self._last_decoded_objects = []
        self._emptyframes = 0

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
    
    def _handle_frame(self, frame):
        if not frame.isValid():
            return

        try:
            image = frame.toImage()
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
            buffer = image.bits().tobytes()
            np_image = np.frombuffer(buffer, dtype=np.uint8).reshape((image.height(), image.width(), 4))
            opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGBA2BGRA)

            if self._highlight and self._last_decoded_objects:
                overlay = opencv_image.copy()
                for obj in self._last_decoded_objects:
                    rect = obj.rect
                    alpha = int(255 * (1 - (min(max(self._emptyframes, 0), 15) / 15)))
                    cv2.rectangle(
                        overlay,
                        (rect.left, rect.top),
                        (rect.left + rect.width, rect.top + rect.height),
                        (128, 100, 100, alpha),
                        5
                    )
                cv2.addWeighted(overlay, alpha / 255.0, opencv_image, 1 - alpha / 255.0, 0, opencv_image)

            opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2RGBA)
            qimage = QImage(opencv_image.data, opencv_image.shape[1], opencv_image.shape[0], QImage.Format_RGBA8888)
            processed_frame = QVideoFrame(qimage)

            if self._processed_sink:
                self._processed_sink.setVideoFrame(processed_frame)

            self._qr_thread.add_frame(opencv_image)

        except Exception as e:
            print(f"Frame error: {e}")

    def _handle_results(self, decoded_objects):
        if decoded_objects:
            new_data = set([obj.data for obj in decoded_objects]) - set([obj.data for obj in self._last_decoded_objects])
            for data in new_data:
                barcode_data = data.decode()
                self.barcodeDetected.emit(barcode_data)
            self._last_decoded_objects = decoded_objects
            self._emptyframes = 0
        else:
            self._emptyframes += 1
            if self._emptyframes > 15:
                self._last_decoded_objects = []

    def __del__(self):
        self._qr_thread.stop()

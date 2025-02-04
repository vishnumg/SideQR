# SideQR

**SideQR** is a PySide6-based library that provides a custom QML component for real-time QR code scanning. It leverages OpenCV and PyZbar for efficient QR code detection and can be seamlessly integrated into PySide6 applications using QML.

---

## Features

- Real-time QR code detection using the device camera.
- Customizable QML component (`QRScanner`) for easy integration.
- Optional highlight overlays for detected QR codes.
- Lightweight and fast, using multithreading for frame processing.

---

## Installation

You can install **SideQR** via `pip`:

```bash
pip install sideqr
```

Or install directly from the GitHub repository:

```bash
pip install git+https://github.com/vishnumg/SideQR.git
```

---

## Usage

### **1. Importing the Library in QML**

Once installed, you can import the `QRScanner` component into your QML application:

```qml
import QtQuick
import QtQuick.Controls
import QtMultimedia
import SideQR 1.0

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: "QR Code Scanner"

    MediaDevices {
        id: mediaDevices
    }

    CaptureSession {
        camera: Camera {
            id: camera
            cameraDevice: mediaDevices.defaultVideoInput
            active: true
        }
        videoOutput: qrScanner.videoSink
    }

    QRScanner {
        id: qrScanner
        onBarcodeDetected: barcode => {
            console.log("QR Code detected:", barcode)
        }
        previewOutput: videoOutput.videoSink
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
    }
}
```

### **2. Running the Example**

You can also test the library with the provided example:

```bash
python examples/qr_scanner_app.py
```

This will open a window showing the camera feed, and detected QR codes will be displayed in the console and UI.

---

## API

### **QRScanner Properties:**

- **`videoSink`**: Connects the camera input to the `QRScanner` component.
- **`previewOutput`**: Outputs the processed video frames (with or without highlights) to a `VideoOutput`.

### **QRScanner Signals:**

- **`barcodeDetected`**: Emits the decoded QR code data as a string whenever a QR code is detected.

---

## Dependencies

- [PySide6](https://pypi.org/project/PySide6/)
- [OpenCV](https://pypi.org/project/opencv-python/)
- [PyZbar](https://pypi.org/project/pyzbar/)
- [Pillow](https://pypi.org/project/Pillow/)
- [NumPy](https://pypi.org/project/numpy/)

Install them manually if needed:

```bash
pip install PySide6 opencv-python pyzbar Pillow numpy
```

---

## Contributing

Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

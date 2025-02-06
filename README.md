# SideQR

**SideQR** is a PySide6-based library that provides a custom QML component for real-time QR code scanning. It leverages OpenCV and PyZbar for efficient QR code detection and can be seamlessly integrated into PySide6 applications using QML.

---

## Features

- Real-time QR code detection using the device camera
- Multiple barcode detection with timestamp tracking
- Customizable QML component (`QRScanner`) for easy integration
- Real-time highlight overlays for detected QR codes
- Visible barcodes model for tracking currently detected codes
- Detection history logging
- Adjustable debounce period for code persistence
- Lightweight and fast, using multithreading for frame processing

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

### 1. Basic Implementation

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

    MediaDevices { id: mediaDevices }

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
        previewOutput: videoOutput.videoSink
        
        onBarcodesDetected: barcodes => {
            // Handle new detections
            barcodes.forEach(barcode => console.log("Detected:", barcode.data))
        }
    }

    VideoOutput {
        id: videoOutput
        height: parent.height / 2
    }

    Row {
        anchors.top: videoOutput.bottom
        spacing: 10

        // Visible Barcodes List
        Column {
            width: parent.width / 2
            Text {
                text: "Visible Barcodes"
                font.bold: true
            }
            ListView {
                width: parent.width
                height: 150
                model: qrScanner.visibleBarcodesModel
                delegate: Text {
                    text: model.data + " - " + new Date(model.timestamp).toLocaleTimeString()
                }
            }
        }

        // Detection History
        Column {
            width: parent.width / 2
            Text {
                text: "Detection Log"
                font.bold: true
            }
            ListView {
                width: parent.width
                height: 150
                model: ListModel { id: logsModel }
                delegate: Text {
                    text: model.data + " at " + model.timestamp
                }
            }
        }
    }
}
```

### 2. Advanced Features

#### Accessing Barcode Details

```qml
ListView {
    model: qrScanner.visibleBarcodesModel
    delegate: Column {
        Text { text: "Data: " + model.data }
        Text { text: "Bounding Box: " + model.bbox }
        Text { text: "Timestamp: " + new Date(model.timestamp).toLocaleTimeString() }
    }
}
```

#### Configuring Scanner Properties

```qml
QRScanner {
    id: qrScanner
    highlightDetected: true  // Enable/disable visual highlights
    debouncePeriod: 2000     // Set persistence time in milliseconds
}
```

---

## API

### QRScanner Properties

| Property           | Type    | Description                                      |
|-------------------|--------|--------------------------------------------------|
| `videoSink`       | QObject | Camera input connection (read-only)              |
| `previewOutput`   | QObject | Processed video output                           |
| `highlightDetected` | bool   | Enable/disable detection highlights              |
| `debouncePeriod`  | int     | Barcode persistence time in milliseconds        |
| `visibleBarcodesModel` | QObject | List model of currently visible barcodes |

### QRScanner Signals

#### `barcodesDetected(list<BarcodeResult>)`

Emits when new barcodes are detected, containing:

- **data**: Decoded text content
- **bbox**: Bounding box coordinates (left, top, width, height)
- **timestamp**: Detection timestamp

---

## Dependencies

- **PySide6**
- **OpenCV**
- **PyZbar**
- **NumPy**

Install all dependencies with:

```bash
pip install PySide6 opencv-python pyzbar numpy
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.


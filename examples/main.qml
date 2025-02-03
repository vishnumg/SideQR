import QtQuick
import QtQuick.Controls
import QtMultimedia
import SideQR 1.0

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: "QR Code Scanner Example"

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
            barcodeText.text = "QR Code: " + barcode
        }
        previewOutput: videoOutput.videoSink
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
    }

    Rectangle {
        width: parent.width
        height: 40
        color: "black"
        anchors.bottom: parent.bottom

        Text {
            id: barcodeText
            anchors.centerIn: parent
            color: "white"
            text: "Waiting for QR Code..."
        }
    }
}

import QtQuick
import QtQuick.Controls
import QtMultimedia
import SideQR 1.0

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: "QR Code Scanner"
    id: appWindow

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
            // Add to logs
            for (let i = 0; i < barcodes.length; i++) {
                logsModel.append({
                    "data": barcodes[i].data,
                    "timestamp": new Date(barcodes[i].timestamp).toLocaleTimeString()
                })
            }
        }
    }

    VideoOutput {
        id: videoOutput
        height: parent.height/2
    }

    Row {
        anchors.top: videoOutput.bottom
        spacing: 10

        Column {
            Text { 
                text: "Visible Barcodes:" 
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            ListView {
                width: appWindow.width/2
                height: 150
                model: qrScanner.visibleBarcodesModel
                delegate: Row {
                    spacing: 10
                    Text { text: "Data: " + model.data }
                    Text { text: "BBox: " + model.bbox }
                    Text { text: "Time: " + new Date(model.timestamp).toLocaleTimeString() }
                }
            }
        }
        Column{
            Text { 
                text: "Detection Log:" 
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            ListView {
                width: appWindow.width/2
                height: 150
                model: ListModel { id: logsModel }
                delegate: Row {
                    spacing: 10
                    Text { text: "Detected:" }
                    Text { text: model.data }
                    Text { text: "at " + model.timestamp }
                }
            }
        }
    }
}
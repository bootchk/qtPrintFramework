import QtQuick 2.3
import QtQuick.Dialogs 1.2
import QtQuick.Controls 1.1

import "../dialogContents" as MyDialogContents
import PageSetupDelegate 1.0	// Registered by business side


// Editor of PageSetup

Dialog {
	modality: Qt.ApplicationModal
	
	property var delegate: PageSetupDelegate {
			id: pageSetupDelegate
			objectName: "pageSetupDelegate"
		}
	
	// Usually hidden unless call open()
	// visible: true
	
	title: "Page Setup"
	standardButtons: StandardButton.Ok | StandardButton.Cancel

	MyDialogContents.StyleDialogContents{}
	
	onAccepted: {
		console.log("Accepted")
		dialogDelegate.accept()
	}
	 
	onRejected: {
		console.log("Rejected")
		dialogDelegate.reject()
	}
}
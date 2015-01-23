import QtQuick 2.3
import QtQuick.Dialogs 1.2

import "../controls" as MyControls
import "../domains" as MyDomains


// Editor of PageSetup
// A componenent of DelegatedPageSetup

Dialog {
	modality: Qt.ApplicationModal
	
	// Specialized at instantiation with a delegate
	property var delegate
	
	// Usually hidden unless call open()
	// visible: true
	
	title: "Page Setup"
	standardButtons: StandardButton.Ok
	// | StandardButton.Cancel

	//MyDialogContents()
	Column {
		MyControls.LabeledComboBox {
			text: "Orientation"
			// bind model to delegate
			model: delegate.orientation
			domain: MyDomains.Orientation{}
		}
	}

	onAccepted: {
		console.log("Accepted")
		delegate.accept()
	}
	 
	onRejected: {
		console.log("Rejected")
		delegate.reject()
	}
	
	Component.onCompleted: {
		console.log("delegate.orientation", delegate.orientation)
		print("Completed PageSetup QML")
	}
}
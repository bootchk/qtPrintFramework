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
			text: "Paper"
			// bind model to field of delegate
			model: delegate.paper
			domain: MyDomains.Paper{}
		}
		
		MyControls.LabeledComboBox {
			text: "Orientation"
			// bind model to field of delegate
			model: delegate.orientation
			domain: MyDomains.Orientation{}
		}
	}
	//Text { text: "Foo" }

	onAccepted: {
		console.log("Accepted")
		delegate.accept()
	}
	 
	onRejected: {
		console.log("Rejected")
		delegate.reject()
	}
	
	Component.onCompleted: {
		print("Completed PageSetup QML")
		console.assert(typeof delegate != 'undefined', "delegate is undefined")
		console.log("delegate.orientation", delegate.orientation.orientationEnum)
		
	}
}
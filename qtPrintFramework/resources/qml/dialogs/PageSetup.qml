import QtQuick 2.3
import QtQuick.Dialogs 1.2
//import QtQuick.Controls 1.1



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
	//console.log("Here")
	/*
	 Column {
		Text {
			text: "foo"
		}
	}
	* 
	 */
	
	
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
	}
}
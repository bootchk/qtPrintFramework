/*
QML for PageSetup editor.

This is outer shell with delegate and connections.
*/

import QtQuick 2.3

//import PrinteredPageLayout 1.0
import PageLayout 1.0
import "../dialogs" as MyDialogs

Item {
	id: pageSetupWindow
	
	// Specialized at instantiation with title that includes printer name
	property string titlePrefix
	
	// Delegate allowing Python side to open this dialog
	//PrinteredPageLayout {
	PageLayout {
		id: pageSetupDelegate
		objectName: "pageSetupDelegate"
	}
	
	MyDialogs.PageSetup {
		id: pageSetupDialog
		title: "PageSetup"
		delegate: pageSetupDelegate
	}
	
	Connections {
		target: pageSetupDelegate
		onOpenView: {
			// console.log("Dialog activated from PyQt business side")
			pageSetupDialog.open()
			console.assert(pageSetupDialog.visible)
		}	
	}
	
	/*
	Component.onCompleted: {
		print(x, y, width, height)
		print("Item completed")
		console.assert(typeof pageSetupDelegate != 'undefined', "pageSetupDelegate is undefined")
	}
	*/
}
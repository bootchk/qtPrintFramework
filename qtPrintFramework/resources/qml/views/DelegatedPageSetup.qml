/*
QML for PageSetup editor.

This is outer shell with delegate and connections.
*/

import QtQuick 2.3

import PageLayout 1.0
import "../dialogs" as MyDialogs

Item {
	id: pageSetupWindow
	
	// Specialized at instantiation with title that includes printer name
	property string titlePrefix
	
	// Delegate allowing Python side to open this dialog
	PageLayout {
		id: pageSetupDelegate
		objectName: "pageSetupDelegate"
	}
	
	MyDialogs.PageSetup {
		id: pageSetupDialog
		title: "PageSetup"
		delegate: pageSetupDelegate
		
		Component.onCompleted: {
			print(x, y, width, height)
			// console.assert(typeof stylesheetModel != 'undefined', "stylesheetModel is undefined")
		}
	}
	
	Connections {
	    target: pageSetupDelegate
	    onActivated: {
	    	console.log("Dialog activated from PyQt business side")
	    	pageSetupDialog.open()
	    	console.log("After dialog activated")
	    	console.assert(pageSetupDialog.visible)
	    }	
	}
}
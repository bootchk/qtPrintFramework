import QtQuick 2.3
import QtQuick.Controls 1.2

// Derived from documentStyle...ResettableComboBox.qml

Row {
	spacing: 10
	
	// Specialized at instantiation
	property string text
	property QtObject model	// controlled model on business side
	property var domain	// combobox's sub model
	
	Label {
		text: parent.text
	}
	
	ComboBox{
		model: parent.domain
		
		// TODO since model is a ListModel, convert from parent.model.value to ListModel.index to currentIndex
		// Binding
		currentIndex: parent.model.value
		         
		onActivated: {
			/*
			 * Similar to currentIndexChanged, but only with user input.
			 * onCurrentIndexChanged comes on initialization without user input.
			 * Also, this has a formal parameter "index" which is not same as currentIndex
			 */
			console.debug("CombBox.onActivated", index)
			// Note index is actual parameter of signal, not same as currentIndex
			// OLD, for continguous enums: parent.model.value = index
			// New use a list of [text,value] pairs i.e. ListModel of ListElements
			console.log("Combo box domain value:", model.get(index).value)
			console.log("parent.model.value before setting", parent.model.value)
			// model <= view
			// model should be a notifiable property and emit a signal
			parent.model.value = model.get(index).value
			console.assert(parent.model.value == model.get(index).value)
			console.log("parent.model after setting", parent.model.value)
		}
		
		// For testing: connect to signal from model property
		/*
		Connections{
			target: parent.model.value
			onOrientationChanged: {
				console.log("parent model orientation changed")
				//combobox.find()
			}	
		}
		*/
	
		Component.onCompleted: {
			print("Completed Combobox")
			console.assert(typeof parent.model != 'undefined', "parent.model is undefined")
			console.log("typeof parent.model", typeof parent.model)
			console.log("parent.model.value", parent.model.value)
		}
	}
}
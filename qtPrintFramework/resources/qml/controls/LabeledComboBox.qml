import QtQuick 2.3
import QtQuick.Controls 1.2

// Derived from documentStyle...ResettableComboBox.qml

Row {
	spacing: 10
	
	// Specialized at instantion
	property string text
	property var model	// controlled model on business side
	property var domain	// combobox's sub model
	
	Label {
		text: parent.text
	}
	
	ComboBox{
		model: parent.domain
		
		// TODO since model is a ListModel, convert from parent.model.value to ListModel.index to currentIndex
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
			console.log(model.get(index).value)
			console.log(parent.model.value)
			// model <= view
			parent.model.value = model.get(index).value	
		}
	}
}
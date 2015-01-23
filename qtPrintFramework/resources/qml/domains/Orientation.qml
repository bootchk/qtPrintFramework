import QtQuick 2.3

/*
Domain model for paper orientation.

Future: will come from QWidget side so is translated.
*/
ListModel {
	id: orientationModel
	
	ListElement{
		text: "Portrait"
		value: 0
	}
	ListElement{
		text: "Landscape"
		value: 1
	}
}
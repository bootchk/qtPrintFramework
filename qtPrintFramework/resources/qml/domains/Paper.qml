import QtQuick 2.3

/*
Domain model for paper orientation.

Future: will come from QWidget side so is translated.
*/
ListModel {
	ListElement{
		text: "A4"
		value: 0
	}
	ListElement{
		text: "B5"
		value: 1
	}
	ListElement{
		text: "Letter"
		value: 2
	}
	ListElement{
			text: "Legal"
			value: 3
		}
}
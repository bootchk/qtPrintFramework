import QtQuick 2.3

/*
Domain model for paper orientation.

Future: will come from QWidget side so is translated.

Derived from QPageSize.

Incomplete
*/
ListModel {
	ListElement{ text: "A4" ;  value: 0 }
	ListElement{ text: "B5" ; value: 1 }
	
	ListElement{ text: "Letter" ; value: 2 }
	ListElement{ text: "Legal" ; value: 3 }
	ListElement{ text: "Executive" ;  value: 4 }
	
	ListElement{ text: "A0" ; value: 5 }
	ListElement{ text: "A1" ; value: 6 }
	ListElement{ text: "A2" ; value: 7 }
	ListElement{ text: "A3" ; value: 8 }
	ListElement{ text: "A5" ; value: 9 }
	ListElement{ text: "A6" ; value: 10 }
	ListElement{ text: "A7" ; value: 11 }
	ListElement{ text: "A8" ; value: 12 }
	ListElement{ text: "A9" ; value: 13 }
	
	ListElement{ text: "B0" ; value: 14 }
	ListElement{ text: "B1" ; value: 15}
	ListElement{ text: "B10" ; value: 16}
	ListElement{ text: "B2" ; value: 17 }
	ListElement{ text: "B3" ; value: 18 }
	ListElement{ text: "B4" ; value: 19 }
	ListElement{ text: "B6" ; value: 20 }
	ListElement{ text: "B7" ; value: 21 }
	ListElement{ text: "B8" ; value: 22 }
	ListElement{ text: "B9" ; value: 23 }
	
	ListElement{ text: "C5E" ; value: 24 }
	ListElement{ text: "Comm10E" ; value: 25 }
	ListElement{ text: "DLE" ; value: 26 }
	ListElement{ text: "Folio" ; value: 27 }
	ListElement{ text: "Ledger" ; value: 28 }
	ListElement{ text: "Tabloid" ; value: 29 }
	ListElement{ text: "Tabloid" ; value: 30 }
}
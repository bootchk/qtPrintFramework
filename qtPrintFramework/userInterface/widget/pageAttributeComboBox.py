'''
Copyright 2012 Lloyd Konneker

This is free software, covered by the GNU General Public License.
'''

from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox

from qtPrintFramework.pageLayout.model.adaptedModel import AdaptedModel


class PageAttributeComboBox(QComboBox):
  '''
  Control widget:
  - GUI behaviour of QComboBox
  - adapts QComboBox to have value(), setValue(), valueChanged() API
  - takes a model that is an enum
  
  QComboBox is too broad for our use: includes editing of text
  AND QComboBox is too narrow for our use: doesn't implement setValue().
  '''
  
  valueChanged = Signal()
  

  def __init__(self, model):
    assert isinstance(model, AdaptedModel)  
    
    QComboBox.__init__(self)
    self.model = model
    
    ### WAS (unsorted): self.addItems(list(model.values.keys()))
    self.addItems(model.keys())

    
    # connect adapted widget signal to adapter
    # !!! connecting to str type signal
    self.currentIndexChanged[str].connect(self.adaptValueChanged)
    
    self._alignSelf()
  

  '''
  Adaption augments inherited Widget with these methods.
  
  Inherited Widget uses int index.
  These are agnostic of type.
  '''
  def setValue(self, newValue):
    '''
    Set value to newValue OR if newValue is not in model, setValue to 0.
    
    !!! Note the setValue API requires emit valueChanged.
    Implemented below (not here) because setCurrentIndex()
    emits a signal which below we re emit as valueChanged.
    '''
    #print("setValue", newValue)
    assert isinstance(newValue, int)  # Weak.  Stronger is: instance of a particular enum type.
    index, _ = self._indexOfValue(newValue)
    # Regardless if found, set index
    self.setCurrentIndex( index )
    
  
  def value(self):
    #print("pageAttributeComboBox.value() returns", self.currentText())
    return self._adaptNewValue(self.currentText())
  
  
  def isValueInModel(self, value):
    _, wasFound = self._indexOfValue(value)
    return wasFound
  
    
  '''
  Adapt signal.
  '''
  @Slot(str)
  def adaptValueChanged(self, newValue):
    '''
    Receive signal currentIndexChanged[str], adapt to signal valueChanged.
    
    Dumb down: discard any passed newValue.
    '''
    #print "Combo box value changed", newValue
    self.valueChanged.emit() # adaptedValue)
    
  
  '''
  Convert to and from Widget text values to model values.
  '''
  
  def _adaptNewValue(self, newValue):
    '''
    Adapt Widget's string value to model value, i.e. enum value.
    '''
    # assert value is unicode. Use str() to decode
    convertedValue = self.model.values[str(newValue)] # 
    #print "Adapted ", newValue, "converted type", type(convertedValue)
    return convertedValue
  
    
  
  def _indexOfValue(self, searchValue):
    '''
    tuple (index of searchValue in model, True)
     or tuple (0, False)  if searchValue missing from model
    '''
    # searchValue is an enum value or None, and None can be a value in dictionary
    i = 0
    foundKey = False
    ## WAS (unsorted) for _, value in self.model.values.items():
    for _, value in self.model.items():
      #print searchValue, value
      # if searchValue is None and None is in dictionary, or searchValue == value
      if value is searchValue or value == searchValue:  # !!! is, not ==, to match None
        foundKey = True
        break
      i += 1
    
    #OLD assert foundKey, "Missing value: " + str(searchValue) + " in model" + str(self.model) # dict is complete on values
    if foundKey:
      result = i, True
    else:
      result = 0, False
    return result


  def _alignSelf(self):
    '''
    See web for much discussion.
     
    lineEdit must be editable to set alignment, but then can be made readOnly
     
    right alignment didn't seem to have desired effect on Linux May 2014.
    right alignment cut off right side of text under scroll bar on Win Vista May 2014 see QTBUG 33176
    
    Apple HIG guidelines don't seem to suggest an alignment.
    But since the widget is left aligned (in a form), might as well left align the items also?
    
    If aligning right, does this help:
    comboBox.view().setLayoutDirection(Qt.RightToLeft)
    '''
    direction = Qt.AlignLeft
    self._alignTextEdit(direction=direction)
    ##self.view().setLayoutDirection(Qt.RightToLeft)
    self._alignItems(direction)
  
  def _alignItems(self, direction):
    for i in range(0, self.count()):
      #print("Aligning item")
      self.setItemData(i, direction, Qt.TextAlignmentRole)
    
  def _alignTextEdit(self, direction):
    self.setEditable(True)
    self.lineEdit().setReadOnly(True)
    self.lineEdit().setAlignment(direction)
    

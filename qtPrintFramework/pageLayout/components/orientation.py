
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QPageLayout


class Orientation(QObject):
  '''
  Paper orientation.
  Wraps enumType=QPageLayout.Orientation
  
  Primarily for translation, name, and repr.
  
  Should be registered with QML if using QML.
  '''
  
  valueChanged = pyqtSignal(int) # !!! Parameter is the new value

  
  def __init__(self, initialValue=None):
    super().__init__()  # init QObject
    
    if initialValue is None:
      #print("Defaulting orientation to Portrait.")
      self._value = QPageLayout.Portrait
    else:
      assert initialValue == QPageLayout.Portrait or initialValue == QPageLayout.Landscape
      self._value = initialValue
      
      
  def __repr__(self):
    print("Orientation.__repr__", self.name)
    return self.name
  
  def __eq__(self, other):
    return self._value == other._value
  
  
  # value is a notifiable property (so QML can access)
  @pyqtProperty(int, notify=valueChanged)
  def value(self):
    return self._value
  
  @value.setter
  def value(self, newValue):
    assert isinstance(newValue, int)
    self._value = newValue
    print("emitting valueChanged")
    self.valueChanged.emit(newValue)
  
  
  
  '''
  Other properties
  '''
  @property
  def name(self):
    print("orientation enum:", self.value)
    if self.isPortrait:
        result = self.tr('Portrait')
    else:
        result = self.tr('Landscape')
    print("Orientation.name", result)
    return result
  
  @property
  def isPortrait(self):
    return self._value == QPageLayout.Portrait
  

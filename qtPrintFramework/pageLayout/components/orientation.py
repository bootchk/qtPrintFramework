
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QPageLayout



class Orientation(QObject):
  '''
  Paper orientation.
  Wraps enumType=QPageLayout.Orientation
  
  Primarily for translation, name, and repr.
  '''
  
  valueChanged = pyqtSignal() 

  
  def __init__(self, initialValue=None):
    super(Orientation, self).__init__()
    if initialValue is None:
      #print("Defaulting orientation to Portrait.")
      self._value = QPageLayout.Portrait
    else:
      assert initialValue == QPageLayout.Portrait or initialValue == QPageLayout.Landscape
      self._value = initialValue
  
  def __repr__(self):
    return self.name
  
  def __eq__(self, other):
    return self._value == other._value
  
  
  # value is a notifiable property (so QML can access)
  @pyqtProperty(int, notify=valueChanged)
  def value(self):
    return self._value
  
  @value.setter
  def value(self, newValue):
    self._value = newValue
    self.valueChanged.emit()
  
  
  
  '''
  Other properties
  '''
  @property
  def name(self):
      if self.isPortrait:
          return self.tr('Portrait')
      else:
          return self.tr('Landscape')
  
  @property
  def isPortrait(self):
    return self._value == QPageLayout.Portrait
  

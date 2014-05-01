'''
'''

from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPrinter



class Orientation(QObject):
  '''
  Paper orientation.
  Wraps enumType=QPrinter.Orientation
  
  Primarily for translation, name, and repr.
  '''
  
  
  def __init__(self, enumValue=None):
    super(Orientation, self).__init__()
    if enumValue is None:
      print("Defaulting orientation to Portrait.")
      self.value = QPrinter.Portrait
    else:
      assert enumValue == QPrinter.Portrait or enumValue == QPrinter.Landscape
      self.value = enumValue
  
  def __repr__(self):
    return self.name
  
  def __eq__(self, other):
    return self.value == other.value
  
  # value is also exported as property
  
  @property
  def name(self):
      if self.isPortrait:
          return self.tr('Portrait')
      else:
          return self.tr('Landscape')
  
  @property
  def isPortrait(self):
    return self.value == QPrinter.Portrait
  

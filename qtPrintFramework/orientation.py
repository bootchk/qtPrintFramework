
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPageLayout



class Orientation(QObject):
  '''
  Paper orientation.
  Wraps enumType=QPageLayout.Orientation
  
  Primarily for translation, name, and repr.
  '''
  
  
  def __init__(self, initialValue=None):
    super(Orientation, self).__init__()
    if initialValue is None:
      #print("Defaulting orientation to Portrait.")
      self.value = QPageLayout.Portrait
    else:
      assert initialValue == QPageLayout.Portrait or initialValue == QPageLayout.Landscape
      self.value = initialValue
  
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
    return self.value == QPageLayout.Portrait
  

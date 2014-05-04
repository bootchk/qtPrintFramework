
from PyQt5.QtCore import QObject

class Translations(QObject):
  '''
  Hold translated strings as attributes.
  Used where caller is not a QObject.
  '''
  
  def __init__(self):
    super(Translations, self).__init__()
    
    self.Size = self.tr("Size")
    self.Orientation = self.tr("Orientation")
    self.PageSetup = self.tr("Page Setup: ")
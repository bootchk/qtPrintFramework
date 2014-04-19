
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox


class Warn(QObject):
  
  '''
  Warning messages to user.
  
  Gathered here for ease of i18n.
  
  Note that most of the difficulty is with Custom paper, which are of little use for most users
  '''
  
  def __init__(self, parentWidget):
    super(Warn, self).__init__()
    # all warnings parented to same window
    self.parentWidget = parentWidget
  
  
  def pageSetupNotUsableOnCustomPaper(self):
    _ = QMessageBox.warning(self.parentWidget,
          "",  # title
          self.tr("Current paper is Custom.  Please setup another paper, or Cancel and setup a Custom page using Print."))  # text
  
  def pageTooSmall(self):
    _ = QMessageBox.warning(self.parentWidget,
          "",  # title
          self.tr("Printable page size is too small to print.  Please increase paper size or decrease margins."))  # text
    



from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout


class PageSetupForm(QFormLayout):
  '''
  A Form (widget) of attributes.
  Part of dialog widget for PageSetup.
  '''
  
  def __init__(self, pageSetup):
    
    super(PageSetupForm, self).__init__()
    
    # Emulate Mac style
    self.setRowWrapPolicy(QFormLayout.DontWrapRows)
    self.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
    self.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
    self.setLabelAlignment(Qt.AlignRight)
    
    # Contains many attribute controls
    for attribute in pageSetup:
      self.addPropertyToForm(attribute)
    
  
  def addPropertyToForm(self, attribute):
    print("adding property", attribute.label)
    self.addRow(attribute.label, attribute.control)
      
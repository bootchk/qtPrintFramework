

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout


class PageSetupForm(QFormLayout):
  '''
  A Form (widget) of attributes.
  Part of dialog widget for PageSetup.
  '''
  
  def __init__(self, controls):
    
    super(PageSetupForm, self).__init__()
    
    # Emulate Mac style
    self.setRowWrapPolicy(QFormLayout.DontWrapRows)
    self.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
    self.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
    self.setLabelAlignment(Qt.AlignRight)
    
    # Contains many controls
    self.addProperties(controls)
    
  
  def addProperties(self, controls):
    for control in controls:
      self._addPropertyToForm(control)
      
      
  def addPropertiesFromPageSetup(self, pageSetup):
    '''
    Not used.
    The page setup knows properties.
    '''
    for control in pageSetup:
      self._addPropertyToForm(control)
    
  
  def _addPropertyToForm(self, control):
    '''
    A property is a row containing a label widget and a subcontrol widget.
    '''
    print("adding property", control.label)
    self.addRow(control.label, control.control)
      
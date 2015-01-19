
from qtPrintFramework.userInterface.widget.pageAttributeComboBox import PageAttributeComboBox


class PageAttribute():
  '''
  Attribute of PageSetup
  
  Responsibilities:
  - standard property responsibilities: get/set value
  - editable
  '''
  
  def __init__(self, label, model):   #, printerAdaptorSetMethod):
    self.label = label
    self.model = model
    self.control = PageAttributeComboBox(model=model) # widget (view displaying model)
    
    
  
  '''
  Methods delegated to owned control.
  '''
  @property
  def value(self):
    '''
    Current value.
    Delegate to control, that is long lived.
    '''
    result = self.control.value()
    # assert result is a value in the model (an enum value.)
    return result

  def setValue(self, value):
    self.control.setValue(value)
    
  
  def isValueInModel(self, value):
    return self.control.isValueInModel(value)
  
  
  
  def default(self):
    return self.model.default()
    
  
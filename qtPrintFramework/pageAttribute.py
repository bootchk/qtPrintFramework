
from qtPrintFramework.userInterface.pageAttributeComboBox import PageAttributeComboBox


class PageAttribute():
  '''
  '''
  
  def __init__(self, label, model):   #, printerAdaptorSetMethod):
    self.label = label
    self.model = model
    self.control = PageAttributeComboBox(model=model) # widget (view displaying model)
    
    ## self.printerAdaptorSetMethod = printerAdaptorSetMethod
    
    
  @property
  def value(self):
    '''
    Current value.
    Delegate to control, that is long lived.
    '''
    result = self.control.value()
    # assert result is a value in the model (an enum value.)
    return result

  """
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Knows how to apply self to a PrinterAdaptor
    '''
  """
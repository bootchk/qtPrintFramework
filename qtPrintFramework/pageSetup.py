

from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.paperSize import PaperSizeModel # singleton
from qtPrintFramework.model.pageOrientation import PageOrientationModel # singleton


class PageSetup(list):
  '''
  Iterable container of attributes of a page.
  
  This defines the set of attributes, their labels and models.
  
  Responsibilities:
  - iterate PageAttributes (which know their labels, controls, models, and values (but values are view values.)
  - save/restore self to settings, so self persists with app, not with a printer TODO
  - apply/get self to/from PrinterAdaptor
  
  !!! Paper/Page are not interchangeable but refer to a similar concept.
  Paper connotes real thing, and Page an ideal concept.
  They are often both confusingly used for the ideal concept (regardless of whether real paper is involved.)
  '''
  
  def __init__(self):
    self.append(PageAttribute(label="Size", model=PaperSizeModel))
    self.append(PageAttribute(label="Orientation", model=PageOrientationModel)) # ('Portrait', 'Landscape')))


  def fromPrinterAdaptor(self):
    # TODO 
    raise NotImplementedError
  
  
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting.)
    
    Alternative design: illustrates general nature.
    for attribute in self:
      attribute.toPrinterAdaptor(printerAdaptor)
    '''
    printerAdaptor.setPaperSize(self[0].value)   # !!! PaperSize,  setPageSize() is Qt obsolete
    printerAdaptor.setOrientation(self[1].value)
    
  
  def dump(self):
    '''
    Dump control values.
    Note control values are from the view,
    and may not reflect what has been set toPrinterAdaptor (if dialog was canceled.)
    '''
    for attribute in self:
      print attribute.value
  
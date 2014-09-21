
from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QPageLayout

from qtPrintFramework.orientedSize import OrientedSize



class Printerable(object):
  '''
  Mixin class for PageSetup.
  Talks to (friend of) real printers.
  '''
  
  '''
  To/from printerAdaptor
  
  Alternative design: illustrates general nature.
    for attribute in self:
      attribute.toPrinterAdaptor(printerAdaptor)
  '''

  def fromPrinterAdaptor(self, printerAdaptor):
    '''
    Copy values from printerAdaptor into self.
    And update controls (which are not visible, and are in parallel with native dialog controls.)
    '''
    self.paper = printerAdaptor.paper() # new instance
    self.orientation = printerAdaptor.paperOrientation
    if self.paper.isCustom:
      # capture size chosen by user, say in native Print dialog
      integralOrientedSizeMM = OrientedSize.roundedSize(sizeF=printerAdaptor.paperSizeMM)
      self.paper.setSize(integralOrientedSizeMM = integralOrientedSizeMM, 
                         orientation=self.orientation)
    # else size of paper is standard.
    
    # editor and settings are not updated                    
    
    
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting.)
    
    1. !!! setPaperSize,  setPageSize() is Qt obsolete
    2. printerAdaptor wants oriented size
    
    !!! setPaperSize is overloaded.
    # TODO should this be orientedPaperSizeDevicePixels ?
    
    Qt docs for setPaperSize() say: "Sets the printer paper size to newPaperSize if that size is supported. 
    The result is undefined if newPaperSize is not supported."
    The same applies here; this may not have the intended effect.
    '''
    
    printerAdaptor.setOrientation(self.orientation.value)
    
    # Formerly we called _toPrinterAdaptorByIntegralMMSize() here
    
    '''
    Set paper by enum where possible.  Why do we need this is additon to the above?
    Because floating point errors in some versions of Qt, 
    setting paperSize by a QSizeF does not always have the intended effect on enum.
    '''
    if self.paper.isCustom :
      # Illegal to call setPaperSize(QPrinter.Custom)
      self._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    else:
      printerAdaptor.setPaperSize(self.paper.paperEnum)
    
    '''
    Strong assertion might not hold: Qt might be showing paper dimensions QSizeF(0,0) for Custom
    (Which is bad programming.  None or Null should represent unknown.)
    
    Or, despite trying to set QPrinter consistent, Qt bugs still don't meet strong assertion.
    '''
    if not self.isEqualPrinterAdaptor(printerAdaptor):
      '''
      Setting by enum (non-custom) has failed.  (Typically on OSX?)
      Fallback: attempt to set by size.
      '''
      self._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    
    """
    Tried this for OSX, but it did not succeed in getting native dialog to agree with self.
    So Qt versions < 5.3 have a bug that cannot be worked around by this framework.
    if not self.isEqualPrinterAdaptor(printerAdaptor):
      self._toPrinterAdaptorByFloatInchSize(printerAdaptor)
    """
      
    self.warnIfDisagreesWithPrinterAdaptor(printerAdaptor)
    # Ideally (if Qt was bug free) these assertions should hold
    #assert self.isStronglyEqualPrinterAdaptor(printerAdaptor)
    #assert self.isEqualPrinterAdaptor(printerAdaptor)
    
  
  def _toPrinterAdaptorByIntegralMMSize(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Take integral size, convert to float.
    '''
    # Even a Custom paper has a size, even if it is defaulted.
    newPaperSizeMM = QSizeF(self.paper.integralOrientedSizeMM(self.orientation))
    assert newPaperSizeMM.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    printerAdaptor.setPaperSize(newPaperSizeMM, QPageLayout.Millimeter)
    
    
  def _toPrinterAdaptorByFloatInchSize(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Floating inch size.
    '''
    # TODO oriented, other inch unit sizes
    if self.paper.paperEnum == QPageLayout.Legal:
      newPaperSizeInch = QSizeF(8.5, 14)
    elif self.paper.paperEnum == QPageLayout.Letter:
      newPaperSizeInch = QSizeF(8.5, 11)
    else:
      return
      
    assert newPaperSizeInch.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    #print("setPaperSize(Inch)", newPaperSizeInch)
    printerAdaptor.setPaperSize(newPaperSizeInch, QPageLayout.Inch)
    

  
  

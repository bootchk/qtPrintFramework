
from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QPageLayout # , QPageSize

from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.alertLog import alertLog

from qtPrintFramework.pageLayout.components.orientation import Orientation
from qtPrintFramework.pageLayout.components.paper.paper import Paper



class AdaptorFromPageLayoutToPrinterAdaptor():
  '''
  Adapt in both directions.
  
  WAS: a mixin class for PageLayout.
  NOW: instance owned by a converser
  
  !!! This does NOT drag in Qt's QPrintSupport module.
  It understands PrintAdaptor, but does not require any imports of same.
  
  Alternative design: illustrates general nature.
    for attribute in self:
      attribute.toPrinterAdaptor(printerAdaptor)
  '''

  def fromPrinterAdaptor(self, pageLayout, printerAdaptor):
    '''
    Copy values from printerAdaptor into pageLayout.
    And update controls (which are not visible, and are in parallel with native dialog controls.)
    '''
    " !!! just change value, don't replace paper instance because QML is bound to the instance. "
    print("Printer: ", printerAdaptor.description)  # ,"has paper:", printerAdaptor.paper())
    pageLayout.paper.value = printerAdaptor.paper().value # new instance
    pageLayout.orientation.value = printerAdaptor.orientation().value
    if pageLayout.paper.isCustom:
      # capture size chosen by user, say in native Print dialog
      integralOrientedSizeMM = OrientedSize.roundedSize(sizeF=printerAdaptor.paperSizeMM)
      pageLayout.paper.setSize(integralOrientedSizeMM = integralOrientedSizeMM, 
                         orientation=pageLayout.orientation)
    # else size of paper is standard.
    
    # editor and settings are not updated                    
    assert isinstance(pageLayout.paper, Paper)
    assert isinstance(pageLayout.orientation, Orientation)
    
    
  def toPrinterAdaptor(self, pageLayout, printerAdaptor):
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
    
    # !!! Requires Qt 5.3 setPageO instead of setOrientation
    #print(type(pageLayout.orientation.value))
    printerAdaptor.setPageOrientation(pageLayout.orientation.value)
    
    # Formerly we called _toPrinterAdaptorByIntegralMMSize() here
    
    '''
    Set paper by enum where possible.  Why do we need this is additon to the above?
    Because floating point errors in some versions of Qt, 
    setting paperSize by a QSizeF does not always have the intended effect on enum.
    '''
    ##WAS if pageLayout.paper.isCustom :
    if pageLayout.paperIsCustom() :
      # Illegal to call setPaperSize(QPrinter.Custom)
      pageLayout._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    else:
      printerAdaptor.setPaperSize(pageLayout.paper.value)
      ##WAS printerAdaptor.setPaperSize(pageLayout.paper)
    
    '''
    Strong assertion might not hold: Qt might be showing paper dimensions QSizeF(0,0) for Custom
    (Which is bad programming.  None or Null should represent unknown.)
    
    Or, despite trying to set QPrinter consistent, Qt bugs still don't meet strong assertion.
    '''
    if not self.isEqualPrinterAdaptor(pageLayout, printerAdaptor):
      '''
      Setting by enum (non-custom) has failed.  (Typically on OSX?)
      Fallback: attempt to set by size.
      '''
      pageLayout._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    
    """
    Tried this for OSX, but it did not succeed in getting native dialog to agree with pageLayout.
    So Qt versions < 5.3 have a bug that cannot be worked around by this framework.
    if not self.isEqualPrinterAdaptor(pageLayout, printerAdaptor):
      pageLayout._toPrinterAdaptorByFloatInchSize(printerAdaptor)
    """
      
    self.warnIfDisagreesWithPrinterAdaptor(pageLayout, printerAdaptor)
    # Ideally (if Qt was bug free) these assertions should hold
    #assert self.isStronglyEqualPrinterAdaptor(pageLayout, printerAdaptor)
    #assert self.isEqualPrinterAdaptor(pageLayout, printerAdaptor)
    
    
  def _toPrinterAdaptorByIntegralMMSize(self, pageLayout, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Take integral size, convert to float.
    '''
    # Even a Custom paper has a size, even if it is defaulted.
    newPaperSizeMM = QSizeF(pageLayout.paper.integralOrientedSizeMM(pageLayout.orientation))
    assert newPaperSizeMM.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    printerAdaptor.setPaperSize(newPaperSizeMM, QPageLayout.Millimeter)
    
    
  def _toPrinterAdaptorByFloatInchSize(self, pageLayout, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Floating inch size.
    '''
    # TODO oriented, other inch unit sizes
    if pageLayout.paper.value == QPageLayout.Legal:
      newPaperSizeInch = QSizeF(8.5, 14)
    elif pageLayout.paper.value == QPageLayout.Letter:
      newPaperSizeInch = QSizeF(8.5, 11)
    else:
      return
      
    assert newPaperSizeInch.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    #print("setPaperSize(Inch)", newPaperSizeInch)
    printerAdaptor.setPaperSize(newPaperSizeInch, QPageLayout.Inch)
    
    
    
  '''
  Support assertions about relations between pageLayout and printerAdaptor.
  '''

  def isEqualPrinterAdaptor(self, pageLayout, printerAdaptor):
    '''
    Weak comparison: computed printerAdaptor.paper() equal pageLayout.paper
    printerAdaptor.paperSize() might still not equal pageLayout.value
    '''
    result = pageLayout.paper.value == printerAdaptor.paper().value and pageLayout.orientation.value == printerAdaptor.orientation().value
    if not result:
      alertLog("pageSetup differs")
      self.dumpDisagreement(pageLayout, printerAdaptor)
    return result
  
  def isStronglyEqual(self, pageLayout, printerAdaptor):
    '''
    Strong comparison: enum, orientation, dimensions equal
    
    Comparison of dimensions is epsilon (one is integer, one is float.
    Comparison of dimensions is unoriented (usually, width < height, but not always, Tabloid/Ledger).
    '''
    # partialResult: enums and orientation
    # paperSize() is QPrinter.paperSize()
    partialResult = pageLayout.paper.value == printerAdaptor.paperSize() \
          and pageLayout.orientation.value == printerAdaptor.orientation().value
    
    # Compare sizes.  All Paper including Custom has a size.
    sizeResult = partialResult and pageLayout.paper.isOrientedSizeEpsilonEqual(pageLayout.orientation.value, printerAdaptor.paperSizeMM)
    
    result = partialResult and sizeResult
      
    if not result:
      alertLog('isStronglyEqualPrinterAdaptor returns False')
      self.dumpDisagreement(printerAdaptor)
      
    return result
  
  
  def warnIfDisagreesWithPrinterAdaptor(self, pageLayout, printerAdaptor):
    '''
    Despite best efforts, could not get printerAdaptor to match pageLayout.
    However, the platform native dialogs might be correct,
    so the situation might correct itself after user uses native dialogs.
    So only give a warning (and the user may see artifactual wrong page outline.)
    This situation mainly occurs on OSX.
    '''
    if not self.isEqualPrinterAdaptor(pageLayout, printerAdaptor):
      alertLog("PrinterAdaptor pageLayout disagrees.")
  
  
  def dumpDisagreement(self, printerAdaptor):
    '''
    For debugging, show disagreement.
    '''
    return
    """
    #print(self.paper.value, printerAdaptor.paperSize(), # our and Qt enums
            self.orientation, printerAdaptor.orientation(), # our and Qt orientation
            printerAdaptor.paperSizeMM ) # Qt paperSize(mm)
    if not self.paper.isCustom:
        #print (self.paper.integralOrientedSizeMM(self.orientation) )  # our size mm (not defined for Custom)
    """

  
  

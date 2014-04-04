

class AdaptedModel(object):
  '''
  ABC
  
  Mimics a PyQt5 enum: "values" attribute is a dictionary.
  But uses a pickleable type 
  (PyQt5 Qt enum not pickleable since enum values are class attributes.)
  
  Responsibility:
  - has attribute 'values' which is standard dictionary
  - know default value
  
  Design notes:
  - keys of model are untranslated (i18n) since they are like English language program literals.
  ??? TODO when do they get translated
  '''
  
  # Responsibility: have attribute 'values'
  def __init__(self):
    self._createValues()  # call subclass
    
    
  def _createValues(self):
    raise NotImplementedError # Deferred
  
  @classmethod
  def _getAdaptedDictionary(self, enumOwningClass, enumType):
    ''' 
    Dictionary keyed by name of enum values.
    i.e. dict[str]=int
    
    Enum values are ints.
    Enum names are class attributes in PyQt.
    An enum class is not defined in PyQt, only the type of the enum.
    
    So this extracts a dictionary from the dictionary (dir) of the owningClass
    '''
    
    '''
    assertion on repr of types?  Why not on the types?
    #print(enumOwningClass.__class__, str(type(enumType)) )
    '''
    assert str(enumOwningClass.__class__) == "<type 'PyQt5.QtCore.pyqtWrapperType'>" 
    assert str(type(enumType)) == "<type 'sip.enumtype'>"
    
    adaptedDictionary = {}
    for key, value in vars(enumOwningClass).items():  # Python2 iteritems():
      if isinstance(value, enumType):
        #print(key, value)
        adaptedDictionary[key] = value
    return adaptedDictionary
    
    
  def default(self):
    '''
    Default value from self.values dictionary.
    
    Base implementation is: assume value 0 is in the model.
    Subclasses may reimplement if Qt defines a default.
    
    Ducktyping: 0 is an int, not really an instance of enum.
    '''
    return 0
    # raise NotImplementedError, 'deferred'
    
    
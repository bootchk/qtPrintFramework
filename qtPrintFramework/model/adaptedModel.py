

from PyQt5.QtCore import QObject

class AdaptedModel(QObject):  # for i18n
  '''
  ABC
  
  Mimics a PySide/PyQt5(?) enum: where "values" is the name of the attribute, really a dictionary.
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
    super(AdaptedModel, self).__init__()
    self._createValues()  # call subclass
    
    
  def _createValues(self):
    raise NotImplementedError, 'Deferred'
  
  
  '''
  Assert class defining enum is a binary relation (one-to-one).
  Can extract dictionaries in both directions, they will be equal in size.
  '''
  
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
  
  @classmethod
  def _getAdaptedReverseDictionary(self, enumOwningClass, enumType):
    ''' 
    Dictionary keyed by enum values of names.
    
    See forward dictionary above.
    '''
    assert str(enumOwningClass.__class__) == "<type 'PyQt5.QtCore.pyqtWrapperType'>" 
    assert str(type(enumType)) == "<type 'sip.enumtype'>"
    
    adaptedDictionary = {}
    for key, value in vars(enumOwningClass).items():  # Python2 iteritems():
      if isinstance(value, enumType):
        #print(key, value)
        adaptedDictionary[value] = key
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
    
    
  def items(self):
    '''
    list of tuples (key, value)
    '''
    return self.values.items()
  
  
  def keys(self):
    '''
    list of keys
    '''
    result =[keyValue[0] for keyValue in self.items()]
    # print result, str(type(result))
    return result
    
    
    
class AdaptedSortedModel(AdaptedModel):
  '''
  Extra postcondition on items() : is sorted
  '''
  
  def items(self):
    '''
    list of tuples (key, value)
    '''
    return sorted(self.values.items())
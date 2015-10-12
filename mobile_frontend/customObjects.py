from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label

class imageButton(ButtonBehavior, AsyncImage): # for thumbnail buttons
    pass
    
class imageButtonLocal(ButtonBehavior, Image): # for local imageButtons (i.e: vote buttons)
    pass

class labelButton(ButtonBehavior, Label): # for label buttons
    pass

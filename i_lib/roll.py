import gi, os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
import math

class Roll(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.size = (190,190) #paint area sizeı
        self.set_size_request(*self.size)#paint area size atama
        self.cursor_size = (130,130)
        self.cursor_pos = (-self.cursor_size[0]/2,-self.cursor_size[1]/2-15)
        self.back_size = (170,170)
        self.back_pos = [0,0]
        self.connect("draw", self.draw_all)
        self.cursor_angle = 0
        self.queue_draw()

    def draw_all(self,widget,cr):
        img_path = os.path.expanduser("./assets/roll_c.png")
        self.cursor = GdkPixbuf.Pixbuf.new_from_file(img_path)#,self.image_size,self.image_size)
        img_path = os.path.expanduser("./assets/roll.png")
        self.back = GdkPixbuf.Pixbuf.new_from_file(img_path)
       
        
        Gdk.cairo_set_source_pixbuf(cr,self.back,*self.back_pos)
        cr.paint()
        cr.translate(self.size[0]/2, self.size[1]/2)
        cr.rotate(math.pi/180*self.cursor_angle)
        Gdk.cairo_set_source_pixbuf(cr,self.cursor,*self.cursor_pos)
        cr.paint()


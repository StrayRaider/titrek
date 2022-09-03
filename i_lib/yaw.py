import gi, os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
import math

class Yaw(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.size = (190,190) #paint area sizeı
        self.set_size_request(*self.size)#paint area size atama
        self.cursor_size = (78,78)
        self.back_size = (190,190)
        self.cursor_pos = ((self.back_size[0]-self.cursor_size[0])/2,(self.back_size[1]-self.cursor_size[1])/2)
        self.back_pos = [-self.back_size[0]/2,-self.back_size[0]/2+9]
        self.connect("draw", self.draw_all)
        self.back_angle = 0
        self.queue_draw()

    def draw_all(self,widget,cr):
        img_path = os.path.expanduser("./assets/yaw_c.png")
        self.cursor = GdkPixbuf.Pixbuf.new_from_file(img_path)#,self.image_size,self.image_size)
        img_path = os.path.expanduser("./assets/yaw.png")
        self.back = GdkPixbuf.Pixbuf.new_from_file(img_path)

        cr.translate(self.size[0]/2, self.size[1]/2)
        cr.rotate(math.pi/180*self.back_angle)
        Gdk.cairo_set_source_pixbuf(cr,self.back,*self.back_pos)
        cr.paint()

        cr.rotate(-(math.pi/180*self.back_angle))
        cr.translate(-self.size[0]/2,-self.size[1]/2)
        

        Gdk.cairo_set_source_pixbuf(cr,self.cursor,*self.cursor_pos)
        cr.paint()

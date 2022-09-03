import gi, os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
import math

class Battery(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.size = (190,190) #paint area sizeı
        self.set_size_request(*self.size)#paint area size atama
        self.cursor_size = (170,170)
        self.cursor_pos = (-self.cursor_size[0]/2,-self.cursor_size[1]/2)
        self.back_size = (170,170)
        self.back_pos = [0,0]
        self.connect("draw", self.draw_all)
        self.cursor_angle = 0
        self.text = "0"
        self.queue_draw()

    def draw_all(self,widget,cr):
        img_path = os.path.expanduser("./assets/cursor.png")
        self.cursor = GdkPixbuf.Pixbuf.new_from_file(img_path)#,self.image_size,self.image_size)
        img_path = os.path.expanduser("./assets/battery.png")
        self.back = GdkPixbuf.Pixbuf.new_from_file(img_path)
       
        
        Gdk.cairo_set_source_pixbuf(cr,self.back,*self.back_pos)
        cr.paint()

        cr.set_font_size(17)
        (x, y, width_1, height, dx, dy) = cr.text_extents("Pil :{}".format(self.text))
        cr.set_font_size(10)
        (x, y, width_2, height, dx, dy) = cr.text_extents("%")
        cr.set_source_rgb(0.1, 0.1, 0.1)
        free_x = (self.size[0]-(width_1+width_2))/2
        free_s = 5
        x_pos = free_x
        y_pos = 170
        cr.move_to(x_pos, y_pos)
        cr.set_font_size(17)
        cr.show_text("Pil :{}".format(self.text))
        cr.move_to(x_pos+width_1+free_s,y_pos)
        cr.set_font_size(10)
        cr.show_text("%")

        cr.translate(self.size[0]/2, self.size[1]/2-15)
        cr.rotate(math.pi/180*self.cursor_angle)
        Gdk.cairo_set_source_pixbuf(cr,self.cursor,*self.cursor_pos)
        cr.paint()

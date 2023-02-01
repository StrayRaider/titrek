import gi
import serial
gi.require_version('Gtk','3.0')
from pymavlink import mavutil
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf, GLib, Gio
from gi.repository import OsmGpsMap as osmgpsmap

from i_lib import window

import random, sys, random

# dialog window for protocol choosing
class DialogWin(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="IHA'ya hoşgeldiniz",transient_for=parent, flags=0)

        self.set_default_size(300,70)
        self.first_insert = True

        box = Gtk.VBox()
        t_box = Gtk.HBox()
        box.pack_start(t_box,0,0,5)

        t_box.pack_start(Gtk.Label("Protocol"),0,0,5)
        self.protocol_combo = Gtk.ComboBoxText()
        
        #all connection elements
        for pro in ["/dev/ttyUSB0","/dev/ttyACMx","udpin:localhost:14551"]:
            self.protocol_combo.append_text(pro)
        #an element for passing connection
        self.protocol_combo.append_text("pass")
        
        t_box.pack_start(self.protocol_combo,1,1,5)
        t_box = Gtk.HBox()
        box.pack_start(t_box,0,0,5)

        #connect button definition
        connect_btn = Gtk.Button()
        connect_btn.set_label("Bağlan")
        t_box.pack_start(connect_btn,1,1,5)
        connect_btn.connect("clicked",self.connect_func)
        area = self.get_content_area()
        area.add(box)
        self.show_all()

    def connect_func(self,widget):
        self.connection_text = self.protocol_combo.get_active_text()
        self.response(Gtk.ResponseType.OK)

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="titrek",
        flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE, **kwargs)
        GLib.set_application_name("Titrek")
        GLib.set_prgname('titrek')
        self.settings = GLib.KeyFile()

        self.win = False
        self.osm = osmgpsmap.Map()
        self.iha_img = GdkPixbuf.Pixbuf.new_from_file('./assets/yaw_c.png')
        self.zoom = 15
        self.lat = 0
        self.lon = 0
        self.airspeed = 0
        self.groundspeed = 0
        self.yaw = 0
        self.roll = 0
        self.pitch = 0
        self.battery_r = 0
        self.altitude = 0
        self.ground = 0

    def do_start_up(self):
        Gtk.Application.do_startup(self)

    def restart(self,error = None):
        if error != None:
            self.create_info_dialog("HATA","Bağlantı Sağlanamadı.\n{}!".format(str(error)))
        self.dialog_win.destroy()
        self.do_activate()

    def do_activate(self):
        if not self.win:
            self.dialog_win = DialogWin(None)
            respons = self.dialog_win.run()
            if respons == Gtk.ResponseType.DELETE_EVENT:
                sys.exit()
            elif respons == Gtk.ResponseType.OK:
                self.connection_text = self.dialog_win.protocol_combo.get_active_text()
                self.connection = None
                if self.connection_text == "/dev/ttyACMx":
                    count = 0
                    #baud=115200
                    try:
                        self.connection = mavutil.mavlink_connection("/dev/ttyACM0")
                    except:
                        count += 1
                        try:
                            self.connection = mavutil.mavlink_connection("/dev/ttyACM1")
                        except:
                            count += 1
                        if count == 2:
                            self.restart(self.connection_text)

                elif self.connection_text == "udpin:localhost:14551":
                    try:
                        self.connection = mavutil.mavlink_connection("udpin:localhost:14551")
                    except:
                        self.restart(self.connection_text)

                elif self.connection_text == "/dev/ttyUSB0":
                    try:
                        self.connection = mavutil.mavlink_connection("/dev/ttyUSB0")
                    except:
                        self.restart(self.connection_text)
                elif self.connection_text == "pass":
                    pass
                else:
                    self.restart("Lütfen Port Seçimi yapın")

                if self.connection != None:
                    print(self.connection)
                    is_connected = self.connection.wait_heartbeat(timeout = 10)
                    is_connected = True
                    print(is_connected)
                    if is_connected == None:
                        self.create_info_dialog("HATA","Bağlantı Sağlanamadı.\nUçak Bulunamadı!")
                        self.do_activate()
                    else :
                        self.dialog_win.destroy()
                        self.win = window.MainWindow(application=self)
                        self.win.show_all()
                        self.win.present()
                        self.give_all_messages()
                        #self.calibre()
                        self.set_ground()
                        #self.give_all_messages()
                        self.timer = GObject.timeout_add(1000/10, self.update_window)
                        #self.timer = GObject.timeout_add(1000/2, self.loop)
                else:
                    self.dialog_win.destroy()
                    self.win = window.MainWindow(application=self)
                    self.win.show_all()
                    self.win.present()
                    self.give_all_messages()
                    self.set_ground()
                    self.timer = GObject.timeout_add(1000/10, self.update_window)

            #self.win = FTerm(application=self)
            #self.win.connect("delete-event", self.write_ftrem_settings)
            #self.win.connect("destroy", Gtk.main_quit)
            #self.win.show_all()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        if not self.win:
            self.do_activate()

    def create_info_dialog(self,title,text):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()

    def take_message(self,msg_type = None, block = False):
        try:
            if msg_type != None:
                msg = self.connection.recv_match(type = msg_type, blocking=block)
            else:
                msg = self.connection.recv_match(blocking=block)
            return msg
        except:
            print("message did not taked")
            return None

    def loop(self):
        pass

    def give_all_messages(self):
        for i in self.connection.messages:
            print(i,"\n")
            print(self.connection.messages[i],"\n")

    def calibre(self):
        try:
            attitude = self.take_message("ATTITUDE",True)
        except:
            print("attıtude alınamadı")
        print("passed")
        try:
            attitude = self.take_message("TERRAIN_REPORT",True)
        except:
            print("attıtude alınamadı")

    def set_degree(self, angle):
        return angle*57.2957795

    def set_ground(self):
        try:
            self.ground = self.connection.messages["POSITION_TARGET_GLOBAL_INT"].alt
        except:
            print("ground atanamadı")

    def update_window(self):
        msg = None
        self.connection.mav.request_data_stream_send(self.connection.target_system, self.connection.target_component,mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)
        try:
            attitude = self.take_message("ATTITUDE",False)
        except:
            print("ATTITUDE alınamadı")
        try:
            attitude = self.take_message("VFR_HUD",False)
        except:
            print("VFR_HUD alınamadı")
        try:
            attitude = self.take_message("GLOBAL_POSITION_INT",False)
        except:
            print("GLOBAL_POSITION_INT alınamadı")

        try:
            attitude = self.take_message("VEHICLE_GLOBAL_POSİTİON",False)
        except:
            print("yok")


        try:
            yaw = self.connection.messages["ATTITUDE"].yaw
            self.yaw = self.set_degree(yaw)
        except:
            print("yaw atanamadı")
        try:
            roll = self.connection.messages["ATTITUDE"].roll
            self.roll = self.set_degree(roll)
        except:
            print("roll atanamadı")
        try:
            pitch = self.connection.messages["ATTITUDE"].pitch
            self.pitch = self.set_degree(pitch)
        except:
            print("pitch atanamadı")

        try:
            #lat = self.connection.messages["GLOBAL_POSITION_INT"].lat
            lat = self.connection.messages["GPS_RAW_INT"].lat
            #lon = self.connection.messages["GLOBAL_POSITION_INT"].lon
            lon = self.connection.messages["GPS_RAW_INT"].lon
            self.lat = float(str(lat)[:2]+"."+str(lat)[2:])
            self.lon = float(str(lon)[:2]+"."+str(lon)[2:])
            #self.lat = float(str(lat)[:2]+"."+str(lat)[2:4]+"."+str(lat)[4:])
            #self.lon = float(str(lat)[:2]+"."+str(lon)[2:4]+"."+str(lon)[4:])
        except:
            pass



        #print(self.roll)
        #print(self.pitch)
        #print(self.yaw)
        #print(self.connection.messages)

        try:
            self.battery_r = self.connection.messages["SYS_STATUS"].battery_remaining
        except:
            pass

        try:
            #print("\n",self.connection.messages["POSITION_TARGET_GLOBAL_INT"].alt,"\n")
            self.altitude = self.connection.messages["POSITION_TARGET_GLOBAL_INT"].alt
        except:
            pass

        try:
            #lat long bunu içerisinde var
            self.airspeed = self.connection.messages["VFR_HUD"].airspeed
            self.groundspeed = self.connection.messages["VFR_HUD"].groundspeed
        except:
            pass

        #print(self.connection.messages["VFR_HUD"])
        #print(self.lat,self.lon)
        #self.give_all_messages()

        #yaw = random.randint(0,360)
        if self.yaw != 0:
            self.win.yaw_w.back_angle = -self.yaw
            self.win.yaw_w.queue_draw()
        #roll = random.randint(0,360)
        self.win.roll_w.cursor_angle = self.roll
        self.win.roll_w.queue_draw()
        #pitch = random.randint(0,360)
        self.win.pitch_w.cursor_angle = self.pitch
        self.win.pitch_w.queue_draw()
        #battery_r = random.randint(0,360)
        self.win.battery_w.cursor_angle = self.battery_r*270/100
        self.win.battery_w.text = str(int(self.battery_r))
        self.win.battery_w.queue_draw()
        #altitude = random.randint(0,360)
        altitude = self.altitude-self.ground
        self.win.altitude_w.cursor_angle = altitude*270/1200
        self.win.altitude_w.text = str(int(altitude))
        self.win.altitude_w.queue_draw()
        #airspeed = random.randint(0,360)
        airspeed_kmh = self.airspeed*36/10
        self.win.velo_w.cursor_angle = airspeed_kmh*270/120
        self.win.velo_w.text = str(int(airspeed_kmh))
        self.win.velo_w.queue_draw()
        #print(self.roll,self.pitch,self.yaw)

        
        self.osm.image_remove_all()
        #print(self.lat,self.lon)
        self.osm.set_center_and_zoom(self.lat,self.lon,self.zoom)
        self.osm.image_add(self.lat,self.lon,self.iha_img)

        #print(msg)
        return self.win

if __name__ == '__main__':
    app = Application()
    app.run(sys.argv)

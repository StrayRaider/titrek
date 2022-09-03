import gi
gi.require_version('Gtk','3.0')
gi.require_version("OsmGpsMap", "1.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, OsmGpsMap as osmgpsmap
from pymavlink import mavutil
import os
from i_lib import roll
from i_lib import pitch
from i_lib import yaw
from i_lib import velo
from i_lib import altitude
from i_lib import battery


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = kwargs["application"]

        self.lat = self.parent.lat
        self.lon = self.parent.lon

        #--header_bar--
        header_bar = Gtk.HeaderBar()
        self.set_titlebar(header_bar)
        header_bar.set_show_close_button(True)
        header_bar.set_title("TITREK")

        #--arm but--
        self.arm_but = Gtk.Button()
        self.arm_but.connect("clicked",self.arm_disarm)
        header_bar.pack_start(self.arm_but)
        self.red_image = Gtk.Image.new_from_file("./assets/red_dot.png")
        self.yellow_image = Gtk.Image.new_from_file("./assets/yellow_dot.png")
        self.arm_but.set_always_show_image(True)

        #--combo_box--
        self.mode_combo = Gtk.ComboBoxText()
        for mode in ["GUIDED","AUTO"]:
            self.mode_combo.append_text(mode)
        self.mode_combo.set_active(0)
        self.mode_combo.connect("changed",self.mode_combo_changed)
        header_bar.pack_start(self.mode_combo)

        main_box = Gtk.HBox()
        self.add(main_box)

        left = Gtk.VBox()
        main_box.pack_start(left,0,0,5)
        mid = Gtk.VBox()
        main_box.pack_start(mid,0,0,5)
        right = Gtk.VBox()
        main_box.pack_start(right,0,0,5)

        #----left----
        self.yaw_w = yaw.Yaw()
        left.pack_start(self.yaw_w,0,0,5)
        self.pitch_w = pitch.Pitch()
        left.pack_start(self.pitch_w,0,0,5)
        self.roll_w = roll.Roll()
        left.pack_start(self.roll_w,0,0,5)

        #----mid----
        self.osm = self.parent.osm
        self.map_lat = 39.9
        self.map_long = 32.8
        #self.iha_img = yaw.Yaw()
        #self.iha_img.set_rotation(100)
        #self.osm.image_add(self.map_lat,self.map_long,self.iha_img)

        #print(self.iha_img.get_rotation)
        #self.osm.gps_add(self.map_lat,self.map_long,osmgpsmap.MAP_INVALID)
        
        self.osm.layer_add(
        osmgpsmap.MapOsd(show_dpad=True,
        show_zoom=True,
        show_crosshair=True)
        )
        self.osm.set_property("map-source", osmgpsmap.MapSource_t.OPENSTREETMAP)
        
        mid.pack_start(self.osm,1,1,5)
        mid.set_size_request(500, 500)

        #----right----
        self.battery_w = battery.Battery()
        right.pack_start(self.battery_w,0,0,5)
        self.velo_w = velo.Velo()
        right.pack_start(self.velo_w,0,0,5)
        self.altitude_w = altitude.Altitude()
        right.pack_start(self.altitude_w,0,0,5)

        self.plane_is_armed = self.parent.connection.motors_armed()
        if self.plane_is_armed:
            self.arm_but.set_image(self.yellow_image)
            self.arm_but.set_label("DISARM")
        else:
            self.arm_but.set_image(self.red_image)
            self.arm_but.set_label("ARM")

        self.plane_mode = self.parent.connection.mode_mapping()[self.mode_combo.get_active_text()]
        self.mode_combo_changed(self.mode_combo)

    def arm_disarm(self,widget):
        if self.parent.connection != None:
            if self.plane_is_armed == 0:
                self.send_arm(1)#arm eder
                self.arm_but.set_image(self.yellow_image)
                self.arm_but.set_label("DISARM")
            else:
                self.send_arm(0)#disarm eder
                self.arm_but.set_image(self.red_image)
                self.arm_but.set_label("ARM")

    def send_arm(self,bool_arm = 1):
        self.parent.connection.mav.command_long_send(self.parent.connection.target_system, self.parent.connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0 ,bool_arm,0,0,0,0,0,0)
        #print(self.take_message("COMMAND_ACK"))#4 failed 2 rejected
        if not(self.parent.take_message("COMMAND_ACK").result):
            print("arm command recieved")
            self.plane_is_armed = bool_arm
            if bool_arm==1:
                self.parent.connection.motors_armed_wait()
        else:
            print("arm command is not recieved")

    def mode_combo_changed(self,widget):
        text = widget.get_active_text()
        mode_id = self.parent.connection.mode_mapping()[text]
        self.parent.connection.mav.set_mode_send(self.parent.connection.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,mode_id)
        try:
            if not(self.parent.take_message("COMMAND_ACK").result):
                print("set mode command recieved")
                self.plane_mode = text
            else:
                print("set mode command is not recieved")
        except:
            print("set mode command is not recieved")
            

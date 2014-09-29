import xbmc
import xbmcgui
import xbmcaddon
import os
import datetime
import time
import _strptime
import threading
import urllib2
import StringIO
import sqlite3
import threading
from sqlite3 import dbapi2 as database
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from UserDict import DictMixin

# two separate flags to kill the AllChannelsThread and the TimerThread
__killthread__ = False
CHANNELS_PER_PAGE = 7


#get actioncodes from keyboard.xml
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_ENTER = 7
ACTION_PREVIOUS_MENU = 10
ACTION_BACKSPACE = 110
ACTION_NUMBER1 = 59
ACTION_NUMBER2 = 60
ACTION_NUMBER3 = 61
ACTION_NUMBER4 = 62
ACTION_NUMBER5 = 63
ACTION_NUMBER6 = 64
ACTION_NUMBER7 = 65
ACTION_NUMBER8 = 66
ACTION_NUMBER9 = 67
ACTION_NUMBER0 = 58

def cSetVisible(WiNdOw,iD,V=True): WiNdOw.getControl(iD).setVisible(V)
ADDON = xbmcaddon.Addon(id = 'script.tvguide')


class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            if len(self) != len(other):
                return False
            for p, q in  zip(self.items(), other.items()):
                if p != q:
                    return False
            return True
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other



class MyClass(xbmcgui.WindowXML):

     def __new__(cls):
         return super(MyClass, cls).__new__(cls, 'script-tvguide-mainmenu.xml', ADDON.getAddonInfo('path'))


     def __init__(self):
         self._timel = []
         self.thread = None



     def onInit(self):
         cSetVisible(self,2,False)
         self.getControl(3).setAnimations([('fade', 'effect=fade start=0 end=100 time=1500')])
         self.getControl(10).setVisible(False)
         cSetVisible(self,11,True)
         allchannels_yellow_BOX = self.getControl(11)
         allchannels_yellow_BOX.setImage("special://home/addons/script.tvguide/resources/skins/Default/media/channels_yellow.png")
         cSetVisible(self,10,False)
         allchannels_blue_BOX = self.getControl(10)
         allchannels_blue_BOX.setImage("special://home/addons/script.tvguide/resources/skins/Default/media/channels_blue.png")
         cSetVisible(self,4200,False)
         loading_gif = self.getControl(4200)
         loading_gif.setImage("special://home/addons/script.tvguide/resources/skins/Default/media/tvguide-loading.gif")
         ADDON = xbmcaddon.Addon(id = 'script.tvguide')
         english_enabled = ADDON.getSetting('english.enabled') == 'true'
         french_enabled = ADDON.getSetting('french.enabled') == 'true'
         self.getString = ADDON.getLocalizedString
         self.getControl(46).setVisible(False)
         self.getControl(46).setLabel(self.getString(30001))
         self.getControl(47).setVisible(False)
         self.getControl(47).setLabel(self.getString(30001))
         self.getControl(54).setVisible(False)
         self.getControl(54).setLabel(self.getString(30005))
         self.getControl(55).setVisible(False)
         self.getControl(55).setLabel(self.getString(30005))
         self.getControl(90).setVisible(False)
         self.getControl(90).setLabel(self.getString(30023))
         cSetVisible(self,4201,False)
         cSetVisible(self,4202,False)
         cSetVisible(self,4204,False)
         cSetVisible(self,4205,False)
         cSetVisible(self,4206,False)



         if english_enabled:
             cSetVisible(self,46,True)
             cSetVisible(self,54,True)
             



         if french_enabled:
             cSetVisible(self,264,True)

         
         
     def parseDateTimeToMinutesSinceEpoch(self, p_datetime):
         datetime = time.strptime(p_datetime, "%Y%m%d%H%M%S")
         seconds_epoch = time.mktime(datetime)
         minutes_epoch = int(seconds_epoch / 60)
         return minutes_epoch



     def abortdownload(self):
         global __killthread__
         __killthread__ = True
         if self.thread is not None:
            self.thread.join(3000)
         del self.thread
         self.thread = None



     def All_Channels(self):
         global __killthread__
         self.getControl(4202).setLabel("0%")
         try:
             # DOWNLOAD THE XML SOURCE HERE
             url = ADDON.getSetting('allchannel.url')
             data = ''
             response = urllib2.urlopen(url)
             meta = response.info()
             file_size = int(meta.getheaders("Content-Length")[0])
             file_size_dl = 0
             block_size = 2048
             while True and not __killthread__:
                 mbuffer = response.read(block_size)
                 if not mbuffer:
                     break
                 file_size_dl += len(mbuffer)
                 data += mbuffer
                 state = int(file_size_dl * 10.0 / file_size)
                 self.getControl(4202).setLabel(str(state) + '%')
             else:
                 if __killthread__:
                     raise AbortDownload('downloading')
             del response

             # CREATE DATABASE
             profilePath = xbmc.translatePath(os.path.join('special://userdata/addon_data/script.tvguide', 'source.db'))
             if os.path.exists(profilePath):
                 os.remove(profilePath)
             con = database.connect(profilePath)
             cur = con.cursor()
             cur.execute('CREATE TABLE programs(channel TEXT, title TEXT, start_date TIMESTAMP, stop_date TIMESTAMP, description TEXT)')
             con.commit()

             # Get the loaded data
             total_count = data.count('programme')/2
             tv_elem = ElementTree.parse(StringIO.StringIO(data)).getroot()
             cur = con.cursor()
             count = 1
             channels = OrderedDict()

             for channel in tv_elem.findall('channel'):
                 channel_name = channel.find('display-name').text
                 for program in channel.findall('programme'):
                     if __killthread__:
                         raise AbortDownload('filling')
                     title = program.find('title').text
                     start_time = program.get("start")
                     stop_time = program.get("stop")
                     cur.execute("INSERT INTO programs(channel, title, start_date, stop_date)" + " VALUES(?, ?, ?, ?)", [channel_name, title, start_time, stop_time])
                     status = 10 + int(float(count)/float(total_count) * 90.0)
                     self.getControl(4202).setLabel(str(status) + '%')
                     xbmc.sleep(10)
                     count += 1
                 con.commit()
             print 'Channels have been successfully stored into the database!'
             self.getControl(4202).setLabel('100%')
             xbmc.sleep(3000)

             # Set the date and time row
             current_time = time.time() # now (in seconds)
             half_hour = current_time + 60*30  # now + 30 minutes
             one_hour = current_time + 60*60  # now + 60 minutes

             for t in [current_time,half_hour,one_hour]:
                 if (0 <= datetime.datetime.now().minute <= 29):
                     self.getControl(4204).setLabel(time.strftime("%I").lstrip('0') + ':00' + time.strftime("%p"))
                     self.getControl(4205).setLabel(time.strftime("%I").lstrip('0') + ':30' + time.strftime("%p"))
                     self.getControl(4206).setLabel(time.strftime("%I" + ":00%p",time.localtime(t)).lstrip("0"))
                 else:
                     self.getControl(4204).setLabel(time.strftime("%I").lstrip('0') + ':30' + time.strftime("%p"))
                     self.getControl(4205).setLabel(time.strftime("%I" + ":00%p",time.localtime(t)).lstrip("0"))
                     self.getControl(4206).setLabel(time.strftime("%I" + ":30%p",time.localtime(t)).lstrip("0"))


             #Pull the data from the database
             channelList = list()
             database_path = xbmc.translatePath(os.path.join('special://userdata/addon_data/script.tvguide', 'source.db'))

             if os.path.exists(database_path):
                 #get the channels list
                 cur.execute('SELECT channel FROM programs WHERE channel GROUP BY channel')

                 for row in cur:
                     channels = row[0].encode('ascii')
                     channelList.append(channels)

                 # set the channels text
                 for index in range(0, CHANNELS_PER_PAGE):
                     channel = channelList[index]
                     channel_index = index

                     if channel is not None:
                         self.getControl(4110 + index).setLabel(channel)

                     #get the programs list
                     cur.execute('SELECT channel, title, start_date, stop_date FROM programs WHERE channel=?', [channel])
                     programList = list()
                     programs = cur.fetchall()

                     for row in programs:
                         program = row[1].encode('ascii'), str(row[2]), str(row[3])
                         title = row[1].encode('ascii')
                         program_start_date = str(row[2])
                         program_end_date = str(row[3])                       
                         
                         #convert the date formats into minutes
                         minutes_start = self.parseDateTimeToMinutesSinceEpoch(program_start_date)
                         minutes_end = self.parseDateTimeToMinutesSinceEpoch(program_end_date)
                         minutes_length = minutes_end - minutes_start
                        
                         program_index = channel_index
                         program_start = channel_index * 60
                         program_length = minutes_length
                         program_notification = program
                         program_minutes = minutes_length
                         program_start_to_end = 100
                         programs_top = 325
                         program_height = 34.5
                         pixels_per_minute = 1080 / minutes_length
                         program_gap = 10
                         position_start = program_start_to_end + (program_start * pixels_per_minute) + ((program_index - 1) * program_gap)
                         position_top = programs_top + (channel_index * program_height) + ((channel_index - 1) * program_gap)
                         program_width = program_length * pixels_per_minute

                         if program_width > 1:
                             if program_notification:
                                 button_nofocus = 'channels_bar1.png'
                                 button_focus = 'channels_yellow.png'
                             else:
                                 button_nofocus = 'channels_bar1.png'
                                 button_focus = 'channels_yellow.png'

                             if program_width < 1:
                                 program_title = ''
                             else:
                                 program_title = title
                                 

                             program_controls = xbmcgui.ControlButton(
                                 position_start, 
                                 position_top, 
                                 program_width, 
                                 program_height, 
                                 program_title, 
                                 focusTexture = button_focus, 
                                 noFocusTexture = button_nofocus
                             )
                             self.addControl(program_controls)
                     cur.close()



             #Enabled EPG and other controls
             self.getControl(4200).setVisible(False)
             self.getControl(4202).setVisible(False)
             self.getControl(4203).setVisible(False)
             self.getControl(4204).setVisible(True)
             self.getControl(4205).setVisible(True)
             self.getControl(4206).setVisible(True)



         except AbortDownload, e:
             __killthread__ = False
             if e.value == 'downloading':
                 try:
                    if response is not None:
                         self.thread = AllChannelsThread(self.All_Channels)
                         self.thread.start()
                    return
                 except:
                    return
             elif e.value == 'filling':
                 try:
                    if cur is not None:
                        del cur
                    if con is not None:
                        con.close()
                        del con
                    if os.path.exists(profilePath):
                        os.remove(profilePath)
                    return
                 except:
                    return


     def onAction(self, action):
         tvguide_table = xbmc.getCondVisibility('Control.IsVisible(5000)')
         tvguide_1 = xbmc.getCondVisibility('Control.IsVisible(5001)')
         tvguide_2 = xbmc.getCondVisibility('Control.IsVisible(4201)')
         tvguide_3 = xbmc.getCondVisibility('Control.IsVisible(4001)')
         tvguide_4 = xbmc.getCondVisibility('Control.IsVisible(4002)')
         tvguide_5 = xbmc.getCondVisibility('Control.IsVisible(4003)')
         tvguide_6 = xbmc.getCondVisibility('Control.IsVisible(4004)')
         tvguide_7 = xbmc.getCondVisibility('Control.IsVisible(4011)')
         tvguide_8 = xbmc.getCondVisibility('Control.IsVisible(4012)')
         tvguide_9 = xbmc.getCondVisibility('Control.IsVisible(4013)')
         tvguide_10 = xbmc.getCondVisibility('Control.IsVisible(4014)')
         tvguide_11 = xbmc.getCondVisibility('Control.IsVisible(4020)')
         tvguide_yellow = xbmc.getCondVisibility('Control.IsVisible(3)')
         self.strAction = xbmcgui.ControlLabel(300, 200, 600, 200, '', 'font14', '0xFF00FF00')
         allchannels_yellow = xbmc.getCondVisibility('Control.IsVisible(11)')
         self.addControl(self.strAction)
         ADDON = xbmcaddon.Addon(id = 'script.tvguide')
         english_enabled = ADDON.getSetting('english.enabled') == 'true'
         french_enabled = ADDON.getSetting('french.enabled') == 'true'
         allchannels_enabled = ADDON.getSetting('allchannels.enabled') == 'true'
         main_loading = 4200
         main_loading_progress = 4201
         main_loading_time_left = 4202



         if action == ACTION_PREVIOUS_MENU:
             self.close()
             return


         if action == ACTION_BACKSPACE:
             if allchannels_enabled:
                 cSetVisible(self,3,True)
                 cSetVisible(self,11,True)                 
                 cSetVisible(self,4200,False)
                 cSetVisible(self,4201,False)
                 cSetVisible(self,4202,False)
                 self.getControl(4202).setLabel("")
                 ADDON.setSetting('allchannels.enabled', 'false')
                 self.abortdownload()
                 self.getControl(4202).setLabel('')
                 self.getControl(4203).setVisible(False)
                 self.getControl(4204).setVisible(False)
                 self.getControl(4205).setVisible(False)
                 self.getControl(4206).setVisible(False)
                 cSetVisible(self,46,True)
                 cSetVisible(self,90,False)
                 cSetVisible(self,54,True)
                 profilePath = xbmc.translatePath(os.path.join('special://userdata/addon_data/script.tvguide', 'source.db'))
                 # Deletes the db file if it persists after abort
                 if os.path.exists(profilePath):
                     os.remove(profilePath)



             elif tvguide_yellow == True:
                 self.close()
                 return



         if action == ACTION_ENTER:
             if tvguide_yellow:
                 if allchannels_yellow:
                     cSetVisible(self,3,False)
                     cSetVisible(self,11,False)
                     ADDON.setSetting('allchannels.enabled', 'true')
                     cSetVisible(self,4200,True)
                     cSetVisible(self,4201,True)
                     cSetVisible(self,4202,True)
                     cSetVisible(self,46,False)
                     cSetVisible(self,54,False)
                     cSetVisible(self,90,True)
                     self.getControl(4202).setLabel("0%")
                     self.thread = AllChannelsThread(self.All_Channels)
                     self.thread.start()
                      
                         

         if action == ACTION_MOVE_RIGHT:
             if allchannels_enabled:
                 #move the yellow image to the next button
                 pass


         if action == ACTION_MOVE_LEFT:
             if allchannels_enabled:
                 #move the yellow image to the next button
                 pass



         if action == ACTION_MOVE_UP:
             if allchannels_enabled:
                 #move the yellow image to the next button
                 pass



         if action == ACTION_MOVE_DOWN:
             if allchannels_enabled:
                 #move the yellow image to the next button
                 pass





class AllChannelsThread(threading.Thread):
    # This is needed for proper threading. The other method continued to block on the call.
    def __init__(self, xtarget):
        threading.Thread.__init__(self, name='all_channels_thread')
        self.xtarget = xtarget

    def start(self):
        threading.Thread.start(self)

    def run(self):
        self.xtarget()

    def stop(self):
        self.join(2000)

class AbortDownload(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

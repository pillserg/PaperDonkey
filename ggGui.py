# -*- coding: utf-8 -*-
import wx
import getGaz
from wx.lib.wordwrap import wordwrap
import wx.lib.delayedresult as delayedresult
import sys
import time
import re

VERSION = ' '.join((getGaz.VERSION, getGaz.NAME))
#-----------------------------START REDIR STDIN/STDERR---------------------------
class RedirectText:

    def __init__(self, aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)
#-----------------------------END REDIR STDIN/STDERR---------------------------

class MyFrame(wx.Frame):
    def __init__(
            self, parent=None, ID=-1, title=VERSION, pos=wx.DefaultPosition,
            size=(600,770), style=wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CAPTION | wx.MINIMIZE_BOX
            ):

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = wx.Panel(self, -1)
        favicon = wx.Icon('donkey.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        self.SetIcon(favicon)
        self.CenterOnScreen()
        self.CreateStatusBar()
        self.SetStatusText("This is the statusbar")
        self.PROXIE = False
        self.Date_UK = False
        self.OutDir = ''
        self.ext = '.txt'
        self.cfg_dict = self.LoadState()

#-----------------------------START GAZET BUTTONS--------------------------------

#-----------------------------START UK BUTTTONS----------------------------------
        self.button_GetUK = wx.Button(panel, 1003, u'Затянуть УК   ')
        self.button_GetUK.SetPosition((15, 15))
        self.text_UK_Date =  wx.TextCtrl(panel, -1, self.localDate(), size=(200, -1))
        self.text_UK_Date.SetPosition((110,16))
        self.Bind(wx.EVT_BUTTON, self.OnGetUK, self.button_GetUK)
        self.Bind(wx.EVT_TEXT, self.EvtText_UK_Date, self.text_UK_Date)
#-----------------------------END UK BUTTTONS------------------------------------

#-----------------------------START RG BUTTTONS----------------------------------
        self.button_GetRG = wx.Button(panel, 1004, u'Затянуть RG   ')
        self.button_GetRG.SetPosition((15, 45))
        self.Bind(wx.EVT_BUTTON, self.OnGetRG, self.button_GetRG)
        self.text_RG_URL =  wx.TextCtrl(panel, -1, 'http://rg.kiev.ua/page1/nomer996/', size=(200, -1))
        self.text_RG_URL.SetPosition((110,46))
#-----------------------------END RG BUTTTONS------------------------------------

#-----------------------------START DAY BUTTTONS---------------------------------
        self.button_GetDAY = wx.Button(panel, 1006, u'Затянуть DAY ')
        self.button_GetDAY.SetPosition((15, 75))
        self.Bind(wx.EVT_BUTTON, self.OnGetDAY, self.button_GetDAY)
        self.text_DAY_URL =  wx.TextCtrl(panel, -1, 'http://www.day.kiev.ua/ua.2010.142', size=(200, -1))
        self.text_DAY_URL.SetPosition((110,76))
#-----------------------------END DAY BUTTTONS---------------------------------

#-----------------------------START WEEKEND BUTTTONS-----------------------------
        self.button_GetWEND = wx.Button(panel, 1007, u'Затянуть WD  ')
        self.button_GetWEND.SetPosition((15, 105))
        self.Bind(wx.EVT_BUTTON, self.OnGetWEND, self.button_GetWEND)
        self.StaticText_WEND_N = wx.StaticText(panel, -1, u"№", (113, 110))
        self.text_WEND_NUM =  wx.TextCtrl(panel, -1, '32', size=(30, -1))
        self.text_WEND_NUM.SetPosition((130,106))

        self.cb_WEND = wx.CheckBox(panel, -1, u"Все статьи")
        self.cb_WEND.SetPosition((170,110))
#-----------------------------END WEEKEND BUTTTONS----------------------------

#-----------------------------START 2000 BUTTTONS-----------------------------
        self.button_Get2000 = wx.Button(panel, 1008, u'Затянуть 2000')
        self.button_Get2000.SetPosition((15, 135))
        self.Bind(wx.EVT_BUTTON, self.OnGet2000, self.button_Get2000)
        self.StaticText_2000_N = wx.StaticText(panel, -1, u"№", (113, 140))
        self.text_2000_NUM =  wx.TextCtrl(panel, -1, '32', size=(30, -1))
        self.text_2000_NUM.SetPosition((130,136))

        self.cb_2000 = wx.CheckBox(panel, -1, u"Все статьи")
        self.cb_2000.SetPosition((170,140))
#-----------------------------END 2000 BUTTTONS--------------------------------

#-----------------------------START FACTS BUTTTONS-----------------------------
        self.button_GetFacts = wx.Button(panel, 1009, u'Затянуть Fact ')
        self.button_GetFacts.SetPosition((15, 165))
        self.Bind(wx.EVT_BUTTON, self.OnGetFacts, self.button_GetFacts)
        self.text_facts_url =  wx.TextCtrl(panel, -1,
                                          'http://www.facts.kiev.ua/archive/%s'%self.localDate(Format='FACTS'),
                                          size=(250, -1))
        self.text_facts_url.SetPosition((110,166))
#-----------------------------END FACTS BUTTTONS--------------------------------

#-----------------------------START ZN BUTTTONS-----------------------------
        self.button_GetZN = wx.Button(panel, 1010, u'Затянуть ZN    ')
        self.button_GetZN.SetPosition((15, 195))
        self.Bind(wx.EVT_BUTTON, self.OnGetZN, self.button_GetZN)
        self.text_ZN_url =  wx.TextCtrl(panel, -1,
                                          'http://www.zn.ua/',
                                          size=(200, -1))
        self.text_ZN_url.SetPosition((110,196))
#-----------------------------END ZN BUTTTONS--------------------------------

#-----------------------------START KPR BUTTTONS-----------------------------
        self.button_GetKPR = wx.Button(panel, 1011, u'Затянуть KPR  ')
        self.button_GetKPR.SetPosition((15, 225))
        self.Bind(wx.EVT_BUTTON, self.OnGetKPR, self.button_GetKPR)
        self.text_KPR_url =  wx.TextCtrl(panel, -1,
                                          'http://www.kiev-pravda.kiev.ua',
                                          size=(200, -1))
        self.text_KPR_url.SetPosition((110,226))
#-----------------------------END KPR BUTTTONS--------------------------------

#-----------------------------START Tov BUTTTONS-----------------------------
        self.button_GetTov = wx.Button(panel, 1012, u'Затянуть Tov  ')
        self.button_GetTov.SetPosition((15, 255))
        self.Bind(wx.EVT_BUTTON, self.OnGetTov, self.button_GetTov)
        self.text_Tov_url =  wx.TextCtrl(panel, -1,
                                          'http://www.tovarish.com.ua/fresh/',
                                          size=(200, -1))
        self.text_Tov_url.SetPosition((110,256))
#-----------------------------END Tov BUTTTONS--------------------------------

#-----------------------------START KP BUTTTONS-----------------------------
        self.button_GetKP = wx.Button(panel, 1013, u'Затянуть KP    ')
        self.button_GetKP.SetPosition((15, 285))
        self.Bind(wx.EVT_BUTTON, self.OnGetKP, self.button_GetKP)
        self.text_KP_url =  wx.TextCtrl(panel, -1,
                                          'http://www.kp.ua',
                                          size=(200, -1))
        self.text_KP_url.SetPosition((110,286))
#-----------------------------END KP BUTTTONS--------------------------------

#-----------------------------START CN BUTTTONS-----------------------------
        self.button_GetCN = wx.Button(panel, 1014, u'Затянуть CN   ')
        self.button_GetCN.SetPosition((15, 315))
        self.Bind(wx.EVT_BUTTON, self.OnGetCN, self.button_GetCN)
        self.text_CN_URL =  wx.TextCtrl(panel, -1,
                                          'http://www.cn.com.ua',
                                          size=(200, -1))
        self.text_CN_URL.SetPosition((110,316))
#-----------------------------END CN BUTTTONS--------------------------------

#-----------------------------START UMOL BUTTTONS-----------------------------
        self.button_GetUMOL = wx.Button(panel, 1015, u'Затянуть Umol')
        self.button_GetUMOL.SetPosition((15, 345))
        self.Bind(wx.EVT_BUTTON, self.OnGetUMOL, self.button_GetUMOL)
        self.text_UMOL_URL =  wx.TextCtrl(panel, -1,
                                          'http://www.umoloda.kiev.ua/number/1749/',
                                          size=(250, -1))
        self.text_UMOL_URL.SetPosition((110,346))
#-----------------------------END UMOL BUTTTONS--------------------------------

#-----------------------------START CV BUTTTONS----------------------------------
        self.button_GetCV = wx.Button(panel, 10016, u'Затянуть CV   ')
        self.button_GetCV.SetPosition((15, 375))
        self.Bind(wx.EVT_BUTTON, self.OnGetCV, self.button_GetCV)
        self.text_CV_URL =  wx.TextCtrl(panel, -1, 'http://www.silskivisti.kiev.ua/18528/index.php', size=(250, -1))
        self.text_CV_URL.SetPosition((110,376))
#-----------------------------END CV BUTTTONS------------------------------------

#-----------------------------START KOM BUTTTONS----------------------------------
        self.button_GetKOM = wx.Button(panel, 10017, u'Затянуть KOM ')
        self.button_GetKOM.SetPosition((15, 405))
        self.Bind(wx.EVT_BUTTON, self.OnGetKOM, self.button_GetKOM)
        self.text_KOM_URL =  wx.TextCtrl(panel, -1, 'http://comments.com.ua', size=(250, -1))
        self.text_KOM_URL.SetPosition((110,406))
#-----------------------------END KOM BUTTTONS------------------------------------

#-----------------------------START GOLOS BUTTTONS----------------------------------
        self.button_GetGOLOS = wx.Button(panel, 10018, u'Затянуть GOL ')
        self.button_GetGOLOS.SetPosition((15, 435))
        self.Bind(wx.EVT_BUTTON, self.OnGetGOLOS, self.button_GetGOLOS)
        self.text_GOLOS_COOKIE =  wx.TextCtrl(panel, -1, 'PASTE COOKIE HERE...', size=(300, 80), style = wx.TE_MULTILINE)
        self.text_GOLOS_COOKIE.SetPosition((110,436))
#-----------------------------END GOLOS BUTTTONS------------------------------------

#-----------------------------END GAZET BUTTONS---------------------------------

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.jobID = 0
        self.abortEvent = delayedresult.AbortEvent()
#-----------------------------MENU CONTROL----------------------------------------
        menuBar = wx.MenuBar()

        # 1st menu from left
        menu1 = wx.Menu()
        menu1.Append(101, u"&О Программе", u"Инфо")
        menu1.Append(102, u"&Помощь", u"Вызов Справки")
        menu1.AppendSeparator()
        menu1.Append(104, u"&Выход", u"Выход из программы")
        # Add menu to the menu bar
        menuBar.Append(menu1, u"&Меню")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.CloseWindow, id=104)
        self.Bind(wx.EVT_MENU, self.OnInfo, id=101)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=102)

#---------------------------------------------------------------
#-----------------------------PROXIE CONTROL--------------------
        self.cb_PROXIE = wx.CheckBox(panel, -1, u"Тянуть через ПРОКСИ")
        self.cb_PROXIE.SetPosition((400,15))
        self.text_PROXIE =  wx.TextCtrl(panel, -1, "192.168.0.105:3128", size=(125, -1))
        self.text_PROXIE.SetPosition((400,47))

        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, self.cb_PROXIE)
        self.Bind(wx.EVT_TEXT, self.EvtText, self.text_PROXIE)
        self.text_PROXIE.Disable()
#------------------------------FILE FORMAT CONTROL---------------------------------
        sampleList = ['.txt', '.doc',]
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rb = wx.RadioBox(
                panel, -1, u"Ext", wx.DefaultPosition, wx.DefaultSize,
                sampleList, 2, wx.RA_SPECIFY_COLS
                )
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, self.rb)

        sizer.Add(self.rb, 0, wx.ALL, 20)
        self.rb.SetPosition((400,135))

#------------------------------OUTPUT DIR CONTROL---------------

        self.button_Out_Dir = wx.Button(panel,-1, u'Куды складывать')
        self.button_Out_Dir.SetPosition((400,75))
        self.Bind(wx.EVT_BUTTON, self.CngOutDir, self.button_Out_Dir)
        self.text_OUT_DIR =  wx.TextCtrl(panel, -1, 'D:\\', size=(125, -1))
        self.text_OUT_DIR.SetPosition((400,107))

#---------------------------------------------------------------

#------------------------------OUT LOG--------------------------
        self.log = wx.TextCtrl(panel, -1, size=(590,190),style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.log.SetPosition((2,528))
        redir = RedirectText(self.log)
        sys.stdout=redir
        sys.stderr = redir
        if self.cfg_dict:
            self.text_RG_URL.SetValue(self.cfg_dict.get('RG_URL'))
            self.text_DAY_URL.SetValue(self.cfg_dict.get('DAY_URL'))
            self.text_UMOL_URL.SetValue(self.cfg_dict.get('UMOL_URL'))
            self.text_CV_URL.SetValue(self.cfg_dict.get('CV_URL'))
            self.text_CN_URL.SetValue(self.cfg_dict.get('CN_URL'))
            self.text_WEND_NUM.SetValue(self.cfg_dict.get('WEND_NUM'))
            self.text_2000_NUM.SetValue(self.cfg_dict.get('2000_NUM'))
            self.text_PROXIE.SetValue(self.cfg_dict.get('PROXIE_ADDR'))
            self.text_OUT_DIR.SetValue(self.cfg_dict.get('SAVE_PATH'))
            self.OutDir = self.cfg_dict.get('SAVE_PATH')
            if self.cfg_dict.get('USEPROXIE') == '1':
                self.cb_PROXIE.SetValue(True)
                self.text_PROXIE.Enable(True)
                self.PROXIE = self.text_PROXIE.GetValue()
            else:
                self.cb_PROXIE.SetValue(False)
                self.PROXIE = False
                self.text_PROXIE.Enable(False)
            print u'Последний запуск: %s'%(self.cfg_dict.get('LAST_USE'),)
            pass
        print u'Готов к труду и обороне...'
#---------------------------------------------------------------
#--------------------JOB THREAD-------------------------------------------
        self.jobID = 0

#--------------------START MENU HANDLERS-------------------------------------
    #------------EXT SWITCH HANDLER------------

    def LoadState(self):
        cfg_dict = {}
        try:
            file = open('config.cfg','r')
            data = file.read().decode('utf-8')
            file.close()
        except IOError:
            print 'ERROR'
            return
        try:
            cfg_dict['RG_URL'] = re.findall('RG_URL = (.+)',data)[0]
            cfg_dict['DAY_URL'] = re.findall('DAY_URL = (.+)',data)[0]
            cfg_dict['UMOL_URL'] = re.findall('UMOL_URL = (.+)',data)[0]
            cfg_dict['CV_URL'] = re.findall('CV_URL = (.+)',data)[0]
            cfg_dict['CN_URL'] = re.findall('CN_URL = (.+)',data)[0]
            cfg_dict['WEND_NUM'] = re.findall('WEND_NUM = (.+)',data)[0]
            cfg_dict['2000_NUM'] = re.findall('2000_NUM = (.+)',data)[0]
            cfg_dict['PROXIE_ADDR'] = re.findall('PROXIE_ADDR = (.+)',data)[0]
            cfg_dict['USEPROXIE'] = re.findall('USEPROXIE = (.+)',data)[0]
            cfg_dict['SAVE_PATH'] = re.findall('SAVE_PATH = (.+)',data)[0]
            cfg_dict['LAST_USE'] = re.findall('LAST_USE = (.+)',data)[0]
        except:
            print 'ERROR with config file, loading DEFAULTS'
            return None
        return cfg_dict
        pass

    def SaveState(self):
        """Save some values to config fle"""
        #get values dict:
        if self.cb_PROXIE.IsChecked():
            USEPROXIE = 1
        else:
            USEPROXIE = 0
        cfg_dict = {'RG_URL':self.text_RG_URL.GetValue(),
                       'DAY_URL':self.text_DAY_URL.GetValue(),
                       'UMOL_URL':self.text_UMOL_URL.GetValue(),
                       'CV_URL':self.text_CV_URL.GetValue(),
                       'CN_URL':self.text_CN_URL.GetValue(),
                       'WEND_NUM':self.text_WEND_NUM.GetValue(),
                       '2000_NUM':self.text_2000_NUM.GetValue(),
                       'PROXIE_ADDR':self.text_PROXIE.GetValue(),
                       'USEPROXIE':USEPROXIE,
                       'SAVE_PATH':self.text_OUT_DIR.GetValue(),
                       'LAST_USE':self.localDate()}
        file = open('config.cfg','w')
        for key, value in cfg_dict.items():
            entry = '%s = %s\n'%(key, value)
            entry = entry.encode('utf-8')
            file.write(entry)
        file.close()
        pass

    def EvtRadioBox(self, event):
        if event.GetInt() == 1:
            self.log.WriteText(u'Сохранять файлы в .doc\n')
            self.ext = '.doc'
        else:
            self.log.WriteText(u'Сохранять файлы в .txt\n')
            self.ext = '.txt'
    #------------------------------------------

    def CloseWindow(self, event):
        self.Close()

    def OnInfo(self, event):
        info = wx.AboutDialogInfo()
        info.Name = u"Контекст PaperDonkey"
        info.Version = "0.9.2"
        info.Copyright = "(C) 2010 PiLL"
        info.Description = ' '
        info.Developers = [ "PiLL",]
        wx.AboutBox(info)
        pass

    def OnHelp(self, event):
        dlg = wx.MessageDialog(self, u"""Сорри но помощи пока нету,
точнее есть но работает только в формате  - Найди Пилю и спроси что за фигня""",
                               u'Упс',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        pass
#--------------------END MENU HANDLERS--------------------------------------
    #----------UK DATE & proxie text handlers-------------------------
    def EvtText_UK_Date(self, event):
        self.Date_UK = event.GetString()

    def EvtText(self, event):
        self.PROXIE = event.GetString()
#----------------------------------------------------------------------------
    def OnCloseWindow(self, event):
        self.SaveState()
        self.Destroy()

    def EvtCheckBox(self, event):
        """Работать через проксю или нет"""

        if event.IsChecked():
            self.text_PROXIE.Enable()
            self.PROXIE = str(self.text_PROXIE.GetValue())
        else:
            self.text_PROXIE.Disable()
            self.PROXIE = False

    def CngOutDir(self,event):
        """Change working Directory"""
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it.
        if dlg.ShowModal() == wx.ID_OK:
            self.OutDir = dlg.GetPath()
            self.text_OUT_DIR.ChangeValue(self.OutDir)

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        self.log.WriteText(u'Сохранять файлы в: '+ self.text_OUT_DIR.GetValue()+'\n')

    def localDate(self,Format='UK'):
        """Returns curent date in string format"""
        year = str (time.localtime () [0])
        month = str(time.localtime () [1])

        if len (month) < 2:
            month = '0'+month
        day = str(time.localtime () [2])

        if Format == 'UK':
            date = day + '.' + month + '.' + year
        elif Format == 'FACTS':
            date = '%s-%s-%s/'%(year,month,day)
        return date


#-----------------START Handle Get UK Button Evt (OUTHER THREAD)--------------------------------

    def OnGetUK(self, event):

        self.button_GetUK.Enable(False)
        print u'Тянем Урядовый курьер за %s'%self.text_UK_Date.GetValue()
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerUK,
                                  self._resultProducerUK,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerUK(self, jobID, abortEvent):
        """call getGaz to get UK."""
        gazet = getGaz.getUK(DATE = self.text_UK_Date.GetValue(),
                             TEST = False,
                             PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgExt(self.ext)
        gazet.process()
        return jobID

    def _resultConsumerUK(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Упс... Попытка стянуть Урядовый закончилась провалом"
            self.button_GetUK.Enable(True)
            return
        # get ready for next job:
        self.button_GetUK.Enable(True)

#-----------------END Handle Get UK Button Evt (OUTHER THtext_WEND_NUMREAD)-----------------

#-----------------START GET RG HANDLER (OUT THREAD)--------------------------

    def OnGetRG(self, event):

        self.button_GetRG.Enable(False)
        print u'Тянем рабочку за %s'%self.text_UK_Date.GetValue()
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerRG,
                                  self._resultProducerRG,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerRG(self, jobID, abortEvent):
        """call getGaz to get RG."""
        print 'OK'
        gazet = getGaz.getRG(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_RG_URL.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()
        return jobID

    def _resultConsumerRG(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except :
            print u"Упс... Попытка стянуть Рабочку закончилась провалом"
            self.button_GetRG.Enable(True)
            return

        # get ready for next job:
        self.button_GetRG.Enable(True)
#-----------------END GET RG HANDLER (OUT THREAD)--------------------------

#-----------------START GET DAY HANDLER (OUT THREAD)--------------------------

    def OnGetDAY(self, event):

        self.button_GetDAY.Enable(False)
        print u'Тянем ДЕНЬ'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerDAY,
                                  self._resultProducerDAY,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerDAY(self, jobID, abortEvent):
        """call getGaz to get RG."""
        print 'OK'
        gazet = getGaz.getDAY(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_DAY_URL.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()
        return jobID

    def _resultConsumerDAY(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть ДЕНЬ закончилась провалом"
            self.button_GetDAY.Enable(True)
            return

        # get ready for next job:
        self.button_GetDAY.Enable(True)
#-----------------END GET DAY HANDLER (OUT THREAD)--------------------------

#-----------------START GET WEEKEND HANDLER (OUT THREAD)--------------------------

    def OnGetWEND(self, event):
        print 'OK'
        self.button_GetWEND.Enable(False)

        print u'Тянем WEEKEND'
        self.abortEvent.clear()
        self.jobID += 1


        delayedresult.startWorker(self._resultConsumerWEND,
                                  self._resultProducerWEND,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)



    def _resultProducerWEND(self, jobID, abortEvent):
        """call getGaz to get WEND."""

        print 'OK'
        gazet = getGaz.getWEND(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.setAllArts(self.cb_WEND.IsChecked())
        gazet.chgNumber(self.text_WEND_NUM.GetValue())
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerWEND(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть УИКЕНД закончилась провалом"
            self.button_GetWEND.Enable(True)
            return

        # get ready for next job:
        self.button_GetWEND.Enable(True)
#-----------------END GET WEEKEND HANDLER (OUT THREAD)--------------------------

#-----------------START GET 2000 HANDLER (OUT THREAD)--------------------------

    def OnGet2000(self, event):
        print 'OK'
        self.button_Get2000.Enable(False)
        print u'Тянем 2000'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumer2000,
                                  self._resultProducer2000,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducer2000(self, jobID, abortEvent):
        """call getGaz to get WEND."""
        print 'OK'
        gazet = getGaz.get2000(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.setAllArts(self.cb_2000.IsChecked())
        gazet.chgNumber(self.text_2000_NUM.GetValue())
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID

    def _resultConsumer2000(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть 2000 закончилась провалом"
            self.button_Get2000.Enable(True)
            return

        # get ready for next job:
        self.button_Get2000.Enable(True)
#-----------------END GET 2000 HANDLER (OUT THREAD)--------------------------

#-----------------START GET FACTS HANDLER (OUT THREAD)--------------------------

    def OnGetFacts(self, event):
        print 'OK'
        self.button_GetFacts.Enable(False)
        print u'Тянем Факты'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerFacts,
                                  self._resultProducerFacts,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerFacts(self, jobID, abortEvent):
        """call getGaz to get Facts."""
        print 'OK'
        gazet = getGaz.getFacts(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_facts_url.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerFacts(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть Facts закончилась провалом"
            self.button_GetFacts.Enable(True)
            return

        # get ready for next job:
        self.button_GetFacts.Enable(True)
#-----------------END GET FACTS HANDLER (OUT THREAD)--------------------------

#-----------------START GET ZN HANDLER (OUT THREAD)--------------------------

    def OnGetZN(self, event):
        print 'OK'
        self.button_GetZN.Enable(False)
        print u'Тянем Зеркало Недели'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerZN,
                                  self._resultProducerZN,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerZN(self, jobID, abortEvent):
        """call getGaz to get ZN."""
        print 'OK'
        gazet = getGaz.getZN(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_ZN_url.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()
        return jobID

    def _resultConsumerZN(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть ZN закончилась провалом"
            self.button_GetZN.Enable(True)
            return

        # get ready for next job:
        self.button_GetZN.Enable(True)
#-----------------END GET ZN HANDLER (OUT THREAD)--------------------------

#-----------------START GET KPR HANDLER (OUT THREAD)--------------------------

    def OnGetKPR(self, event):
        print 'OK'
        self.button_GetKPR.Enable(False)
        print u'Тянем KPR'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerKPR,
                                  self._resultProducerKPR,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerKPR(self, jobID, abortEvent):
        """call getGaz to get KPR."""
        print 'OK'
        gazet = getGaz.getKPR(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerKPR(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть KPR закончилась провалом"
            self.button_GetKPR.Enable(True)
            return

        # get ready for next job:
        self.button_GetKPR.Enable(True)
#-----------------END GET KPR HANDLER (OUT THREAD)--------------------------


#-----------------START GET Tov HANDLER (OUT THREAD)--------------------------

    def OnGetTov(self, event):
        print 'OK'
        self.button_GetTov.Enable(False)
        print u'Тянем Tov'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerTov,
                                  self._resultProducerTov,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerTov(self, jobID, abortEvent):
        """call getGaz to get Tov."""
        print 'OK'
        gazet = getGaz.getTov(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        #gazet.chgWorkURL(str(self.text_ZN_url.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerTov(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"УПС... Попытка стянуть Tov закончилась провалом"
            self.button_GetTov.Enable(True)
            return

        # get ready for next job:
        self.button_GetTov.Enable(True)
#-----------------END GET Tov HANDLER (OUT THREAD)--------------------------


#-----------------START GET KP---------

    def OnGetKP(self, event):
        print 'OK'
        self.button_GetKP.Enable(False)
        print u'Тянем KP'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerKP,
                                  self._resultProducerKP,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerKP(self, jobID, abortEvent):
        """call getGaz to get KP."""
        print 'OK'
        gazet = getGaz.getKP(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        #gazet.chgWorkURL(str(self.text_ZN_url.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerKP(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть KP закончилась провалом"
            self.button_GetKP.Enable(True)
            return

        # get ready for next job:
        self.button_GetKP.Enable(True)
#-----------------END GET KP HANDLER (OUT THREAD)--------------------------

#-----------------START GET CN---------

    def OnGetCN(self, event):
        print 'OK'
        self.button_GetCN.Enable(False)
        print u'Тянем CN'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerCN,
                                  self._resultProducerCN,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerCN(self, jobID, abortEvent):
        """call getGaz to get CN."""
        print 'OK'
        gazet = getGaz.getCN(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_CN_URL.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerCN(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        #try:
        result = delayedResult.get()
        #except:
            #print u"Попытка стянуть CN закончилась провалом"
        self.button_GetCN.Enable(True)
        return

        # get ready for next job:
        self.button_GetCN.Enable(True)
#-----------------END GET CN HANDLER (OUT THREAD)--------------------------

#-----------------START GET UMOL---------

    def OnGetUMOL(self, event):
        print 'OK'
        self.button_GetUMOL.Enable(False)
        print u'Тянем UMOL'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerUMOL,
                                  self._resultProducerUMOL,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerUMOL(self, jobID, abortEvent):
        """call getGaz to get UMOL."""
        print 'OK'
        gazet = getGaz.getUMOL(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_UMOL_URL.GetValue()))
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerUMOL(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть UMOL закончилась провалом"
            self.button_GetUMOL.Enable(True)
            return

        # get ready for next job:
        self.button_GetUMOL.Enable(True)
#-----------------END GET UMOL HANDLER (OUT THREAD)--------------------------

#-----------------START GET CV---------

    def OnGetCV(self, event):
        print 'OK'
        self.button_GetCV.Enable(False)
        print u'Тянем CV'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerCV,
                                  self._resultProducerCV,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerCV(self, jobID, abortEvent):
        """call getGaz to get CV."""
        print 'OK'
        gazet = getGaz.getCV(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_CV_URL.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerCV(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть CV закончилась провалом"
            self.button_GetCV.Enable(True)
            return

        # get ready for next job:
        self.button_GetCV.Enable(True)
#-----------------END GET CV HANDLER (OUT THREAD)--------------------------

#-----------------START GET GOLOS---------

    def OnGetGOLOS(self, event):
        print 'OK'
        self.button_GetGOLOS.Enable(False)
        print u'Тянем GOLOS'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerGOLOS,
                                  self._resultProducerGOLOS,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerGOLOS(self, jobID, abortEvent):
        """call getGaz to get GOLOS."""
        print 'OK'
        gazet = getGaz.getGOLOS(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgCookie(str(self.text_GOLOS_COOKIE.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerGOLOS(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except:
            print u"Попытка стянуть GOLOS закончилась провалом"
            self.button_GetGOLOS.Enable(True)
            return

        # get ready for next job:
        self.button_GetGOLOS.Enable(True)
#-----------------END GET GOLOS HANDLER (OUT THREAD)--------------------------

#-----------------START GET KOMENTARI---------

    def OnGetKOM(self, event):
        print 'OK'
        self.button_GetKOM.Enable(False)
        print u'Тянем KOMMENTARI'
        self.abortEvent.clear()
        self.jobID += 1
        delayedresult.startWorker(self._resultConsumerKOM,
                                  self._resultProducerKOM,
                                  wargs=(self.jobID,self.abortEvent),
                                  jobID=self.jobID)

    def _resultProducerKOM(self, jobID, abortEvent):
        """call getGaz to get KOMENTARI."""
        print 'OK'
        gazet = getGaz.getKOM(TEST = False,PROXIE = self.PROXIE)
        if self.cb_PROXIE.IsChecked():
            print 'Working through: ' + self.PROXIE
            gazet.chgPROXIE(self.PROXIE)
        if self.OutDir:
            gazet.chgOutDir(self.OutDir)
        gazet.chgWorkURL(str(self.text_KOM_URL.GetValue()))
        gazet.chgExt(self.ext)
        print 'Looking in ',gazet.work_URL
        gazet.process()

        return jobID


    def _resultConsumerKOM(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        #try:
        result = delayedResult.get()
        #except:
            #print u"Попытка стянуть GOLOS закончилась провалом"
            #self.button_GetGOLOS.Enable(True)
            #return

        # get ready for next job:
        self.button_GetKOM.Enable(True)
#-----------------END GET GOLOS HANDLER (OUT THREAD)--------------------------

class MyApp(wx.App):
    """Application class"""

    def OnInit(self):

        self.frame = MyFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

def main():

    app = MyApp(True)
    app.MainLoop()

if __name__ == '__main__':
    main()


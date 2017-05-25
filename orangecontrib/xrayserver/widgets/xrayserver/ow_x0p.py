__author__ = "Luca Rebuffi"


from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.util.oasys_util import ShowHtmlDialog

import urllib
from http import server


from orangecontrib.xrayserver.util.xrayserver_util import HttpManager, XRayServerGui
from orangecontrib.xrayserver.widgets.gui.ow_xrayserver_widget import XrayServerWidget, XrayServerException

from PyQt5 import QtGui
import platform
if platform.system() == 'Darwin':
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
elif platform.system() == 'Linux':
    from PyQt5.QtWebKit import QWebView

APPLICATION = "/cgi/X0p_form.exe"

class X0p(XrayServerWidget):
    name = "X0h Search"
    description = "X0p"
    icon = "icons/x0p.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "X0h"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 1

    xway = Setting(2)
    wave = Setting(0.0)
    line = Setting("Cu-Ka1")

    code = Setting("Silicon")

    hkl11 = Setting(-5)
    hkl12 = Setting(-5)
    hkl13 = Setting(-5)

    hkl21 = Setting(5)
    hkl22 = Setting(5)
    hkl23 = Setting(5)

    qb1 = Setting(0.0)
    qb2 = Setting(90.0)

    prcmin = Setting(0.0)

    df1df2 = Setting(1)

    base1 = Setting(1)
    base2 = Setting(0)
    base3 = Setting(0)

    modesearch = Setting(0)

    q1 = Setting(0.0)
    q2 = Setting(180.0)


    def __init__(self):
        super().__init__()

        left_box_1 = oasysgui.widgetBox(self.controlArea, "X0h-Search Request Form", addSpace=True, orientation="vertical",
                                         width=400, height=630)

        left_box_2 = oasysgui.widgetBox(left_box_1, "X-rays", addSpace=True, orientation="horizontal", width=380, height=110)

        left_box_2_1 = oasysgui.widgetBox(left_box_2, "", addSpace=True, orientation="vertical", width=150, height=110)

        gui.radioButtons(left_box_2_1, self, "xway", ["Wavelength (Å)", "Energy (keV)", "Characteristic line"], callback=self.set_xway )

        self.box_wave = oasysgui.widgetBox(left_box_2, "", addSpace=True, orientation="vertical", width=190)
        gui.separator(self.box_wave, height=10)
        gui.lineEdit(self.box_wave, self, "wave", label="", labelWidth=0, addSpace=False, valueType=float, orientation="horizontal")

        self.box_line = oasysgui.widgetBox(left_box_2, "", addSpace=True, orientation="horizontal", width=190, height=110)
        gui.separator(self.box_line, height=120)
        XRayServerGui.combobox_text(self.box_line, self, "line", label="", labelWidth=0,
                               items=self.get_lines(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.line)

        button = gui.button( self.box_line, self, "?", callback=self.help_lines)
        button.setFixedWidth(15)

        self.set_xway()

        left_box_3 = oasysgui.widgetBox(left_box_1, "Crystal", addSpace=True, orientation="horizontal", width=380, height=60)

        self.box_crystal = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="horizontal", width=210)
        XRayServerGui.combobox_text(self.box_crystal, self, "code", label="", labelWidth=0,
                               items=self.get_crystals(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.code)


        button = gui.button( self.box_crystal, self, "?", callback=self.help_crystals)
        button.setFixedWidth(15)

        left_box_4 = oasysgui.widgetBox(left_box_1, "Bragg Planes Range", addSpace=True, orientation="horizontal", width=380, height=60)

        gui.lineEdit(left_box_4, self, "hkl11", label="From", labelWidth=50, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "hkl12", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "hkl13", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        gui.lineEdit(left_box_4, self, "hkl21", label="  To", labelWidth=50, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "hkl22", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "hkl23", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        left_box_7 = oasysgui.widgetBox(left_box_1, "Bragg Angle Range", addSpace=True, orientation="horizontal", width=380, height=60)

        gui.lineEdit(left_box_7, self, "qb1", label="From", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_7, self, "qb2", label="  To", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")

        tab_central = oasysgui.tabWidget(left_box_1)
        tab_1 = oasysgui.createTabPage(tab_central, "Intensity Control")
        tab_2 = oasysgui.createTabPage(tab_central, "Find only Bragg planes making certain angles to the surface")

        left_box_5 = oasysgui.widgetBox(tab_1, "", addSpace=True, orientation="vertical", width=370, height=250)

        gui.separator(left_box_5)

        gui.lineEdit(left_box_5, self, "prcmin", label="Minimum |xh/x0| (%)", labelWidth=250, addSpace=False, valueType=float, orientation="horizontal")

        left_box_5_1 = oasysgui.widgetBox(left_box_5, "Database Options for dispersion corrections df1, df2", addSpace=True, orientation="vertical", width=370, height=185)

        gui.radioButtons(left_box_5_1, self, "df1df2", ["Auto (Henke at low energy, X0h at mid, Brennan-Cowan\nat high)",
                                                      "Use X0h data (5-25 keV or 0.5-2.5 A), recommended for\nBragg diffraction",
                                                      "Use Henke data (0.01-30 keV or 0.4-1200 A),\nrecommended for soft x-rays",
                                                      "Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)"])

        left_box_6 = oasysgui.widgetBox(tab_2, "", addSpace=True, orientation="vertical", width=370, height=255)

        gui.separator(left_box_6)

        left_box_6_1 = oasysgui.widgetBox(left_box_6, "", addSpace=False, orientation="horizontal", width=370, height=30)

        gui.lineEdit(left_box_6_1, self, "base1", label="Surface Plane Indices", labelWidth=200, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_6_1, self, "base2", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_6_1, self, "base3", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        gui.radioButtons(left_box_6, self, "modesearch", ["Planes make angles from Theta1 to Theta2",
                                                      "Planes make angles from Theta1 to (Bragg_Angle - Theta2)",
                                                      "Planes make angles from (Bragg_Angle - Theta1)\nto (Bragg_Angle - Theta2)"])

        gui.separator(left_box_6, height=10)

        left_box_6_2 = oasysgui.widgetBox(left_box_6, "", addSpace=True, orientation="horizontal", width=370, height=30)

        gui.lineEdit(left_box_6_2, self, "q1", label="Theta1", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_6_2, self, "q2", label="  Theta2", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")

        button = gui.button(self.controlArea, self, "Find Planes!", callback=self.submit)
        button.setFixedHeight(30)

        gui.rubber(self.controlArea)

        self.tabs_widget = oasysgui.tabWidget(self.mainArea)
        self.tab_output = oasysgui.createTabPage(self.tabs_widget, "X-ray Server Ouput")

        self.x0h_output = QWebView(self.tab_output)

        self.tab_output.layout().addWidget(self.x0h_output)

        self.x0h_output.setFixedHeight(640)
        self.x0h_output.setFixedWidth(740)

    def set_xway(self):
        self.box_wave.setVisible(self.xway!=2)
        self.box_line.setVisible(self.xway==2)


    def submit(self):
        self.progressBarInit()
        self.setStatusMessage("Submitting Request")
        
        self.checkFields()

        parameters = {}

        parameters.update({"xway" : str(self.xway + 1)})
        parameters.update({"wave" : str(self.wave)})
        parameters.update({"line" : self.line})
        parameters.update({"code" : self.code})
        parameters.update({"hkl11" : str(self.hkl11)})
        parameters.update({"hkl12" : str(self.hkl12)})
        parameters.update({"hkl13" : str(self.hkl13)})
        parameters.update({"hkl21" : str(self.hkl21)})
        parameters.update({"hkl22" : str(self.hkl22)})
        parameters.update({"hkl23" : str(self.hkl23)})
        parameters.update({"qb1" : str(self.qb1)})
        parameters.update({"qb2" : str(self.qb2)})
        parameters.update({"prcmin" : str(self.prcmin)})
        parameters.update({"df1df2" : self.decode_df1df2()})
        parameters.update({"base1" : str(self.base1)})
        parameters.update({"base2" : str(self.base2)})
        parameters.update({"base3" : str(self.base3)})
        parameters.update({"modesearch" : self.decode_modesearch()})
        parameters.update({"q1" : str(self.q1)})
        parameters.update({"q2" : str(self.q2)})

        try:
            response = HttpManager.send_xray_server_request_POST(APPLICATION, parameters)
            response = response.split("<hr>")[0] + "\n </body></html>"

            self.x0h_output.setHtml(response)

        except urllib.error.HTTPError as e:
            self.x0h_output.setHtml('The server couldn\'t fulfill the request.\nError Code: '
                                    + str(e.code) + "\n\n" +
                                    server.BaseHTTPRequestHandler.responses[e.code][1])
        except urllib.error.URLError as e:
            self.x0h_output.setHtml('We failed to reach a server.\nReason: '
                                    + e.reason)
        except XrayServerException as e:
            ShowHtmlDialog.show_html("X-ray Server Error", e.response, width=750, height=500, parent=self)
        except Exception as e:
            self.x0h_output.setHtml('We failed to reach a server.\nReason: '
                                    + str(e))

        self.setStatusMessage("")
        self.progressBarFinished()

    def getLeftPartWidth(self):
        return 415

    def checkFields(self):
        pass

    def decode_df1df2(self):
        if self.df1df2 == 0: return "-1"
        elif self.df1df2 == 1: return "0"
        elif self.df1df2 == 2: return "2"
        elif self.df1df2 == 3: return "4"

    def decode_modesearch(self):
        if self.modesearch == 0: return "3"
        elif self.modesearch == 1: return "2"
        elif self.modesearch == 2: return "1"


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = X0p()
    w.show()
    app.exec()
    w.saveSettings()



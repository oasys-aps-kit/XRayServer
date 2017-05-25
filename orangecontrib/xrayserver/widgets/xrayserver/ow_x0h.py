__author__ = "Luca Rebuffi"

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets.exchange import DataExchangeObject
from oasys.util.oasys_util import ShowHtmlDialog

import urllib
from http import server

from orangecontrib.xrayserver.util.xrayserver_util import HttpManager, XRayServerPhysics, XRayServerGui
from orangecontrib.xrayserver.widgets.gui.ow_xrayserver_widget import XrayServerWidget, XrayServerException

from PyQt5 import QtGui

import platform
if platform.system() == 'Darwin':
    from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
elif platform.system() == 'Linux':
    from PyQt5.QtWebKit import QWebView

APPLICATION = "/cgi/X0h_form.exe"

class X0h(XrayServerWidget):
    name = "X0h"
    description = "X0h"
    icon = "icons/x0h.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "X0h"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 1

    outputs = [{"name": "xrayserver_data",
                "type": DataExchangeObject,
                "doc": "xrayserver_data",
                "id": "xrayserver_data"}, ]


    xway = Setting(2)
    wave = Setting(0.0)
    line = Setting("Cu-Ka1")

    coway = Setting(0)
    code = Setting("Silicon")
    amor = Setting("")
    chem = Setting("")
    rho = Setting(0.0)

    i1 = Setting(1)
    i2 = Setting(1)
    i3 = Setting(1)

    df1df2 = Setting(1)
    detail = Setting(1)

    def __init__(self):
        super().__init__()

        left_box_1 = oasysgui.widgetBox(self.controlArea, "X0h Request Form", addSpace=True, orientation="vertical",
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

        left_box_3 = oasysgui.widgetBox(left_box_1, "Target", addSpace=True, orientation="horizontal", width=380, height=140)

        left_box_3_1 = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="vertical", width=125, height=110)

        gui.radioButtons(left_box_3_1, self, "coway", ["Crystal", "Other Material", "Chemical Formula"], callback=self.set_coway )

        self.box_crystal = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="horizontal", width=210)
        XRayServerGui.combobox_text(self.box_crystal, self, "code", label="", labelWidth=0,
                               items=self.get_crystals(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.code)


        button = gui.button( self.box_crystal, self, "?", callback=self.help_crystals)
        button.setFixedWidth(15)

        self.box_other = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="horizontal", width=210)
        gui.separator(self.box_other, height=75)
        XRayServerGui.combobox_text(self.box_other, self, "amor", label="", labelWidth=0,
                               items=self.get_others(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.amor)

        button = gui.button( self.box_other, self, "?", callback=self.help_others)
        button.setFixedWidth(15)

        self.box_chemical = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="vertical", width=210, height=140)
        gui.separator(self.box_chemical, height=50)

        gui.lineEdit(self.box_chemical, self, "chem", label=" ", labelWidth=1, addSpace=False, valueType=str, orientation="horizontal", callback=self.set_rho)
        gui.lineEdit(self.box_chemical, self, "rho", label=u"\u03C1" + " (g/cm3)", labelWidth=60, addSpace=False, valueType=float, orientation="horizontal")

        self.set_coway()

        left_box_4 = oasysgui.widgetBox(left_box_1, "Reflection", addSpace=True, orientation="horizontal", width=380, height=60)

        gui.lineEdit(left_box_4, self, "i1", label="Miller indices", labelWidth=200, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "i2", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4, self, "i3", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        left_box_5 = oasysgui.widgetBox(left_box_1, "Database Options for dispersion corrections df1, df2", addSpace=True, orientation="vertical", width=380, height=185)

        gui.radioButtons(left_box_5, self, "df1df2", ["Auto (Henke at low energy, X0h at mid, Brennan-Cowan\nat high)",
                                                      "Use X0h data (5-25 keV or 0.5-2.5 A), recommended for\nBragg diffraction",
                                                      "Use Henke data (0.01-30 keV or 0.4-1200 A),\nrecommended for soft x-rays",
                                                      "Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)",
                                                      "Compare results for all of the above sources"])

        left_box_6 = oasysgui.widgetBox(left_box_1, "Output Options", addSpace=True, orientation="vertical", width=380, height=50)

        gui.checkBox(left_box_6, self, "detail", "Print atomic coordinates", labelWidth=250)

        button = gui.button(self.controlArea, self, "Get X0h!", callback=self.submit)
        button.setFixedHeight(30)

        gui.rubber(self.controlArea)

        self.tabs = []
        self.tabs_widget = oasysgui.tabWidget(self.mainArea)
        self.initializeTabs()

        self.x0h_output = QWebView(self.tabs[0])

        self.tabs[0].layout().addWidget(self.x0h_output)

        self.x0h_output.setFixedHeight(640)
        self.x0h_output.setFixedWidth(740)

    def getLeftPartWidth(self):
        return 415

    def set_xway(self):
        self.box_wave.setVisible(self.xway!=2)
        self.box_line.setVisible(self.xway==2)

    def set_coway(self):
        self.box_crystal.setVisible(self.coway==0)
        self.box_other.setVisible(self.coway==1)
        self.box_chemical.setVisible(self.coway==2)

    def set_rho(self):
        if not self.chem is None:
            if not self.chem.strip() == "":
                self.chem = self.chem.strip()
                self.rho = XRayServerPhysics.getMaterialDensity(self.chem)

    def initializeTabs(self):
        current_tab = self.tabs_widget.currentIndex()

        size = len(self.tabs)

        for index in range(0, size):
            self.tabs_widget.removeTab(size-1-index)

        self.tabs = [gui.createTabPage(self.tabs_widget, "X-ray Server Ouput"),
                     gui.createTabPage(self.tabs_widget, "Critical Angle for TER"),
                     gui.createTabPage(self.tabs_widget, "Darwin Curve (" + u"\u03C3" + " Pol.)"),
                     gui.createTabPage(self.tabs_widget, "Darwin Curve (" + u"\u03C0" + " Pol.)"),
                     ]

        for tab in self.tabs:
            tab.setFixedHeight(650)
            tab.setFixedWidth(750)

        self.plot_canvas = [None, None, None]

        self.tabs_widget.setCurrentIndex(current_tab)

    def submit(self):
        self.progressBarInit()
        self.setStatusMessage("Submitting Request")
        
        self.checkFields()

        parameters = {}

        parameters.update({"xway" : str(self.xway + 1)})
        parameters.update({"wave" : str(self.wave)})
        parameters.update({"line" : self.line})
        parameters.update({"coway" : str(self.coway)})
        parameters.update({"code" : self.code})
        parameters.update({"amor" : self.amor})
        parameters.update({"chem" : self.chem})
        parameters.update({"rho" : str(self.rho)})

        parameters.update({"i1" : str(self.i1)})
        parameters.update({"i2" : str(self.i2)})
        parameters.update({"i3" : str(self.i3)})
        parameters.update({"df1df2" : self.decode_df1df2()})

        parameters.update({"modeout" : "0" })
        parameters.update({"detail" : str(self.detail)})

        try:
            response = HttpManager.send_xray_server_request_POST(APPLICATION, parameters)
            response = self.clear_response(response)

            self.tabs_widget.setCurrentIndex(0)
            self.x0h_output.setHtml(response)

            data0, data1, data2 = self.extract_plots(response)

            exchange_data = DataExchangeObject("XRAYSERVER", "X0H")
            exchange_data.add_content("reflectivity", data0)
            exchange_data.add_content("reflectivity_units_to_degrees", 1.0)
            exchange_data.add_content("x-ray_diffraction_profile_sigma", data1)
            exchange_data.add_content("x-ray_diffraction_profile_sigma_units_to_degrees", 0.000277777805)
            exchange_data.add_content("x-ray_diffraction_profile_pi", data2)
            exchange_data.add_content("x-ray_diffraction_profile_pi_units_to_degrees", 0.000277777805)

            self.send("xrayserver_data", exchange_data)

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

    def clear_response(self, response):
        # remove links
        output = response.split("<hr>")[0] + "\n</body></html>"

        # remove "get the curve" images
        output = "".join(output.split("<input type=image src=\"images/get_the_curve.gif\" border=0 width=102 height=12 alt=\"Get the reflectivity curve\">"))
        output = "".join(output.split("<input type=image src=\"images/get_the_curve.gif\" border=0 width=102 height=12 alt=\"Get the Bragg curve (sigma)\">"))
        output = "".join(output.split("<input type=image src=\"images/get_the_curve.gif\" border=0 width=102 height=12 alt=\"Get the Bragg curve (pi)\">"))
        # remove question mark images and links
        output = "".join(output.split("<a  href=\"javascript:void(0)\" onClick=\"Wfloat(\'images/x0h_help_0.gif\',\'x0h_0\',740,357);\"><b>?</b></a> &nbsp;"))
        output = "".join(output.split("<a  href=\"javascript:void(0)\" onClick=\"Wfloat(\'images/x0h_help_h.gif\',\'x0h_h\',705,853);\"><b>?</b></a> &nbsp;"))

        return output

    def checkFields(self):
        pass

    def decode_df1df2(self):
        if self.df1df2 == 0: return "-1"
        elif self.df1df2 == 1: return "0"
        elif self.df1df2 == 2: return "2"
        elif self.df1df2 == 3: return "4"
        elif self.df1df2 == 4: return "10"

    def extract_plots(self, response):
        form_1_begin = False
        form_2_begin = False
        form_3_begin = False

        form_1 = None
        form_2 = None
        form_3 = None

        rows = response.split("\r\n")

        for row in rows:
            if form_1_begin:
                if "<td>" in row:
                    form_1_begin = False
            elif form_2_begin:
                if "<td>" in row:
                    form_2_begin = False
            elif form_3_begin:
                if "<td>" in row:
                    form_3_begin = False

            if form_1_begin:
                form_1.append(row)
            elif form_2_begin:
                form_2.append(row)
            elif form_3_begin:
                form_3.append(row)

            if "/cgi/ter_form.pl" in row:
                if form_1 is None:
                    form_1 = []
                    form_1_begin = True

            if "/cgi/gid_form.pl" in row:
                if form_2 is None:
                    form_2 = []
                    form_2_begin = True
                elif form_3 is None:
                    form_3 = []
                    form_3_begin = True

        self.setStatusMessage("Plotting Results")

        if not form_1 is None:
            x_1, y_1 = self.get_plots_from_form("/cgi/ter_form.pl", form_1)

            self.plot_histo(x_1, y_1, 40, 1, 0, "Critical Angle for TER", "Incidence angle [degrees]", "Reflectivity")
            self.tabs_widget.setCurrentIndex(1)
        else:
            x_1 = None
            y_1 = None
            
        if not form_2 is None:
            x_2, y_2 = self.get_plots_from_form("/cgi/gid_form.pl", form_2)

            self.plot_histo(x_2, y_2, 60, 2, 1, "Darwin Curve ($\sigma$ Pol.)", "Scan Angle [arcsec]", "Diffracted Intensity")
            self.tabs_widget.setCurrentIndex(2)
        else:
            x_2 = None
            y_2 = None

        if not form_3 is None:
            x_3, y_3 = self.get_plots_from_form("/cgi/gid_form.pl", form_3)

            self.plot_histo(x_3, y_3, 80, 3, 2, "Darwin Curve ($\pi$ Pol.)", "Scan Angle [arcsec]", "Diffracted Intensity")
            self.tabs_widget.setCurrentIndex(3)
        else:
            x_3 = None
            y_3 = None

        return [x_1, y_1], [x_2, y_2], [x_3, y_3]


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = X0h()
    w.show()
    app.exec()
    w.saveSettings()



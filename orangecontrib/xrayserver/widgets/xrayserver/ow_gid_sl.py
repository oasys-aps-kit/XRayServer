__author__ = "Luca Rebuffi"

import numpy

from oasys.widgets import widget
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from PyMca5.PyMcaGui.plotting.PlotWindow import PlotWindow

import urllib
from http import server

from orangecontrib.xrayserver.util.xrayserver_util import HttpManager, ShowTextDialog, XRayServerPhysics, XRayServerGui, XRayServerPlot
from orangecontrib.xrayserver.widgets.xrayserver.list_utility import ListUtility

from PyQt4 import QtGui
from PyQt4.QtWebKit import QWebView

APPLICATION = "/cgi/GID_form.pl"

class GID_SL(widget.OWWidget):
    name = "GID_SL"
    description = "GID_SL"
    icon = "icons/gidsl.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 3
    category = "GID_SL"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 1

    outputs = [{"name": "GID_SL_Result",
                "type": object,
                "doc": "GID_SL",
                "id": "gid_sl_result"}, ]

    template_type = Setting(0)
    simplified_form = Setting(0)
    full_form = Setting(0)

    xway = Setting(2)
    wave = Setting(0.0)
    line = Setting("Cu-Ka1")

    ipol = Setting(0)

    code = Setting("Germanium")
    df1df2 = Setting(0)

    sigma = Setting(0.0)
    w0 = Setting(1.0)
    wh = Setting(1.0)

    i1 = Setting(1)
    i2 = Setting(1)
    i3 = Setting(1)

    daa = Setting(0.0)

    igie = Setting(0)

    fcentre = Setting(0.0)

    unic = Setting(1)

    n1 = Setting(0)
    n2 = Setting(0)
    n3 = Setting(0)
    m1 = Setting(0)
    m2 = Setting(0)
    m3 = Setting(0)
    miscut = Setting(0.0)
    unim = Setting(0)
    axis= Setting(4)
    a1= Setting(0)
    a2= Setting(0)
    a3= Setting(0)

    scanmin = Setting(-60.0)
    scanmax = Setting(60.0)

    unis = Setting(0)

    nscan = Setting(0)
    invert = Setting(1)

    column = Setting(0)

    alphamax = Setting(1e+8)

    profile = Setting("")

    def __init__(self):
        self.setFixedWidth(1200)
        self.setFixedHeight(700)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "GID_SL Request Form", addSpace=True, orientation="vertical",
                                         width=400, height=630)

        central_tabs = gui.tabWidget(left_box_1)
        tab_template = gui.createTabPage(central_tabs, "Template Options")
        tab_input = gui.createTabPage(central_tabs, "Input Options")

        left_box_1_1 = oasysgui.widgetBox(tab_template, "", addSpace=True, orientation="vertical", width=370, height=620)

        gui.comboBox(left_box_1_1, self, "template_type", label="Template Type", labelWidth=100,
                     items=["Simplified (coplanar geometries only)", "Full"],
                     callback=self.set_TemplateType, sendSelectedValue=False, orientation="horizontal")

        self.simplified_box = oasysgui.widgetBox(left_box_1_1, "", addSpace=False, orientation="horizontal", width=380, height=220)

        gui.radioButtons(self.simplified_box, self, "simplified_form",
                         ["Symmetric Bragg diffraction from perfect crystals",
                          "Symmetric Bragg diffraction from multilayers and\nsuperlattices",
                          "Symmetric Bragg diffraction at Bragg angle of 90 degrees\n(\"back diffraction\")",
                          "Energy scanning of symmetric Bragg diffraction peaks"],
                         callback=self.set_SimplifiedForm)

        self.full_box = oasysgui.widgetBox(left_box_1_1, "", addSpace=False, orientation="horizontal", width=380, height=220)

        gui.radioButtons(self.full_box, self, "full_form",
                         ["Symmetric Bragg diffraction from perfect crystals",
                          "Symmetric Bragg diffraction from multilayers and\nsuperlattices",
                          "Coplanar extremely asymmetric diffraction of synchrotron\nradiation",
                          "Grazing incidence (\"surface\") diffraction from perfect\ncrystals",
                          "Grazing incidence (\"surface\") diffraction from multilayers\nin the scheme with position sensitive detector (PSD)",
                          "Non-coplanar Bragg-Laue diffraction from crystals with a\nfew degrees surface miscut"],
                         callback=self.set_FullForm)

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # -------------------------------------------------------------

        left_box_2 = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370, height=60)

        left_box_2_1 = oasysgui.widgetBox(left_box_2, "", addSpace=True, orientation="horizontal", width=370, height=30)

        gui.comboBox(left_box_2_1, self, "xway", label="X-rays specified by", labelWidth=120,
                     items=["Wavelength (Å)", "Energy (keV)", "Bragg angle (deg)", "X-ray line"],
                     callback=self.set_xway, sendSelectedValue=False, orientation="horizontal")

        self.box_wave = oasysgui.widgetBox(left_box_2_1, "", addSpace=False, orientation="horizontal", width=100)
        gui.lineEdit(self.box_wave, self, "wave", label="", labelWidth=0, addSpace=False, valueType=float, orientation="horizontal")

        self.box_line = oasysgui.widgetBox(left_box_2_1, "", addSpace=False, orientation="horizontal", width=100)
        XRayServerGui.combobox_text(self.box_line, self, "line", label="", labelWidth=0,
                               items=self.get_lines(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.line)

        button = gui.button(self.box_line, self, "?", callback=self.help_lines)
        button.setFixedWidth(15)

        self.set_xway()

        gui.comboBox(left_box_2, self, "ipol", label="Polarization", labelWidth=250,
                     items=["Sigma", "Pi", "Mixed"], sendSelectedValue=False, orientation="horizontal")



        left_box_3 = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370, height=60)

        left_box_3_1 = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="horizontal", width=370)
        XRayServerGui.combobox_text(left_box_3_1, self, "code", label="Crystal", labelWidth=40,
                               items=self.get_crystals(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.code)


        button = gui.button(left_box_3_1, self, "?", callback=self.help_crystals)
        button.setFixedWidth(15)

        gui.comboBox(left_box_3_1, self, "df1df2", label="", labelWidth=0,
                     items=["Auto DB for f\', f\'\'",
                            "X0h data (0.5-2.5 A)",
                            "Henke (0.4-1200 A)",
                            "Brennan (0.02-400 A)"],
                     sendSelectedValue=False, orientation="horizontal")

        left_box_3_2 = oasysgui.widgetBox(left_box_3, "", addSpace=True, orientation="horizontal", width=370)

        gui.lineEdit(left_box_3_2, self, "sigma", label="Sigma", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_3_2, self, "w0", label="A      W0", labelWidth=50, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_3_2, self, "wh", label="        Wh", labelWidth=50, addSpace=False, valueType=float, orientation="horizontal")

        left_box_4 = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="horizontal", width=370, height=60)

        left_box_4_1 = oasysgui.widgetBox(left_box_4, "", addSpace=True, orientation="horizontal", width=190)

        gui.lineEdit(left_box_4_1, self, "i1", label="Bragg Reflection", labelWidth=97, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4_1, self, "i2", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4_1, self, "i3", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        left_box_4_2 = oasysgui.widgetBox(left_box_4, "", addSpace=True, orientation="horizontal", width=178)

        gui.lineEdit(left_box_4_2, self, "daa", label="  Substrate da/a", labelWidth=95, addSpace=False, valueType=float, orientation="horizontal")

        self.simplified_input_box = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370)

        gui.comboBox(self.simplified_input_box, self, "igie", label="Geometry specified by", labelWidth=150,
                     items=["angle of Bragg planes to surface ('+' for g0>gh)",
                            "incidence angle of K0",
                            "exit angle of Kh",
                            "asymmetry factor beta=g0/gh"],
                     callback=self.set_igie_s, sendSelectedValue=False, orientation="horizontal")

        simplified_input_box_1 = oasysgui.widgetBox(self.simplified_input_box, "", addSpace=True, orientation="horizontal", width=370)

        gui.lineEdit(simplified_input_box_1, self, "fcentre", label="Value", labelWidth=50, addSpace=False, valueType=float, orientation="horizontal")

        self.unic_combo_s = gui.comboBox(simplified_input_box_1, self, "unic", label=" ", labelWidth=1,
                                       items=[" ",
                                              "degr.",
                                              "min.",
                                              "mrad.",
                                              "sec.",
                                              "urad"],
                                       sendSelectedValue=False, orientation="horizontal")

        self.set_igie_s()

        self.full_input_box = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370)

        box_top = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370)

        gui.label(box_top, self, "Top layer profile (optional):\nperiod=\nt= sigma= da/a= code= x= code2= x2= code3= x3= code4= \\\nx0= xh= xhdf= w0= wh=\nend period")

        self.profile_area = QtGui.QTextEdit()
        self.profile_area.setMaximumHeight(150)
        self.profile_area.setMaximumWidth(370)
        box_top.layout().addWidget(self.profile_area)

        gui.label(box_top, self, "Available Codes:")

        box_top_labels = oasysgui.widgetBox(box_top, "", addSpace=True, orientation="horizontal", width=370)

        gui.label(box_top_labels, self, "Crystals")
        gui.label(box_top_labels, self, "Non-Crystals")
        gui.label(box_top_labels, self, "Elements")

        box_top_1 = oasysgui.widgetBox(box_top, "", addSpace=True, orientation="horizontal", width=370)

        crystals_area = QtGui.QTextEdit()
        crystals_area.setMaximumHeight(80)
        crystals_area.setMaximumWidth(120)
        crystals_area.setText("\n".join(ListUtility.get_list("crystals")))
        crystals_area.setReadOnly(True)

        non_crystals_area = QtGui.QTextEdit()
        non_crystals_area.setMaximumHeight(80)
        non_crystals_area.setMaximumWidth(120)
        non_crystals_area.setText("\n".join(ListUtility.get_list("amorphous")))
        non_crystals_area.setReadOnly(True)

        elements_area = QtGui.QTextEdit()
        elements_area.setMaximumHeight(80)
        elements_area.setMaximumWidth(120)
        elements_area.setText("\n".join(ListUtility.get_list("atoms")))
        elements_area.setReadOnly(True)

        box_top_1.layout().addWidget(crystals_area)
        box_top_1.layout().addWidget(non_crystals_area)
        box_top_1.layout().addWidget(elements_area)

        # -----------------------------------------------------------

        self.set_TemplateType(change_values=False)

        button = gui.button(self.controlArea, self, "Submit Query!", callback=self.submit)
        button.setFixedHeight(30)

        gui.rubber(self.controlArea)

        self.tabs = []
        self.tabs_widget = gui.tabWidget(self.mainArea)
        self.initializeTabs()

        self.profile_area.textChanged.connect(self.set_profile)

    def set_profile(self):
        self.profile = self.profile_area.toPlainText()

    def set_TemplateType(self, change_values=True):
        if self.template_type == 0:
            self.simplified_box.setVisible(True)
            self.full_box.setVisible(False)
            self.simplified_input_box.setVisible(True)
            self.full_input_box.setVisible(False)
            self.set_SimplifiedForm(change_values)
        else:
            self.simplified_box.setVisible(False)
            self.full_box.setVisible(True)
            self.simplified_input_box.setVisible(False)
            self.full_input_box.setVisible(True)
            self.set_FullForm(change_values)

    def set_SimplifiedForm(self, change_values=True):
        if change_values:
            self.xway=0
            self.ipol=0
            self.df1df2 = 0
            self.sigma = 0.0
            self.w0 = 1.0
            self.wh = 1.0
            self.daa = 0.0
            self.fcentre = 0.0
            self.igie = 0
            self.unic = 1
            self.profile_area.setText("")

        if self.simplified_form==0:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 1
                self.i2 = 1
                self.i3 = 1

        elif self.simplified_form==1:
            if change_values:
                self.wave=1.540562
                self.code = "GaAs"
                self.i1 = 4
                self.i2 = 0
                self.i3 = 0
                self.profile_area.setText("period=20\nt=100 code=GaAs sigma=2\nt=70 code=AlAs sigma=2 da/a=a\nend period")

        elif self.simplified_form==2:
            if change_values:
                self.xway=1
                self.wave=13.934425
                self.code = "Diamond"
                self.i1 = 8
                self.i2 = 0
                self.i3 = 0

        elif self.simplified_form==3:
            if change_values:
                self.xway=2
                self.wave=89.0
                self.code = "Diamond"
                self.i1 = 8
                self.i2 = 0
                self.i3 = 0
                self.igie = 3

        self.set_xway()
        self.set_igie_s()


    def set_FullForm(self, change_values=True):
        if change_values:
            self.xway=0
            self.ipol=0
            self.df1df2 = 0
            self.sigma = 0.0
            self.w0 = 1.0
            self.wh = 1.0
            self.daa = 0.0
            self.profile_area.setText("")

        if self.full_form==0:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 1
                self.i2 = 1
                self.i3 = 1

        elif self.full_form==1:
            if change_values:
                self.wave=1.540562
                self.code = "GaAs"
                self.i1 = 4
                self.i2 = 0
                self.i3 = 0
                self.profile_area.setText("period=20\nt=100 code=GaAs sigma=2\nt=70 code=AlAs sigma=2 da/a=a\nend period")

        elif self.full_form==2:
            if change_values:
                self.xway=1
                self.wave=8.3
                self.code = "Germanium"
                self.i1 = 1
                self.i2 = 1
                self.i3 = 1

        elif self.full_form==3:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 1
                self.i2 = 1
                self.i3 = 1

        elif self.full_form==4:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 2
                self.i2 = 2
                self.i3 = 0

        elif self.full_form==5:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 2
                self.i2 = -2
                self.i3 = 0

        self.set_xway()
        self.set_igie_f()



    def set_xway(self):
        self.box_wave.setVisible(self.xway!=3)
        self.box_line.setVisible(self.xway==3)

    def set_igie_s(self):
        self.unic_combo_s.setEnabled(self.igie != 3)
        if self.igie == 3: self.unic = 0

    def set_igie_f(self):
        self.unic_combo_f.setEnabled(self.igie != 3)
        if self.igie == 3: self.unic = 0

    def initializeTabs(self):
        current_tab = self.tabs_widget.currentIndex()

        size = len(self.tabs)

        for index in range(0, size):
            self.tabs_widget.removeTab(size-1-index)

        self.tabs = [gui.createTabPage(self.tabs_widget, "Diffraction Intensity"),]

        for tab in self.tabs:
            tab.setFixedHeight(650)
            tab.setFixedWidth(750)

        self.plot_canvas = [None]

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

            data = self.extract_plots(response)

            self.send("GIS_SL_Result", data)

        except urllib.error.HTTPError as e:
            self.x0h_output.setHtml('The server couldn\'t fulfill the request.\nError Code: '
                                    + str(e.code) + "\n\n" +
                                    server.BaseHTTPRequestHandler.responses[e.code][1])
        except urllib.error.URLError as e:
            self.x0h_output.setHtml('We failed to reach a server.\nReason: '
                                    + e.reason)
        except Exception as e:
            self.x0h_output.setHtml('We failed to reach a server.\nReason: '
                                    + str(e))

        self.setStatusMessage("")
        self.progressBarFinished()



    def checkFields(self):
        pass

    def decode_df1df2(self):
        if self.df1df2 == 0: return "-1"
        elif self.df1df2 == 1: return "0"
        elif self.df1df2 == 2: return "2"
        elif self.df1df2 == 3: return "4"

    def decode_igie(self):
        if self.igie == 0: return "6"
        elif self.igie == 1: return "7"
        elif self.igie == 2: return "8"
        elif self.igie == 3: return "9"

    def extract_plots(self, response):

        self.setStatusMessage("Plotting Results")

        x_1, y_1 = self.get_data_file_from_response(response)

        self.plot_histo(x_1, y_1, 80, 0, "X-ray Diffraction Profile", "Scan Angle [" + self.unis +"]", "Diffracted Intensity")

        return [x_1, y_1]


    def get_data_file_from_response(self, response):
        rows = response.split("\n")

        job_id = None
        data = None

        for row in rows:
            if "Job ID" in row:
                job_id = (row.split("<b>"))[1].split("</b>")[0]

            if not job_id is None:
                if job_id+".dat" in row:
                    data = HttpManager.send_xray_server_direct_request((row.split("href=\"")[1]).split("\"")[0])

        if not data is None:
            rows = data.split("\r\n")

            x = []
            y = []

            for row in rows:
                temp = row.strip().split(" ")

                if len(temp) > 1:
                    x.append(float(temp[0].strip()))
                    y.append(float(temp[len(temp)-1].strip()))

            return x, y
        else:
            return None, None

    def plot_histo(self, x, y, progressBarValue, plot_canvas_index, title="", xtitle="", ytitle=""):
        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = PlotWindow(roi=False, control=False, position=False, plugins=False)
            self.plot_canvas[plot_canvas_index].setDefaultPlotLines(True)
            self.plot_canvas[plot_canvas_index].setActiveCurveColor(color='darkblue')
            self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(True)

            self.tabs[plot_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        XRayServerPlot.plot_histo(self.plot_canvas[plot_canvas_index], x, y, title, xtitle, ytitle)

        self.progressBarSet(progressBarValue)



    ''' ---------------------------------------------------------------------
        ---------------------------------------------------------------------
        ---------------------------------------------------------------------'''

    def get_lines(self):
        return ListUtility.get_list("waves")

    def help_lines(self):
        ShowTextDialog.show_text("Help Waves", ListUtility.get_help("waves"), width=350, parent=self)

    def get_crystals(self):
        return ListUtility.get_list("crystals")

    def help_crystals(self):
        ShowTextDialog.show_text("Help Crystals", ListUtility.get_help("crystals"), parent=self)

    def get_others(self):
        return ListUtility.get_list("amorphous+atoms")

    def help_others(self):
        ShowTextDialog.show_text("Help Others", ListUtility.get_help("amorphous+atoms"), parent=self)

    def set_Rho(self):
        if not self.chem is None:
            if not self.chem.strip() == "":
                self.chem = self.chem.strip()
                self.rho = XRayServerPhysics.getMaterialDensity(self.chem)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = X0h()
    w.show()
    app.exec()
    w.saveSettings()



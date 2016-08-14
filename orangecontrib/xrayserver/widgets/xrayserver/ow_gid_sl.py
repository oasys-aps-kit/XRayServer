__author__ = "Luca Rebuffi"

from oasys.widgets import widget
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

import urllib
from http import server

from orangecontrib.xrayserver.util.xrayserver_util import HttpManager, ShowTextDialog, ShowHtmlDialog, XRayServerGui
from orangecontrib.xrayserver.widgets.xrayserver.list_utility import ListUtility
from orangecontrib.xrayserver.widgets.gui.ow_xrayserver_widget import XrayServerWidget, XrayServerException

from PyQt4 import QtGui

APPLICATION = "/cgi/GID_form.pl"

class GID_SL(XrayServerWidget):
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

    xway = Setting(0)
    wave = Setting(1.540562)
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
    a1= Setting(0)
    a2= Setting(0)
    a3= Setting(0)
    scanmin = Setting(-60.0)
    scanmax = Setting(60.0)
    unis = Setting(3)
    nscan = Setting(401)
    invert = Setting(0)
    axis = Setting(0)
    column = Setting(0)
    alphamax = Setting(1e+8)
    profile = Setting("")

    def __init__(self):
        self.setFixedWidth(1200)
        self.setFixedHeight(700)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "GID_SL Request Form", addSpace=False, orientation="vertical",
                                         width=400, height=650)

        self.central_tabs = gui.tabWidget(left_box_1)
        tab_template = gui.createTabPage(self.central_tabs, "Template Options")
        tab_input = gui.createTabPage(self.central_tabs, "Input Options")

        left_box_1_1 = oasysgui.widgetBox(tab_template, "", addSpace=False, orientation="vertical", width=370, height=640)

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

        left_box_2 = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370)

        gui.separator(left_box_2)

        left_box_2_1 = oasysgui.widgetBox(left_box_2, "", addSpace=False, orientation="horizontal", width=370)

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


        # -------------------------------------------------------------

        left_box_3 = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=370)

        left_box_3_1 = oasysgui.widgetBox(left_box_3, "", addSpace=False, orientation="horizontal", width=370)
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

        left_box_3_2 = oasysgui.widgetBox(left_box_3, "", addSpace=False, orientation="horizontal", width=370)

        gui.lineEdit(left_box_3_2, self, "sigma", label="Sigma", labelWidth=80, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_3_2, self, "w0", label="A      W0", labelWidth=50, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(left_box_3_2, self, "wh", label="        Wh", labelWidth=50, addSpace=False, valueType=float, orientation="horizontal")

        # -------------------------------------------------------------

        left_box_4 = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="horizontal", width=370)

        left_box_4_1 = oasysgui.widgetBox(left_box_4, "", addSpace=False, orientation="horizontal", width=190)

        gui.lineEdit(left_box_4_1, self, "i1", label="Bragg Reflection", labelWidth=97, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4_1, self, "i2", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")
        gui.lineEdit(left_box_4_1, self, "i3", label=" ", labelWidth=1, addSpace=False, valueType=int, orientation="horizontal")

        left_box_4_2 = oasysgui.widgetBox(left_box_4, "", addSpace=False, orientation="horizontal", width=178)

        gui.lineEdit(left_box_4_2, self, "daa", label="  Substrate da/a", labelWidth=95, addSpace=False, valueType=float, orientation="horizontal")

        # -------------------------------------------------------------
        # -------------------------------------------------------------

        self.simplified_input_box = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=370)

        gui.comboBox(self.simplified_input_box, self, "igie", label="Geom. by", labelWidth=60,
                     items=["angle of Bragg planes to surface ('+' for g0>gh)",
                            "incidence angle of K0",
                            "exit angle of Kh",
                            "asymmetry factor beta=g0/gh"],
                     callback=self.set_igie_s, sendSelectedValue=False, orientation="horizontal")

        simplified_input_box_1 = oasysgui.widgetBox(self.simplified_input_box, "", addSpace=False, orientation="horizontal", width=370)

        gui.lineEdit(simplified_input_box_1, self, "fcentre", label="Value", labelWidth=180, addSpace=False, valueType=float, orientation="horizontal")

        self.unic_combo_s = gui.comboBox(simplified_input_box_1, self, "unic", label=" ", labelWidth=1,
                                       items=[" ",
                                              "degr.",
                                              "min.",
                                              "mrad.",
                                              "sec.",
                                              "urad"],
                                       sendSelectedValue=False, orientation="horizontal")

        self.set_igie_s()

        simplified_input_box_2 = oasysgui.widgetBox(self.simplified_input_box, "", addSpace=False, orientation="horizontal", width=370)

        gui.lineEdit(simplified_input_box_2, self, "scanmin", label="Scan: From", labelWidth=70, addSpace=False, valueType=float, orientation="horizontal")
        gui.lineEdit(simplified_input_box_2, self, "scanmax", label="To", labelWidth=15, addSpace=False, valueType=float, orientation="horizontal")

        self.simplified_input_box_scan_1_1 = oasysgui.widgetBox(simplified_input_box_2, "", addSpace=False, orientation="horizontal")

        gui.comboBox(self.simplified_input_box_scan_1_1, self, "unis", label=" ", labelWidth=1,
                     items=["degr.",
                            "min.",
                            "mrad.",
                            "sec.",
                            "urad"],
                     sendSelectedValue=False, orientation="horizontal")

        gui.lineEdit(self.simplified_input_box_scan_1_1, self, "nscan", label="Points", labelWidth=40, addSpace=False, valueType=int, orientation="horizontal")

        self.simplified_input_box_scan_1_2 = oasysgui.widgetBox(self.simplified_input_box, "", addSpace=False, orientation="horizontal", width=370)

        gui.checkBox(self.simplified_input_box_scan_1_2, self, "invert", "Invert axis", labelWidth=90)
        gui.comboBox(self.simplified_input_box_scan_1_2, self, "column", label="Plot argument", labelWidth=90,
                                       items=["scan angle",
                                              "incidence angle",
                                              "exit angle"],
                                       sendSelectedValue=False, orientation="horizontal")

        self.simplified_input_box_scan_2_1 = oasysgui.widgetBox(simplified_input_box_2, "", addSpace=False, orientation="horizontal")

        self.unis_combo_s = gui.comboBox(self.simplified_input_box_scan_2_1, self, "unis", label=" ", labelWidth=1,
                                         items=["degr.",
                                                "min.",
                                                "mrad.",
                                                "sec.",
                                                "urad",
                                                "eV"],
                                         sendSelectedValue=False, orientation="horizontal")

        gui.lineEdit(self.simplified_input_box_scan_2_1, self, "nscan", label="Points", labelWidth=40, addSpace=False, valueType=int, orientation="horizontal")

        self.simplified_input_box_scan_2_2 = oasysgui.widgetBox(self.simplified_input_box, "", addSpace=False, orientation="horizontal")

        gui.comboBox(self.simplified_input_box_scan_2_2, self, "axis", label="Scan Type", labelWidth=150,
                     items=["[k0 x h]",
                            "Energy (eV)",
                            "Energy (eV), no X0h recalc"],
                     sendSelectedValue=False, orientation="horizontal", callback=self.set_scan_type_s)

        self.set_scan_type_s()

        # -------------------------------------------------------------
        # -------------------------------------------------------------

        self.full_input_box = oasysgui.widgetBox(tab_input, "", addSpace=True, orientation="vertical", width=370)

        # -------------------------------------------------------------

        box_alpha = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="horizontal", width=280)

        self.le_alphamax = gui.lineEdit(box_alpha, self, "alphamax", label="Approximations: alpha_max", labelWidth=170, addSpace=False, valueType=float, orientation="horizontal")
        gui.label(box_alpha, self, "*|xh|")

        # -------------------------------------------------------------

        box_top = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=370)

        box_top_0 = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=250)

        gui.label(box_top_0, self, "Top layer profile (optional):")

        button = gui.button(box_top_0, self, "?", callback=self.help_profile)
        button.setFixedWidth(25)

        gui.label(box_top_0, self, "(sintax)")

        self.profile_area = QtGui.QTextEdit()
        self.profile_area.setMaximumHeight(170)
        self.profile_area.setMaximumWidth(370)
        box_top.layout().addWidget(self.profile_area)

        gui.label(box_top, self, "Available Codes:")

        box_top_labels = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=370)

        gui.label(box_top_labels, self, "Crystals")
        gui.label(box_top_labels, self, "Non-Crystals")
        gui.label(box_top_labels, self, "Elements")

        box_top_1 = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=370)

        crystals_area = QtGui.QTextEdit()
        crystals_area.setMaximumHeight(100)
        crystals_area.setMaximumWidth(120)
        crystals_area.setText("\n".join(ListUtility.get_list("crystals")))
        crystals_area.setReadOnly(True)

        non_crystals_area = QtGui.QTextEdit()
        non_crystals_area.setMaximumHeight(100)
        non_crystals_area.setMaximumWidth(120)
        non_crystals_area.setText("\n".join(ListUtility.get_list("amorphous")))
        non_crystals_area.setReadOnly(True)

        elements_area = QtGui.QTextEdit()
        elements_area.setMaximumHeight(100)
        elements_area.setMaximumWidth(120)
        elements_area.setText("\n".join(ListUtility.get_list("atoms")))
        elements_area.setReadOnly(True)

        box_top_1.layout().addWidget(crystals_area)
        box_top_1.layout().addWidget(non_crystals_area)
        box_top_1.layout().addWidget(elements_area)

        # -----------------------------------------------------------


        button = gui.button(self.controlArea, self, "Submit Query!", callback=self.submit)
        button.setFixedHeight(30)

        gui.rubber(self.controlArea)

        self.tabs = []
        self.tabs_widget = gui.tabWidget(self.mainArea)
        self.initializeTabs()

        self.set_TemplateType(change_values=False)

        self.profile_area.textChanged.connect(self.set_profile)
        self.le_alphamax.focusOutEvent = self.alphamax_focusOutEvent
        self.alphamax_focusOutEvent(None)

    def set_profile(self):
        self.profile = self.profile_area.toPlainText()

    def alphamax_focusOutEvent(self, event):
        try:
            XRayServerGui.format_scientific(self.le_alphamax)
        except:
            pass

        if event: QtGui.QLineEdit.focusOutEvent(self.le_alphamax, event)

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

        self.simplified_input_box_scan_1_1.setVisible(self.simplified_form != 3)
        self.simplified_input_box_scan_1_2.setVisible(self.simplified_form != 3)
        self.simplified_input_box_scan_2_1.setVisible(self.simplified_form == 3)
        self.simplified_input_box_scan_2_2.setVisible(self.simplified_form == 3)

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
            self.nscan = 401
            self.invert = 0
            self.column = 0
            self.axis = 0
            self.alphamax = 1e8

            self.profile_area.setText("")

        if self.simplified_form==0:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"
                self.i1 = 1
                self.i2 = 1
                self.i3 = 1
                self.scanmin=-60.0
                self.scanmax=60.0
                self.unis = 3

        elif self.simplified_form==1:
            if change_values:
                self.wave=1.540562
                self.code = "GaAs"
                self.i1 = 4
                self.i2 = 0
                self.i3 = 0
                self.scanmin=-2000.0
                self.scanmax=2000.0
                self.unis = 3
                self.column = 1
                self.profile_area.setText("period=20\nt=100 code=GaAs sigma=2\nt=70 code=AlAs sigma=2 da/a=a\nend period")

        elif self.simplified_form==2:
            if change_values:
                self.xway=1
                self.wave=13.934425
                self.code = "Diamond"
                self.i1 = 8
                self.i2 = 0
                self.i3 = 0
                self.scanmin=-30.0
                self.scanmax=30.0
                self.unis = 1

        elif self.simplified_form==3:
            if change_values:
                self.xway=2
                self.wave=89.0
                self.code = "Diamond"
                self.i1 = 8
                self.i2 = 0
                self.i3 = 0
                self.scanmin=-1.0
                self.scanmax=1.0
                self.nscan = 501
                self.axis = 1
                self.set_scan_type_s()

        self.set_xway()
        self.set_igie_s()

        self.alphamax_focusOutEvent(None)

        self.central_tabs.setCurrentPage(1)


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

        self.central_tabs.setCurrentPage(1)

    def set_xway(self):
        self.box_wave.setVisible(self.xway!=3)
        self.box_line.setVisible(self.xway==3)

    def set_igie_s(self):
        self.unic_combo_s.setEnabled(self.igie != 3)
        if self.igie == 3: self.unic = 0
        else: self.unic = 1

    def set_scan_type_s(self):
        self.unis_combo_s.setEnabled(self.axis==0)
        if self.axis != 0: self.unis = 5
        else: self.unis = 3

    def set_igie_f(self):
        self.unic_combo_f.setEnabled(self.igie != 3)
        if self.igie == 3: self.unic = 0

    def help_profile(self):
        ShowTextDialog.show_text("Top Layer Profile Sintax",
                                 "period=\nt= sigma= da/a= code= x= code2= x2= code3= x3= code4= x0= xh= xhdf= w0= wh=\nend period",
                                 height=150, parent=self)

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

        parameters.update({"xway" : self.decode_xway()})
        parameters.update({"wave" : str(self.wave)})
        parameters.update({"line" : self.line})
        parameters.update({"ipol" : str(self.ipol + 1)})
        parameters.update({"code" : self.code})
        parameters.update({"df1df2" : self.decode_df1df2()})
        parameters.update({"sigma" : str(self.sigma)})
        parameters.update({"w0" : str(self.w0)})
        parameters.update({"wh" : str(self.wh)})
        parameters.update({"i1" : str(self.i1)})
        parameters.update({"i2" : str(self.i2)})
        parameters.update({"i3" : str(self.i3)})
        parameters.update({"daa" : str(self.daa)})
        parameters.update({"igie" : self.decode_igie()})
        parameters.update({"fcentre" : str(self.fcentre)})
        parameters.update({"unic" : str(self.unic - 1)})
        parameters.update({"n1" : str(self.n1)})
        parameters.update({"n2" : str(self.n2)})
        parameters.update({"n3" : str(self.n3)})
        parameters.update({"m1" : str(self.m1)})
        parameters.update({"m2" : str(self.m2)})
        parameters.update({"m3" : str(self.m3)})
        parameters.update({"miscut" : str(self.miscut)})
        parameters.update({"unim" : str(self.unim)})
        parameters.update({"a1" : str(self.a1)})
        parameters.update({"a2" : str(self.a2)})
        parameters.update({"a3" : str(self.a3)})
        parameters.update({"scanmin" : str(self.scanmin)})
        parameters.update({"scanmax" : str(self.scanmax)})
        parameters.update({"unis" : str(self.unis)})
        parameters.update({"nscan" : str(self.nscan)})
        parameters.update({"invert" : str(self.invert)})
        parameters.update({"axis" : self.decode_axis()})
        parameters.update({"column" : self.decode_column()})
        parameters.update({"alphamax" : str(self.alphamax)})
        parameters.update({"profile" : self.profile})

        try:
            response = HttpManager.send_xray_server_request_POST(APPLICATION, parameters)
            data = self.extract_plots(response)

            self.send("GID_SL_Result", data)

        except urllib.error.HTTPError as e:
            ShowTextDialog.show_text("Error", 'The server couldn\'t fulfill the request.\nError Code: '
                                     + str(e.code) + "\n\n" +
                                     server.BaseHTTPRequestHandler.responses[e.code][1], parent=self)
        except urllib.error.URLError as e:
            ShowTextDialog.show_text("Error", 'We failed to reach a server.\nReason: ' + e.reason, parent=self)
        except XrayServerException as e:
            ShowHtmlDialog.show_html("X-ray Server Error", e.response, width=750, height=500, parent=self)
        except Exception as e:
            ShowTextDialog.show_text("Error", 'Error Occurred.\nReason: ' + str(e), parent=self)

        self.setStatusMessage("")
        self.progressBarFinished()


    def checkFields(self):
        pass

    def decode_xway(self):
        if self.xway == 0: return "1"
        elif self.xway == 1: return "2"
        elif self.xway == 2: return "4"
        elif self.xway == 3: return "3"

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

    def decode_column(self):
        if self.column == 0: return "A"
        elif self.column == 1: return "I"
        elif self.column == 2: return "E"

    def decode_axis(self):
        if self.axis == 0: return "4"
        elif self.axis == 1: return "7"
        elif self.axis == 2: return "8"

    def extract_plots(self, response):

        self.setStatusMessage("Plotting Results")

        x_1, y_1 = self.get_data_file_from_response(response)

        self.plot_histo(x_1, y_1, 80, 0, 0, "X-ray Diffraction Profile", "Choosen Scan Variable", "Diffracted Intensity")

        return [x_1, y_1]


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = GID_SL()
    w.show()
    app.exec()
    w.saveSettings()



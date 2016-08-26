__author__ = "Luca Rebuffi"

import numpy

from PyQt4.QtGui import QImage, QLabel, QPixmap

import orangecanvas.resources as resources
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets.exchange import DataExchangeObject

import urllib
from http import server

from orangecontrib.xrayserver.util.xrayserver_util import HttpManager, ShowTextDialog, ShowHtmlDialog, XRayServerGui
from orangecontrib.xrayserver.widgets.xrayserver.list_utility import ListUtility
from orangecontrib.xrayserver.widgets.gui.ow_xrayserver_widget import XrayServerWidget, XrayServerException

from PyQt4 import QtGui

APPLICATION = "/cgi/TER_form.pl"

class TER_SL(XrayServerWidget):
    name = "TER_SL"
    description = "TER_SL"
    icon = "icons/tersl.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 4
    category = "TER_SL"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 1

    outputs = [{"name": "xrayserver_data",
                "type": DataExchangeObject,
                "doc": "xrayserver_data",
                "id": "xrayserver_data"}, ]

    ter_sl_form = Setting(0)

    xway = Setting(0)
    wave = Setting(1.540562)
    line = Setting("Cu-Ka1")
    ipol = Setting(0)

    subway = Setting(0)

    code = Setting("Germanium")
    df1df2 = Setting(0)
    chem = Setting("")
    rho = Setting(0.0)

    x0 = Setting(0.0)
    w0 = Setting(1.0)
    sigma = Setting(4.0)
    tr = Setting(0.0)


    def __init__(self):
        self.setFixedWidth(1200)
        self.setFixedHeight(700)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "TER_SL Request Form", addSpace=False, orientation="vertical",
                                         width=500, height=680)

        self.central_tabs = gui.tabWidget(left_box_1)
        tab_template = gui.createTabPage(self.central_tabs, "Template Options")
        tab_input = gui.createTabPage(self.central_tabs, "Input Options")

        left_box_1_1 = oasysgui.widgetBox(tab_template, "", addSpace=False, orientation="vertical", width=480, height=670)

        gui.separator(left_box_1_1)

        ter_sl_box = oasysgui.widgetBox(left_box_1_1, "", addSpace=False, orientation="horizontal", width=470, height=220)

        gui.radioButtons(ter_sl_box, self, "ter_sl_form",
                         ["Specular reflection from perfect reflectors",
                          "Specular reflection from multilayers",
                          "Specular reflection from perfect reflectors + standing waves",
                          "Specular reflection from multilayers + standing waves"],
                         callback=self.set_TerSLForm)

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # -------------------------------------------------------------

        gui.separator(tab_input)

        left_box_2 = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=470)


        left_box_2_1 = oasysgui.widgetBox(left_box_2, "", addSpace=False, orientation="horizontal", width=470)

        gui.comboBox(left_box_2_1, self, "xway", label="X-rays specified by",
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

        gui.comboBox(left_box_2_1, self, "ipol", label="Polarization",
                     items=["Sigma", "Pi", "Mixed"], sendSelectedValue=False, orientation="horizontal")


        # -------------------------------------------------------------

        left_box_3 = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=470)

        left_box_3_top = oasysgui.widgetBox(left_box_3, "", addSpace=False, orientation="horizontal", width=470)
        gui.label(left_box_3_top, self, "Substrate:")

        left_box_3_content = oasysgui.widgetBox(left_box_3, "", addSpace=False, orientation="horizontal", width=470)

        left_box_3_left = oasysgui.widgetBox(left_box_3_content, "", addSpace=False, orientation="horizontal", width=20)
        left_box_3_right = oasysgui.widgetBox(left_box_3_content, "", addSpace=False, orientation="vertical", width=445)

        gui.radioButtons(left_box_3_left, self, "subway", [" ", " ", " "], callback=self.set_subway)

        self.left_box_3_1 = oasysgui.widgetBox(left_box_3_right, "", addSpace=False, orientation="horizontal", width=445)
        XRayServerGui.combobox_text(self.left_box_3_1, self, "code", label="Crystal", labelWidth=45,
                               items=self.get_crystals(),
                               sendSelectedValue=True, orientation="horizontal", selectedValue=self.code)

        button = gui.button(self.left_box_3_1, self, "?", callback=self.help_crystals)
        button.setFixedWidth(15)

        gui.comboBox(self.left_box_3_1, self, "df1df2", label=" ", labelWidth=1,
                     items=["Auto DB for f\', f\'\'",
                            "X0h data (0.5-2.5 A)",
                            "Henke (0.4-1200 A)",
                            "Brennan (0.02-400 A)"],
                     sendSelectedValue=False, orientation="horizontal")

        self.left_box_3_2 = oasysgui.widgetBox(left_box_3_right, "", addSpace=False, orientation="horizontal", width=445)

        gui.lineEdit(self.left_box_3_2, self, "chem", label="Chemical Formula", addSpace=False, valueType=str, orientation="horizontal", callback=self.set_rho)
        gui.lineEdit(self.left_box_3_2, self, "rho", label=u"\u03C1" + " (g/cm3)", labelWidth=60, addSpace=False, valueType=float, orientation="horizontal")

        self.left_box_3_3 = oasysgui.widgetBox(left_box_3_right, "", addSpace=False, orientation="vertical", width=445)

        left_box_3_3_1 = oasysgui.widgetBox(self.left_box_3_3, "", addSpace=False, orientation="horizontal", width=445)

        gui.lineEdit(left_box_3_3_1, self, "x0", label="Susceptibility x0", labelWidth=100, addSpace=False, valueType=float, orientation="horizontal")
        gui.label(left_box_3_3_1, self, "format: x0=(Re(x0), Im(x0)); note: x0=2*delta", labelWidth=230 )

        left_box_3_3_2 = oasysgui.widgetBox(self.left_box_3_3, "", addSpace=False, orientation="horizontal", width=445)

        gui.lineEdit(left_box_3_3_2, self, "w0", label="x0 correction: w0", labelWidth=100, addSpace=False, valueType=float, orientation="horizontal")
        gui.label(left_box_3_3_2, self, "this is used as: x0 = w0 * x0", labelWidth=230)

        left_box_3_3_3 = oasysgui.widgetBox(self.left_box_3_3, "", addSpace=False, orientation="vertical", width=445)

        gui.lineEdit(left_box_3_3_3, self, "sigma", label="Roughness: sigma [Å]", labelWidth=100, addSpace=False, valueType=float, orientation="horizontal")
        gui.label(left_box_3_3_3, self, "      OR")
        gui.lineEdit(left_box_3_3_3, self, "tr", label="Transition layer tr [Å]", labelWidth=100, addSpace=False, valueType=float, orientation="horizontal")

        self.set_subway()

        # -------------------------------------------------------------

        left_box_4 = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="horizontal", width=470)

        left_box_4_1 = oasysgui.widgetBox(left_box_4, "", addSpace=False, orientation="horizontal", width=240)

        # -------------------------------------------------------------
        # -------------------------------------------------------------

        self.standing_waves_box = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="horizontal", width=470, height=30)
        self.standing_waves_box_hidden = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="horizontal", width=470, height=30)

        gui.label(self.standing_waves_box, self, "Standing waves:")

        gui.separator(tab_input)

        # -------------------------------------------------------------

        box_top = oasysgui.widgetBox(tab_input, "", addSpace=False, orientation="vertical", width=470)

        box_top_0 = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=470)

        box_top_0_1 = oasysgui.widgetBox(box_top_0, "", addSpace=False, orientation="vertical", width=100)

        gui.label(box_top_0_1, self, "Top layer profile\n(optional):")

        button = gui.button(box_top_0_1, self, "? (sintax)", callback=self.help_profile)
        button.setFixedWidth(90)

        box_top_0_2 = oasysgui.widgetBox(box_top_0, "", addSpace=False, orientation="horizontal", width=360)

        self.profile_area = QtGui.QTextEdit()
        self.profile_area.setMaximumHeight(110)
        self.profile_area.setMaximumWidth(360)
        box_top_0_2.layout().addWidget(self.profile_area)


        box_top_labels = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=470)

        box_top_labels_1 = oasysgui.widgetBox(box_top_labels, "", addSpace=False, orientation="horizontal", width=100)

        gui.label(box_top_labels_1, self, "Available Codes:")

        box_top_1 = oasysgui.widgetBox(box_top, "", addSpace=False, orientation="horizontal", width=470)

        oasysgui.widgetBox(box_top_1, "", addSpace=False, orientation="horizontal", width=100)
        box_top_1_2 = oasysgui.widgetBox(box_top_1, "", addSpace=False, orientation="horizontal", width=360)

        crystals_area = QtGui.QTextEdit()
        crystals_area.setMaximumHeight(100)
        crystals_area.setMaximumWidth(120)
        crystals_area.setText("\n".join(ListUtility.get_list("crystals")))
        crystals_area.setReadOnly(True)

        box_top_1_2.layout().addWidget(crystals_area)

        # -----------------------------------------------------------


        button = gui.button(tab_input, self, "Submit Query!", callback=self.submit)
        button.setFixedHeight(30)

        gui.rubber(self.controlArea)

        self.tabs = []
        self.tabs_widget = gui.tabWidget(self.mainArea)
        self.initializeTabs()

        self.profile_area.textChanged.connect(self.set_profile)

    def set_profile(self):
        self.profile = self.profile_area.toPlainText()

    def set_TerSLForm(self, change_values=True, switch_page=True):

        self.standing_waves_box.setVisible(self.ter_sl_form == 2 or self.ter_sl_form==3)
        self.standing_waves_box_hidden.setVisible(self.ter_sl_form < 2)

        if change_values:
            self.xway=0
            self.ipol=0
            self.df1df2 = 0
            self.sigma = 0.0

            self.profile_area.setText("")

        if self.ter_sl_form==0:
            if change_values:
                self.wave=1.540562
                self.code = "Germanium"

        elif self.ter_sl_form==1:
            if change_values:
                self.wave=1.540562
                self.code = "GaAs"
                self.profile_area.setText("period=20\nt=100 code=GaAs sigma=2\nt=70 code=AlAs sigma=2 da/a=a\nend period")

        elif self.ter_sl_form==2:
            if change_values:
                self.xway=1
                self.wave=13.934425
                self.code = "Diamond"

        elif self.ter_sl_form==3:
            if change_values:
                self.xway=2
                self.wave=89.0
                self.code = "Diamond"

        self.set_xway()

        if switch_page: self.central_tabs.setCurrentIndex(1)


    def set_xway(self):
        self.box_wave.setVisible(self.xway!=3)
        self.box_line.setVisible(self.xway==3)

    def set_subway(self):
        self.left_box_3_1.setEnabled(self.subway == 0)
        self.left_box_3_2.setEnabled(self.subway == 1)
        self.left_box_3_3.setEnabled(self.subway == 2)

    def set_rho(self):
        if not self.chem is None:
            if not self.chem.strip() == "":
                self.chem = self.chem.strip()
                self.rho = XRayServerPhysics.getMaterialDensity(self.chem)

    def help_profile(self):
        ShowTextDialog.show_text("Top Layer Profile Sintax",
                                 "period=\nt= sigma= da/a= code= x= code2= x2= code3= x3= code4= x0= xh= xhdf= w0= wh=\nend period",
                                 height=150, parent=self)

    def initializeTabs(self):
        current_tab = self.tabs_widget.currentIndex()

        size = len(self.tabs)

        for index in range(0, size):
            self.tabs_widget.removeTab(size-1-index)

        self.tabs = [gui.createTabPage(self.tabs_widget, "Reflectivity Plot"),
                     gui.createTabPage(self.tabs_widget, "Standing Waves Plot")]

        for tab in self.tabs:
            tab.setFixedHeight(650)
            tab.setFixedWidth(650)

        self.plot_canvas = [None, None]

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

        parameters.update({"profile" : self.profile})

        try:
            self.progressBarSet(10)

            response = HttpManager.send_xray_server_request_POST(APPLICATION, parameters)

            self.progressBarSet(50)

            data = self.extract_plots(response)

            exchange_data = DataExchangeObject("XRAYSERVER", "TER_SL")
            exchange_data.add_content("ter_sl_result", data)
            exchange_data.add_content("ter_sl_result_units_to_degrees", self.get_units_to_degrees())

            self.send("xrayserver_data", exchange_data)

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

    def decode_um(self):
        if self.unis == 0: return "degrees"
        elif self.unis == 1: return "arcmin"
        elif self.unis == 2: return "mrad"
        elif self.unis == 3: return "arcsec"
        elif self.unis == 4: return "urad"

    def get_units_to_degrees(self):
        if self.unis == 0: # degrees
            return 1.0
        elif self.unis == 1: #arcmin
            return 0.0166667
        elif self.unis == 2: #mrad
            return 57.2957795e-3
        elif self.unis == 3: # ARCSEC
            return 0.000277777805
        elif self.unis == 4: #urad
            return 57.2957795e-6
        else:
            return numpy.nan

    def extract_plots(self, response):

        self.setStatusMessage("Plotting Results")

        x_1, y_1 = self.get_data_file_from_response(response)

        self.plot_histo(x_1, y_1, 85, 0, 0, "Reflectivity", "Choosen Scan Variable", "Reflectivity")

        figure_url = self.extract_2D_image_from_response(response)

        self.plot_image(figure_url, 95, 1, 1)

        return [x_1, y_1]

    def extract_2D_image_from_response(self, response):
        rows = response.split("\n")

        job_id = None

        for row in rows:
            if "Job ID" in row:
                job_id = (row.split("<b>"))[1].split("</b>")[0]

            if not job_id is None:
                if not job_id+"_sw.png" in response:
                    return None
                else:
                    return (row.split("src=\"")[1]).split("\"")[0]

        if job_id is None:
            raise Exception("Job ID not present")

    def plot_image(self, image_url, progressBarValue, tabs_canvas_index, plot_canvas_index):

        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = QLabel(self.tabs[tabs_canvas_index])
            self.tabs[tabs_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        if image_url is None:
            image = QImage(resources.package_dirname("orangecontrib.xrayserver.widget.xrayserver.icons") + "/no_standing_waves_result.png")
        else:
            image = QImage()
            image.loadFromData(HttpManager.send_xray_server_direct_request(image_url, decode=False))

        self.plot_canvas[plot_canvas_index].setPixmap(QPixmap(image))

        self.progressBarSet(progressBarValue)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    w = TER_SL()
    w.show()
    app.exec()
    w.saveSettings()



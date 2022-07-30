import os
import sys
from orangewidget import gui
import xraylib
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView

import matplotlib

import urllib

XRAY_SERVER_URL = "https://x-server.gmca.aps.anl.gov"
TMP_FILE = "xrayserver_tmp.txt"

class HttpManager():

    @classmethod
    def send_xray_server_request_GET(cls, application, parameters):
        # this code prevent the real X-Ray Server to see Oasys as a bot.
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(XRAY_SERVER_URL + application + "?" + urllib.parse.urlencode(parameters), TMP_FILE)

        with open(TMP_FILE) as f:
            content = f.read()
            f.close()

        try: os.remove(TMP_FILE)
        except: pass

        return content

    @classmethod
    def send_xray_server_direct_request(cls, url, decode=True):
        resp = urllib.request.urlopen(url=XRAY_SERVER_URL+url)

        if decode: return resp.read().decode('ascii')
        else:      return resp.read()

class XRayServerPhysics:
    @classmethod
    def getMaterialDensity(cls, material_formula):
        if material_formula is None: return 0.0
        if str(material_formula.strip()) == "": return 0.0

        try:
            compoundData = xraylib.CompoundParser(material_formula)

            if compoundData["nElements"] == 1:
                return xraylib.ElementDensity(compoundData["Elements"][0])
            else:
                return 0.0
        except:
            return 0.0

class XRayServerGui:

    @classmethod
    def format_scientific(cls, lineedit):
        lineedit.setText("{:.2e}".format(float(lineedit.text().replace("+", ""))))


    @classmethod
    def combobox_text(cls, widget, master, value, box=None, label=None, labelWidth=None,
             orientation='vertical', items=(), callback=None,
             sendSelectedValue=False, valueType=str,
             control2attributeDict=None, emptyString=None, editable=False, selectedValue=None,
             **misc):

        combo = gui.comboBox(widget, master, value, box=box, label=label, labelWidth=labelWidth, orientation=orientation,
                             items=items, callback=callback, sendSelectedValue=sendSelectedValue, valueType=valueType,
                             control2attributeDict=control2attributeDict, emptyString=emptyString,editable=editable, **misc)
        try:
            combo.setCurrentIndex(items.index(selectedValue))
        except:
            pass

        return combo

class XRayServerPlot:

    @classmethod
    def plot_histo(cls, plot_window, x, y, title, xtitle, ytitle):
        matplotlib.rcParams['axes.formatter.useoffset']='False'

        plot_window.addCurve(x, y, title, symbol='', color='blue', replace=True) #'+', '^', ','
        if not xtitle is None: plot_window.setGraphXLabel(xtitle)
        if not ytitle is None: plot_window.setGraphYLabel(ytitle)
        if not title is None: plot_window.setGraphTitle(title)

        if min(y) < 0:
            plot_window.setGraphYLimits(1.01*min(y), max(y)*1.01)
        else:
            plot_window.setGraphYLimits(min(y), max(y)*1.01)
        plot_window.replot()

class ShowHtmlDialog(QtWidgets.QDialog):

    def __init__(self, title, html_text, width=650, height=400, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout(self)

        web_view = QWebView(self)
        web_view.setHtml(html_text)

        text_area = QtWidgets.QScrollArea(self)
        text_area.setWidget(web_view)
        text_area.setWidgetResizable(True)
        text_area.setFixedHeight(height)
        text_area.setFixedWidth(width)

        bbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        bbox.accepted.connect(self.accept)
        layout.addWidget(text_area)
        layout.addWidget(bbox)

    @classmethod
    def show_html(cls, title, html_text, width=650, height=400, parent=None):
        dialog = ShowHtmlDialog(title, html_text, width, height, parent)
        dialog.show()

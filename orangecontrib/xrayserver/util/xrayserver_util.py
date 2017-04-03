import sys
from orangewidget import gui
import xraylib

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib import figure as matfig
    import pylab
except ImportError:
    print(sys.exc_info()[1])
    pass

import urllib

XRAY_SERVER_URL = "http://x-server.gmca.aps.anl.gov"

class HttpManager():

    @classmethod
    def send_xray_server_request_POST(cls, application, parameters):
        data = urllib.parse.urlencode(parameters)
        data = data.encode('utf-8') # data should be bytes
        req = urllib.request.Request(XRAY_SERVER_URL + application, data)
        resp = urllib.request.urlopen(req)

        return resp.read().decode('ascii')

    @classmethod
    def send_xray_server_request_GET(cls, application, parameters):
        resp = urllib.request.urlopen(url=HttpManager.build_xray_server_request_GET(application, parameters))

        return resp.read().decode('ascii')

    @classmethod
    def send_xray_server_direct_request(cls, url, decode=True):
        resp = urllib.request.urlopen(url=XRAY_SERVER_URL+url)

        if decode:
            return resp.read().decode('ascii')
        else:
            return resp.read()

    @classmethod
    def build_xray_server_request_GET(cls, application, parameters):
        return XRAY_SERVER_URL + application + "?" + urllib.parse.urlencode(parameters)


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
        plot_window.setDrawModeEnabled(True, 'rectangle')
        plot_window.setZoomModeEnabled(True)

        if min(y) < 0:
            plot_window.setGraphYLimits(1.01*min(y), max(y)*1.01)
        else:
            plot_window.setGraphYLimits(min(y), max(y)*1.01)
        plot_window.replot()

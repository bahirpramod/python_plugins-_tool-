# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FeatureInformation
                                 A QGIS plugin
 This plugin gets the feature information
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-11-08
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Genesys
        email                : pramoddb@email.igenesys.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.core import *
from qgis.utils import *
from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *
import qgis
import psycopg2
import json

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .feature_information_dialog import FeatureInformationDialog
import os.path
import sys


class FeatureInformation(QgsMapToolIdentifyFeature):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FeatureInformation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Feature Information')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.canvas = self.iface.mapCanvas()
        self.layer = self.iface.activeLayer()
        QgsMapToolIdentifyFeature.__init__(self, self.canvas, self.layer)
        try:
            self.iface.currentLayerChanged.connect(self.active_changed)
        except:
            pass


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FeatureInformation', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/feature_information/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Show Feature Information'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        self.loadData()
        self.iface.layerTreeView().currentLayerChanged.connect(self.layer_selection_changed)
        


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Feature Information'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False


            # self.dlg.pushButton.clicked.connect(self.get_transation)

        # self.testConnection()
        self.layer_selection_changed(self.iface.activeLayer())
        self.iface.mapCanvas().setMapTool(self)
        self.get_domain=self.getDomainValuesFromDB()
        # show the dialog

        # self.variable = ''
        # self.multiple_var = []

        # Run the dialog event loop
        # result = self.dlg.exec_()
        # # See if OK was pressed
        # if result:
        #     # Do something useful here - delete the line containing pass and
        #     # substitute with your code.
        #     pass

        # def testConnection(self):
        #     self.conn = psycopg2.connect(database='inomap_testdb', user='postgres', password='postgres', host='172.16.1.1', port=int(5432))
        #     self.cursor = self.conn.cursor()

    def active_changed(self, layer):
        # self.layer.removeSelection()
        try:
            if isinstance(layer, QgsVectorLayer) and layer.isSpatial():
                self.layer = layer
                self.setLayer(self.layer)
        except:
            pass

    def canvasPressEvent(self, event):
        # self.layer.removeSelection()
        self.iface.mainWindow().findChild(QAction, 'mActionDeselectAll').trigger()
        found_features = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        self.layer.selectByIds([f.mFeature.id() for f in found_features], QgsVectorLayer.AddToSelection)
        feature = [f.mFeature for f in found_features]
        if self.layer.name()=='vw_transition_line':
            tablename = 'transitions'
            column_name = 'transition_id'
            # print("self.data",self.data)
            self.read_only_fld=self.data['transitions_read_only']
        elif self.layer.name()=='vw_lane_poly':
            tablename = 'lanes'
            column_name = 'lane_id'
            self.read_only_fld = self.data['lanes_read_only']
        elif self.layer.name()=='vw_segment_poly':
            tablename = 'segment'
            column_name = 'segment_id'
            self.read_only_fld = self.data['segment_read_only']
        else:
            self.layer.startEditing()
            field_names = self.layer.fields().names()
            for field_name in field_names:
                if field_name in self.data['zone_and_lane_lines_read_only']:
                    dom_ind = field_names.index(field_name)
                    form_config = self.layer.editFormConfig()
                    form_config.setReadOnly(dom_ind, True)
                    self.layer.setEditFormConfig(form_config)
            if len(feature) > 0:
                feat=feature[0]
                b1=None
                if feat is not None:
                    b1=self.iface.openFeatureForm(self.layer, feat,False, True)
                if b1:
                    self.layer.updateFeature(feat)
                return
            # self.SameLayer(self.layer)
        if len(feature) > 0:
            transition_id = feature[0][column_name]
            self.get_transation(transition_id,tablename,column_name)
    def get_transation(self,transition_id,tablename,column_name):
        flt_domain=self.get_domain[tablename]
        fld_list=[list(f.keys())[0] for f in flt_domain]
        # print('fld_list',fld_list)
        self.dlg = FeatureInformationDialog()
        self.dlg.pushButton.clicked.connect(self.updateFeat)
        self.dlg.pushButton_2.clicked.connect(self.dlg.close)
        self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        filter = '"'+column_name+'"' + '=' + "'"+transition_id+"'"
        # print(filter)
        uri = QgsDataSourceUri()
        uri.setConnection(self.data['host'], str(self.data['port']), self.data['database'], self.data['user'], self.data['password'])
        uri.setDataSource(self.schema, tablename, None)
        self.vlayer = QgsVectorLayer(uri.uri(False), tablename, "postgres")
        self.vlayer.setSubsetString(filter)
        self.vlayer.startEditing()
        field_names = self.vlayer.fields().names()
        feat = [f for f in self.vlayer.getFeatures()][0]
        self.feature=feat
        self.fld_dict={}

        for field_name in field_names:
            # print(feat.attributes())
            if field_name in fld_list:
                dom_ind=fld_list.index(field_name)
                dom_val=list(flt_domain[dom_ind][field_name].keys())
                vals=[str(feat[field_name])]+dom_val
                text_field = QComboBox()
                text_field.addItems(vals)
                self.fld_dict.update({field_name:[text_field,str(feat[field_name])]})
            else:

                if field_name in self.read_only_fld:
                    text_field = QLabel()

                else:
                    text_field = QLineEdit()

                text_field.setText(str(feat[field_name]))
                self.fld_dict.update({field_name: [text_field,str(feat[field_name])]})
            self.dlg.formLayout.addRow(QLabel(field_name), text_field)

        self.dlg.show()

    def getDomainValuesFromDB(self):
        try:
            domainsValues = {}
            # self.conn = psycopg2.connect(database= self.parent.database.dbname, user='postgres', password='matrix@123', host=self.parent.database.IP, port=self.parent.database.port)

            self.conn = psycopg2.connect(database=self.data['database'], user=self.data['user'], password=self.data['password'],
                                         host=self.data['host'], port=int(self.data['port']))
            sql = "select * from master.domain_mapping_master"
            # print("sql ", sql )
            isExecute, rows, sException_reson, colums = self.sql_FeachRecords(sql)
            # print("rows",rows)
            if isExecute == False:
                # print("test_11")
                QMessageBox.information(None, 'Get Domain Settings',
                                        "Unable to fetch Domain Settings from master table in DB:-" + str(
                                            sException_reson))
            else:
                # print("test_12")
                for row in rows:
                    domain = {}
                    if row[2] not in domainsValues.keys():
                        domainsValues[row[2]] = []
                    sql = "select {0},{1} from {2}.{3}".format(row[6], row[7], row[4], row[5])
                    # print("sql",sql)
                    isExecute, rows2, sException_reson, colums = self.sql_FeachRecords(sql)
                    # print("rows2",rows2)
                    if isExecute == False:
                        QMessageBox.information(None, 'Get Domain Settings',
                                                "Unable to fetch Domain Settings from master table in DB:-" + str(
                                                    sException_reson))
                    else:
                        domain_ = {}
                        keyIndx = 0
                        valIndx = 1
                        if len(colums) > 1:
                            if str(colums[1][0]) == row[7]:
                                keyIndx = 1
                                valIndx = 0
                            for row2 in rows2:
                                domain_[str(row2[keyIndx])] = str(row2[valIndx])
                        domain[row[3]] = domain_
                    domainsValues[row[2]].append(domain)
            # print("domainsValues", domainsValues)
            # self.domain_list=domainsValues
            return domainsValues
        except:
            QgsMessageLog.logMessage("Unable to Fetch Domain records", "AddPostgresLayerToMap", Qgis.Info)
        finally:
            self.conn.close()
            self.conn = None

    def sql_FeachRecords(self, sql, isCommit=False, isSilent=True, isCloseConn=True):
        isExecute = False
        sException_reson = None
        cur = None
        rows = None
        QgsMessageLog.logMessage("Query :- " + str(sql), "AddPostgresLayerToMap", Qgis.Info)
        cur = self.conn.cursor()
        try:
            # print("test_13")
            cur.execute(sql)
            if isCommit == True:
                self.conn.commit()
            rows = cur.fetchall()
            # print("test_13")
            isExecute = True
        except Exception as e:
            # print("test")
            sException_reson = str(sys.exc_info())
            if isSilent == False:
                QMessageBox.information(None, 'AddPostgresLayerToMap',
                                        "Unable to Feach Records Query reason:-" + str(sys.exc_info()))
            QgsMessageLog.logMessage("Unable to Feach Records Query reason :-" + str(e), "AddPostgresLayerToMap",
                                     Qgis.Info)
            isExecute = False
        # finally:
        # if isCloseConn == True:
        # self.conn.close()
        # self.conn = None
        return isExecute, rows, sException_reson, cur.description


        # QMessageBox.information(self.dlg, 'Successfull',
        #                         "The operation has been successfully completed.\nHence the Transition is created.")
    def updateFeat(self):
        # print("gulab")
        # self.vlayer.startEditing()
        fld_names=self.fld_dict.keys()
        for fld in fld_names:
            # print(i,fld)
            i, j = self.dlg.formLayout.getWidgetPosition(self.fld_dict[fld][0])
            widget_item = self.dlg.formLayout.itemAt(i, j)
            widget = widget_item.widget()
            try:
                text = widget.text()
                text_old =self.fld_dict[fld][1]

            except:
                text = widget.currentText()
                text_old = self.fld_dict[fld][1]

            if str(text) != str(text_old):
                self.feature[fld]=text
                self.vlayer.updateFeature(self.feature)
                self.vlayer.commitChanges()
        QMessageBox.information(self.dlg, 'Successfull',
                                "The Values has been successfully Updated.")
        pass

    def loadData(self):
        self.data = {}
        path2 = self.plugin_dir
        path = os.path.join(path2, "AppConfig.json")
        try:
            if os.path.exists(path):
                with open(path) as json_file:
                    self.data = json.load(json_file)
                    pass
                # print (self.data)
                pass
        except Exception as e:
            err1 = "unable read data:-\n" + str(e)
            QMessageBox.information(None, 'Error', err1)
            pass
    def layer_selection_changed(self,layer):
        try:
            # print("singal received",layer)
            source = layer.source()
            # print("source",source)
            kvp = source.split(" ")
            for kv in kvp:
                if kv.startswith("table"):
                    # self.active_schema = kv.split("=")[1][0:-15]
                    schema1= kv.split("=")[1][0:-1]
                    self.active_schema=schema1.split(".")[0]
                    self.schema=self.active_schema[1:-1]
                    # print( "self.active_schema",self.schema)

                    # print( "schemajson",self.data['schema'])
        except Exception as e:
            pass
            # err1 = "select layer:-\n" + str(e)
            # QMessageBox.information(None, 'Error', err1)

# t = FeatureInformation(iface)

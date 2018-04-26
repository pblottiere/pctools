# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PCTools
                                 A QGIS plugin
 PointCloud Tools
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-01-03
        copyright            : (C) 2018 by Paul Blottiere
        email                : blottiere.paul@gmail.com
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

__author__ = 'a'
__date__ = '2018-01-03'
__copyright__ = '(C) 2018 by Paul Blottiere'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication

from qgis.PyQt.QtCore import QVariant

from qgis.core import (QgsProcessing,
                       QgsVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsWkbTypes,
                       QgsGeometry,
                       QgsRectangle,
                       QgsDataSourceUri,
                       QgsSettings,
                       QgsMessageLog,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

import psycopg2
import pdal
import json


class ExtentImport(QgsProcessingAlgorithm):

    INPUT = 'LAS'
    OUTPUT_LAYER = 'LAYER'

    def uri(self, db):
        s = QgsSettings()
        s.beginGroup('PostgreSQL/connections/{}/'.format(db))

        host = s.value( 'host' )
        port = s.value( 'port' )
        user = s.value( 'username' )
        pwd = s.value( 'password' )

        uri = QgsDataSourceUri()
        uri.setConnection(str(host), str(port), str(db), str(user), str(pwd))

        return uri

    def pgpointcloudDatabases(self):
        s = QgsSettings()
        s.beginGroup('PostgreSQL/connections')

        dbs = s.childGroups()
        pcdbs = []
        for db in dbs:
            uri = self.uri( db )

            try:
                conn = psycopg2.connect(uri.connectionInfo(True))
                cur = conn.cursor()
                cur.execute('select * from pg_extension where extname=\'pointcloud\';')
                if cur.fetchall():
                    cur.close()
                    pcdbs.append( db )

            except psycopg2.OperationalError as e:
                msg = 'Connection failed for {} ({})'.format(db, str(e))
                QgsMessageLog.logMessage(msg)
                continue

        return pcdbs

    def initAlgorithm(self, config):

        # las file
        lasParam = QgsProcessingParameterFile( self.INPUT )
        lasParam.setDescription( self.tr( 'LAS file' ) )
        #lasParam.setExtension( 'las' )

        self.addParameter( lasParam )

        # output layer
        layerParam = QgsProcessingParameterFeatureSink( self.OUTPUT_LAYER )
        layerParam.setDescription( self.tr( 'Vector layer' ) )

        self.addParameter( layerParam )


    def processAlgorithm(self, parameters, context, feedback):

        feedback.setProgress(0)

        filenames = self.parameterAsString(parameters, self.INPUT, context)

        crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)

        fields = QgsFields()
        fields.append(QgsField("filename", QVariant.String))
        fields.append(QgsField("points", QVariant.Int))

        outputWkb = QgsWkbTypes.Polygon
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_LAYER,
                                               context, fields, outputWkb, crs)

        total = 100 / len(filenames.split(";"))
        count = 0
        for filename in filenames.split(";"):
            if feedback.isCanceled():
                break

            feedback.setProgress(count * total)
            count += 1

            QgsMessageLog.logMessage("Filename:{}".format(filename))

            pipejson = """
            {{
                \"pipeline\":[
                    \"{}\"
                ]
            }}
            """.format(filename)

            pipeline = pdal.Pipeline(pipejson)
            pipeline.validate()
            pipeline.loglevel = 4
            pipeline.execute()

            meta = json.loads(pipeline.get_metadata())
            minx = meta["metadata"]["readers.las"][0]['minx']
            maxx = meta["metadata"]["readers.las"][0]['maxx']
            miny = meta["metadata"]["readers.las"][0]['miny']
            maxy = meta["metadata"]["readers.las"][0]['maxy']
            count = meta["metadata"]["readers.las"][0]['count']

            extent = QgsRectangle(minx, miny, maxx, maxy)
            wkt = extent.asWktPolygon()
            geom = QgsGeometry().fromWkt(wkt)

            f = QgsFeature()
            f.setFields(QgsFields())
            f.setGeometry(geom)
            f.setAttributes([filename, count])

            sink.addFeature(f, QgsFeatureSink.FastInsert)

            #features = vlayer.getFeatures()
            #for current, inFeat in enumerate(features):
            #    sink.addFeature(inFeat, QgsFeatureSink.FastInsert)

        return {self.OUTPUT_LAYER: dest_id}

    def name(self):
        return 'LAS/LAZ to extents'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Import'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExtentImport()

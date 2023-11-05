# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FeatureInformation
                                 A QGIS plugin
 This plugin gets the feature information
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-11-08
        copyright            : (C) 2022 by Genesys
        email                : pramoddb@email.igenesys.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FeatureInformation class from file FeatureInformation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .feature_information import FeatureInformation
    return FeatureInformation(iface)

# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets
import re
import pymel.core as pm
import maya.cmds as cmds


class DerHrunkel(object):
    def __init__(self, parent=None):
        super(DerHrunkel, self).__init__(parent)

        self.start, self.end = int(pm.playbackOptions(q=1, min=1)), int(pm.playbackOptions(q=1, max=1))

        # get camera
        pat = re.compile(r"cam_part\d{2}_\D{2}\d{,3}.+")
        cameras = pm.ls(type='camera')
        self.current = [a for a in cameras if pat.search(a.nodeName())][0]

        # create panel for playblast
        self.viewport = pm.modelPanel(tearOff=True)
        pm.lookThru(self.current)

    def apply_setting(self):
        """apply setting for camera, render resolution, viweport settings etc"""
        self.current.filmFit.set(3)
        self.current.setAspectRatio(1.78)
        self.current.displayFilmGate.set(1)
        self.current.displayResolution.set(0)
        self.current.displayGateMask.set(1)
        self.current.displayGateMaskOpacity.set(0.99)
        self.current.overscan.set(1.005)
        self.current.displaySafeAction.set(1)
        self.current.displayGateMaskColor.set([0.01, 0.01, 0.01])

    def get_path(self):
        """where to store video file"""
        pass

    def publish(self):
        """publish playblast video to server"""
        pass


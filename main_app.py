# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets
import re
import pymel.core as pm
import maya.cmds as cmds

# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets
import re
import pymel.core as pm
import maya.cmds as cmds
from os.path import split, splitext, normpath, join
from shutil import copy2


class DerHrunkel(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(DerHrunkel, self).__init__(parent)
        self.start, self.end = int(pm.playbackOptions(q=1, min=1)), int(pm.playbackOptions(q=1, max=1))
        self.scene_path, self.scene_name = split(pm.sceneName())
        self.playblast_path = normpath(join(self.scene_path, splitext(self.scene_name)[0] + '.mov'))

        # get camera
        pat = re.compile(r"cam_part\d{2}_\D{2}\d{,3}.+")
        cameras = pm.ls(type='camera')
        self.current_camera = [a for a in cameras if pat.search(a.nodeName())]

        # self.current_camera = self.current_camera[0] if isinstance(self.current_camera, list) else None
        self.viewport = None
        print(self.current_camera)

        # setup ui
        self.ui = HrunkelUi(camlist=self.current_camera, parent=self)
        self.setCentralWidget(self.ui)

        # apply settings
        self.apply_setting()

    # def check_path(self):
    #     if os.path.exists(self.playblast_path):
    #         copy2()

    def apply_setting(self):
        """apply setting for camera, render resolution, viweport settings etc"""
        x = self.ui.cameras.currentText()
        camera = pm.PyNode(x)
        dr = pm.PyNode('defaultResolution')
        dr.pixelAspect.set(1)
        dr.width.set(1920)
        dr.height.set(1080)
        dr.pixelAspect.set(1)
        camera.filmFit.set(3)
        camera.setAspectRatio(1.78)
        camera.displayFilmGate.set(1)
        camera.displayResolution.set(0)
        camera.displayGateMask.set(1)
        camera.displayGateMaskOpacity.set(0.99)
        camera.overscan.set(1.005)
        camera.displaySafeAction.set(1)
        camera.displaySafeTitle.set(0)
        camera.displayFilmPivot.set(0)
        camera.displayFilmOrigin.set(0)
        camera.depthOfField.set(0)
        camera.displayGateMaskColor.set([0.01, 0.01, 0.01])

        # settings for panel
        viewport_setting = {
            "rendererName": "vp2Renderer",
            "fogging": False,
            "fogMode": "linear",
            "fogDensity": 1,
            "fogStart": 1,
            "fogEnd": 1,
            "fogColor": (0, 0, 0, 0),
            "shadows": False,
            "displayTextures": True,
            "displayLights": "default",
            "useDefaultMaterial": False,
            "wireframeOnShaded": False,
            "displayAppearance": 'smoothShaded',
            "selectionHiliteDisplay": False,
            "headsUpDisplay": True
        }
        # settings for camera

        # create panel for playblast
        self.viewport = pm.modelPanel(tearOff=True)
        pm.setFocus(self.viewport)
        pm.lookThru(self.current_camera)
        pm.modelEditor(self.viewport, edit=True, allObjects=False)
        pm.modelEditor(self.viewport, edit=True, polymeshes=True)
        for key, value in viewport_setting.iteritems():
            pm.modelEditor(self.viewport, edit=True, **{key: value})

        self.setup_huds()

    def setup_huds(self):
        data = {'objectDetailsVisibility': 'ToggleObjectDetails;',
                'polyCountVisibility': 'TogglePolyCount;',
                'subdDetailsVisibility': 'ToggleSubdDetails;',
                'animationDetailsVisibility': 'ToggleAnimationDetails;',
                'frameRateVisibility': 'ToggleFrameRate;',
                'cameraNamesVisibility': 'ToggleCameraNames;',
                'viewAxisVisibility': 'ToggleViewAxis;',
                'toolMessageVisible': 'ToggleToolMessage;',
                'currentContainerVisibility': 'ToggleCurrentContainerHud',
                'currentFrameVisibility': 'ToggleCurrentFrame',
                'focalLengthVisibility': 'ToggleFocalLength',
                'hikDetailsVisibility': 'ToggleHikDetails',
                'materialLoadingDetailsVisibility': 'ToggleMaterialLoadingDetailsVisibility',
                'particleCountVisibility': 'ToggleParticleCount',
                'sceneTimecodeVisibility': 'ToggleSceneTimecode',
                'selectDetailsVisibility': 'ToggleSelectDetails',
                'symmetryVisibility': 'ToggleSymmetryDisplay'
                }
        for tgl in data:
            try:
                if cmds.optionVar(q=tgl):
                    mel.eval(data[tgl])
            except:
                pass
        try:
            if cmds.toggleAxis(q=True, o=True):
                mel.eval('ToggleOriginAxis;')
        except:
            pass

    def get_path(self):
        """where to store video file"""
        pass

    def publish(self):
        """publish playblast video to server"""
        pass


class HrunkelUi(QtWidgets.QWidget):
    def __init__(self, camlist, parent=None):
        super(HrunkelUi, self).__init__(parent)

        ml = QtWidgets.QGridLayout(self)
        self.cameras = QtWidgets.QComboBox(self)
        for c in camlist:
            # text = c.nodeName().replace('Shape', '').replace('shape', '')
            self.cameras.addItem(c.nodeName())

        self.create_camera = QtWidgets.QPushButton(self)
        self.output = QtWidgets.QLineEdit(self)

        self.playblast = QtWidgets.QPushButton(self)
        self.playblast.setObjectName('playblast')
        self.playblast.setMinimumHeight(26)
        lay1 = QtWidgets.QHBoxLayout(self.playblast)
        lay1.setObjectName('button_layout')
        lay1.setContentsMargins(0,0,0,0)
        self.publish = QtWidgets.QCheckBox(self)
        self.publish.setObjectName('publish')
        self.publish.setText('')
        self.publish.setStyleSheet("""QCheckBox{padding-left: 5px; padding-right: 10px}""")
        lay1.addWidget(self.publish, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        ml.addWidget(self.output, 0, 0, 1, 3)
        ml.addWidget(self.cameras, 1, 0, 1, 2)
        ml.addWidget(self.create_camera, 1, 2, 1, 1)
        ml.addWidget(self.playblast, 2, 0, 1, 3)
        self.setLayout(ml)

        @self.playblast.clicked.connect
        def do_playblast():
            publish = self.publish.isChecked()
            if publish:
                print('publish')
            else:
                print('lol')


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = HrunkelUi()
    win.show()
    sys.exit(app.exec_())


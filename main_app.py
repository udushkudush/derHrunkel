# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets
import re
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
from os.path import split, splitext, normpath, join, dirname, exists
from glob import glob
from shutil import copy2


class DerHrunkel(QtWidgets.QMainWindow):
    part = None
    scene = None
    user = None
    version = None
    output_dimentions = [1920, 1080]
    backup = False

    def __init__(self, parent=None):
        super(DerHrunkel, self).__init__(parent)
        self.setMinimumSize(423, 155)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('Der Hrunkel')
        self.set_style()
        self.start, self.end = int(pm.playbackOptions(q=1, min=1)), int(pm.playbackOptions(q=1, max=1))
        self.scene_path, self.scene_name = split(pm.sceneName())
        self.playblast_path = normpath(join(self.scene_path, splitext(self.scene_name)[0] + '.mov'))
        self.define_variables()
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

        # SIGNALS
        self.ui.cameras.currentIndexChanged.connect(self.switch_view)
        self.ui.playblast.clicked.connect(self.do_playblast)

        # defive version of file, then select actual camera, applying settings
        self.version = self.define_version()
        self.update_camera()
        self.apply_camera_setting()
        self.create_temp_panel()
        self.apply_panel_setting()
        self.path_to_video()

    def update_camera(self):
        self.current_camera = pm.PyNode(self.ui.cameras.currentText())
        # print('>>> ', self.current_camera)

    def apply_camera_setting(self):
        """apply setting for camera, render resolution, viweport settings etc"""
        # x = self.ui.cameras.currentText()
        # camera = pm.PyNode(x)
        print('::: {}'.format(self.current_camera))
        camera = self.current_camera
        dr = pm.PyNode('defaultResolution')
        dr.pixelAspect.set(1)
        dr.width.set(self.output_dimentions[0])
        dr.height.set(self.output_dimentions[1])
        dr.pixelAspect.set(1)
        camera.filmFit.set(3)
        camera.nearClipPlane.set(1)
        camera.farClipPlane.set(35000)
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

    def create_temp_panel(self):
        # create panel for playblast
        self.viewport = pm.modelPanel(tearOff=True)
        pm.setFocus(self.viewport)
        pm.control(self.viewport, edit=True, w=self.output_dimentions[0])
        pm.control(self.viewport, edit=True, h=self.output_dimentions[1])
        pm.lookThru(self.current_camera)

    def apply_panel_setting(self):
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
        # enable multisample AA
        hrg = pm.PyNode('hardwareRenderingGlobals')
        hrg.multiSampleEnable.set(1)
        pm.modelEditor(self.viewport, edit=True, allObjects=False)
        pm.modelEditor(self.viewport, edit=True, grid=False)
        pm.modelEditor(self.viewport, edit=True, manipulators=False)
        pm.modelEditor(self.viewport, edit=True, sel=False)
        pm.modelEditor(self.viewport, edit=True, polymeshes=True)
        for key, value in viewport_setting.iteritems():
            pm.modelEditor(self.viewport, edit=True, **{key: value})

        self.setup_huds()

    def switch_view(self):
        self.update_camera()
        self.apply_camera_setting()
        pm.setFocus(self.viewport)
        pm.lookThru(self.current_camera)

    def setup_huds(self):
        data = dict(objectDetailsVisibility='ToggleObjectDetails;',
                    polyCountVisibility='TogglePolyCount;',
                    subdDetailsVisibility='ToggleSubdDetails;',
                    animationDetailsVisibility='ToggleAnimationDetails;',
                    frameRateVisibility='ToggleFrameRate;',
                    viewAxisVisibility='ToggleViewAxis;',
                    toolMessageVisible='ToggleToolMessage;',
                    currentContainerVisibility='ToggleCurrentContainerHud',
                    currentFrameVisibility='ToggleCurrentFrame',
                    focalLengthVisibility='ToggleFocalLength',
                    hikDetailsVisibility='ToggleHikDetails',
                    materialLoadingDetailsVisibility='ToggleMaterialLoadingDetailsVisibility',
                    particleCountVisibility='ToggleParticleCount',
                    sceneTimecodeVisibility='ToggleSceneTimecode',
                    # 'cameraNamesVisibility': 'ToggleCameraNames;',
                    selectDetailsVisibility='ToggleSelectDetails',
                    symmetryVisibility='ToggleSymmetryDisplay')
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
        if not pm.optionVar(q='cameraNamesVisibility'):
            mel.eval('ToggleCameraNames;')
        dfs = 'large'
        labelFontSize = 'large'
        blockSize = 'small'

        # for i in range(10):
        #     for b in range(4):
        #         cmds.headsUpDisplay(rp=[i, b])
        HUD_names = ['HUD_partNum', 'HUD_sceneNum', 'HUD_user', 'HUD_version', 'HUD_frame']
        for h in HUD_names:
            try:
                pm.headsUpDisplay(h, rem=True)
            except:
                pass

        pm.headsUpDisplay('HUD_partNum', section=6, block=4, blockSize=blockSize, label='Part:',
                          dfs=dfs, labelFontSize=labelFontSize, command=lambda: self.part)

        pm.headsUpDisplay('HUD_sceneNum', section=6, block=3, blockSize=blockSize, label='Scene:',
                          dfs=dfs, labelFontSize=labelFontSize, command=lambda: self.scene)

        pm.headsUpDisplay('HUD_user', section=5, block=3, blockSize=blockSize, label='User:',
                          dfs=dfs, labelFontSize=labelFontSize, command=lambda: self.user)

        pm.headsUpDisplay('HUD_version', section=5, block=4, blockSize=blockSize, label='ver:',
                          dfs=dfs, labelFontSize=labelFontSize, command=lambda: self.version, atr=True)

        pm.headsUpDisplay('HUD_frame', section=8, block=3, blockSize=blockSize, label='frame:',
                          dfs=dfs, labelFontSize=labelFontSize, command=lambda: pm.currentTime(q=1), atr=True)

    def path_to_video(self):
        """where to store video file"""
        self.ui.output.setText(self.playblast_path)

    def define_version(self):
        x = '{}/*.mov'.format(dirname(self.playblast_path))
        _path = glob(x)
        pat = re.compile(r"(_v)(\d{,2})$")
        _v = 1
        files = [a for a in _path if pat.search(splitext(split(a)[-1])[0])]
        if files:
            _v = max([int(pat.search(splitext(a)[0]).group(2)) for a in files])
            return _v + 1
        else:
            print('no versions')
            return _v

    def define_variables(self):
        pat = re.compile(r"(part\d{2})_(s[ch]\d{,3})")
        res = pat.search(self.scene_name)
        self.part = res.group(1)
        self.scene = res.group(2)
        self.user = 'v.borzenko'
        self.version = '#01'

    def publish(self):
        """publish playblast video to server"""
        pass

    def do_backup(self):
        if exists(self.playblast_path):
            new = '{}_v{:02d}.mov'.format(splitext(self.playblast_path)[0], self.version)
            copy2(self.playblast_path, new)
        else:
            print('no versions')

    def do_playblast(self):
        self.do_backup()
        pm.setFocus(self.viewport)
        data = dict(
            filename=self.playblast_path,
            widthHeight=self.output_dimentions,
            forceOverwrite=True,
            format='qt',
            quality=100,
            percent=100,
            compression='H.264',
            clearCache=True,
            showOrnaments=True,
            offScreen=True
        )
        pm.playblast(**data)

        if pm.modelPanel(self.viewport, exists=True):
            cmds.deleteUI(self.viewport, panel=True)
        self.close()

    def set_style(self):
        colors = {
            '@border': 'rgb(78,78,78)',
            '@borderHover': 'rgb(87,87,87)',
            '@mainWidgetColor': 'rgb(98,98,98)',
            '@widgetHover': 'rgb(118,118,118)'
        }
        style = """QLineEdit{border-radius: 5px; border: 2px solid @border}
            QLineEdit:hover{border: 2px solid @borderHover}
            QComboBox{border-radius: 6px; font-size: 12pt; border: 2px solid @border}
            QComboBox:hover{border: 2px solid @borderHover}
            QComboBox::drop-down{
                background-color: rgb(55,55,55);
                width: 32px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px}
            QComboBox::drop-down:hover{background-color: @widgetHover}
            QComboBox:item{height: 18px}
            QPushButton{
                min-width: 36px;
                border: 2px solid @border;
                border-radius: 5px;
                background-color: @mainWidgetColor}
            QPushButton:hover{background-color: @widgetHover}
        """
        for k in colors:
            style = style.replace(k, colors[k])
        # print('style: {}'.format(style))
        self.setStyleSheet(style)


class HrunkelUi(QtWidgets.QWidget):
    def __init__(self, camlist, parent=None):
        super(HrunkelUi, self).__init__(parent)
        ml = QtWidgets.QGridLayout(self)
        self.cameras = QtWidgets.QComboBox(self)
        self.cameras.setObjectName('camera_list')
        self.cameras.setMinimumHeight(32)
        for c in camlist:
            # text = c.nodeName().replace('Shape', '').replace('shape', '')
            self.cameras.addItem(c.nodeName())

        self.create_camera = QtWidgets.QPushButton(self)
        self.create_camera.setObjectName('create_camera')
        self.create_camera.setText('+')
        self.create_camera.setMinimumHeight(32)
        self.output = QtWidgets.QLineEdit(self)
        self.output.setObjectName('output_file')
        self.output.setMinimumHeight(30)

        self.playblast = QtWidgets.QPushButton(self)
        self.playblast.setObjectName('playblast')
        self.playblast.setText('PLAYBLAST')
        self.playblast.setMinimumHeight(42)
        lay1 = QtWidgets.QHBoxLayout(self.playblast)
        lay1.setObjectName('button_layout')
        lay1.setContentsMargins(0,0,0,0)
        self.publish = QtWidgets.QCheckBox(self)
        self.publish.setObjectName('publish')
        self.publish.setText('')
        self.publish.setStyleSheet("""QCheckBox{padding-left: 15px; padding-right: 10px}""")
        lay1.addWidget(self.publish, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        ml.addWidget(self.output, 0, 0, 1, 3)
        ml.addWidget(self.cameras, 1, 0, 1, 2)
        ml.addWidget(self.create_camera, 1, 2, 1, 1)
        ml.addWidget(self.playblast, 2, 0, 1, 3)
        ml.setColumnStretch(0, 3)
        ml.setColumnMinimumWidth(1, 36)
        self.setLayout(ml)

        @self.publish.stateChanged.connect
        def change_button_status():
            publish = self.publish.isChecked()
            if publish:
                self.playblast.setText('DO PUBLISH')
            else:
                self.playblast.setText('PLAYBLAST')

        # @self.playblast.clicked.connect
        # def do_playblast():
        #     publish = self.publish.isChecked()
        #     if publish:
        #         print('publish')
        #     else:
        #         print('lol')


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = HrunkelUi()
    win.show()
    sys.exit(app.exec_())


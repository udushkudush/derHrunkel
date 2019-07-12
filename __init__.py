# -*- coding:utf8 -*-

#import DerHrunkel
# reload(DerHrunkel)

import pymel.core as pm
import main_app
reload(main_app)
from main_app import DerHrunkel

maya_window = pm.ui.PyUI('MayaWindow').asQtObject()
try:
    der_hrunkel.close()
    print('try delete widget')
except NameError as e:
    print(e)
except RuntimeError as e:
    print(e)
der_hrunkel = DerHrunkel(maya_window)
der_hrunkel.show()

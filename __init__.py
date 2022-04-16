bl_info = {
    "name": "PCAfree",
    "author": "DerMische",
    "version": (1, 1),
    "blender": (3, 0),
    "location": "View3D > UI > PCAfree",
    "description": "PanoCams & Hotspots",
    "warning": "",
    "wiki_url": "https://der-mische.de/panocamadder/",
    "category": "3D View",
}

import bpy


from . pcaf_ui import PCAF_Settings, PCAF_PT_main_panel
from . pcaf_op import PCAF_OT_addpc, PCAF_OT_addhsop


classes = (PCAF_Settings,
            PCAF_PT_main_panel,
            PCAF_OT_addpc,
            PCAF_OT_addhsop)
 
 
register, unregister = bpy.utils.register_classes_factory(classes)


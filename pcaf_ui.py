import bpy
 
 
class PCAF_Settings(bpy.types.PropertyGroup):
    
    my_string : bpy.props.StringProperty(name= "Name")
    

class PCAF_PT_main_panel(bpy.types.Panel):
    bl_label = "PCA free 1.1"
    bl_idname = "PCAF_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PCA free"
    bl_context = 'objectmode'
    
 
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("pcaf.addpc", icon= 'CON_CAMERASOLVER')
        col.operator("pcaf.addhs", icon= 'PROP_ON')
        
        layout.scale_y = 1.3
    
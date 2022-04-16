import bpy
import os
from bpy_extras.io_utils import ImportHelper

class PCAF_OT_addpc(bpy.types.Operator, ImportHelper):
    """Adds A New PanoCam Scene"""
    bl_label = "Add PanoCam"
    bl_idname = "pcaf.addpc"
    bl_options = {'UNDO'}
    
    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff',
        options={'HIDDEN'}
    )
    
    pname: bpy.props.StringProperty(
        name='Name: ',
        description='Give your pano a name',
        default='My Pano'
    )
    
    cheight : bpy.props.FloatProperty(
        name= "Camera Height: ",
        description='Height above the 3D-cursor',
        soft_min= 0, soft_max= 1500, 
        default= (1.65)
        )

    material_boolean: bpy.props.BoolProperty(
        name='Material/World',
        description='create panomaterial and background world',
        default=True,
        )
    
    
    
    def execute(self, context):
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)


        # check selected objects
        ol = 0
        if len(bpy.context.selected_objects) > 0:
            ol = 1
            so = bpy.context.selected_objects[0]

        # remove materials
        cm = self.material_boolean
        if cm == True :
            if extension != '.jpg' and extension != '.jpeg' and extension != '.png' and extension != '.tif' and extension != '.tiff':
                self.report({'WARNING'}, 'Only jpg, png or tif images allowed!')
                return {'FINISHED'}
            # remove all materials
            if ol == 1 and so.type == 'MESH':            
                for s in so.material_slots:
                    bpy.ops.object.material_slot_remove()
            # else:
            #     self.report({'WARNING'}, 'This is not a mesh..')
            #     return {'FINISHED'}

            

        
        imgpath = str(self.filepath)
        pn = str(self.pname)
        ch = self.cheight
        

        #clean input str
        pn = pn.strip()
        pn = pn.replace('ä', 'ae')
        pn = pn.replace('ö', 'oe')
        pn = pn.replace('ü', 'ue')
        pn = pn.replace('Ä', 'Ae')
        pn = pn.replace('Ö', 'Oe')
        pn = pn.replace('Ü', 'Ue')
        pn = pn.replace('ß', 'ss')
        pn = pn.replace(' ', '_')

        #if bpy.context.active_object == None or bpy.context.active_object.type == 'MESH':
        
        #add Panoempty        
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        bpy.context.object.name = pn + "_HANDLE"
    
        pemty = bpy.context.active_object
        pemty.location[2] += ch
        pemty.show_name = True


        # add Cam360
        bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', rotation=(1.5708, 0, 0))
        pcam = bpy.context.active_object

        pcam.data.lens_unit = 'MILLIMETERS'
        pcam.data.lens = 18
        pcam.name = pn + "_CAM"
        pcam.data.show_name = True
        pcam.data.show_passepartout = False
        bpy.ops.object.constraint_add(type='COPY_LOCATION')   
        bpy.context.object.constraints["Copy Location"].target = pemty
        
        pcam.lock_location[0] = True
        pcam.lock_location[1] = True
        pcam.lock_location[2] = True
        pcam.lock_rotation[1] = True
        bpy.context.space_data.lock_camera = True
        bpy.context.space_data.camera = pcam
        
        #add rotempty        
        bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
        prot = bpy.context.active_object
        prot.empty_display_size = 0.1
        prot.name = pn + "_ROT"
        prot.lock_location[0] = True
        prot.lock_location[1] = True
        prot.lock_location[2] = True       
        bpy.ops.object.constraint_add(type='COPY_ROTATION')      
        bpy.context.object.constraints["Copy Rotation"].target = pemty

        # create material
        if cm == True:
    
            #add mat
            pmat = bpy.data.materials.new(name= "new")
            pmat.use_nodes = True
            pmat.use_fake_user = True
            pmat.name = pn + "_MAT"
            
            # Remove default material
            pmat.node_tree.nodes.remove(pmat.node_tree.nodes.get('Principled BSDF')) #title of the existing node when materials.new
            pmat_output = pmat.node_tree.nodes.get('Material Output')
            
            diffuse = pmat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
            diffuse.inputs["Color"].default_value = (0, 1, 0, 0.5)
            diffuse.location = (-30,0)
            
            texslider_node = pmat.node_tree.nodes.new('ShaderNodeMixShader')
            pmat.node_tree.nodes["Mix Shader"].label = "MIXER"
            texslider_node.location = (130,200)
            pmat.node_tree.nodes["Mix Shader"].inputs[0].default_value = 1
            
            panoemi_node = pmat.node_tree.nodes.new('ShaderNodeEmission')
            pmat.node_tree.nodes["Emission"]
            panoemi_node.location = (-30,200)
            
            panotex_node = pmat.node_tree.nodes.new('ShaderNodeTexEnvironment')
            pmat.node_tree.nodes["Environment Texture"].label = "Panorama"
            panotex_node.image = bpy.data.images.load(imgpath)
            panotex_node.location = (-300,200)

            panotexm2_node = pmat.node_tree.nodes.new('ShaderNodeMapping')
            pmat.node_tree.nodes["Mapping"].label = "Pre Leveling Panorama" 
            pmat.node_tree.nodes["Mapping"].name = "PanoTexMapping02"
            pmat.node_tree.nodes["PanoTexMapping02"].inputs[2].default_value[2] = -1.5708 
            panotexm2_node.location = (-700,300)

            panotex_co_node = pmat.node_tree.nodes.new('ShaderNodeTexCoord')
            panotex_co_node.location = (-1000,300)
            pmat.node_tree.nodes["Texture Coordinate"].object = pemty

            # link shaders 
            pmat.node_tree.links.new(texslider_node.outputs[0], pmat_output.inputs[0])
            pmat.node_tree.links.new(panoemi_node.outputs[0], texslider_node.inputs[2])
            pmat.node_tree.links.new(diffuse.outputs[0], texslider_node.inputs[1])
            pmat.node_tree.links.new(panotex_node.outputs[0], panoemi_node.inputs[0])
            pmat.node_tree.links.new(panotexm2_node.outputs[0], panotex_node.inputs[0])
            pmat.node_tree.links.new(panotex_co_node.outputs[3], panotexm2_node.inputs[0])

            # backface culling
            pmat.use_backface_culling = True
 
            # apply MAT
            if ol == 1:
                if so.type == 'MESH':
                    so.active_material = pmat

            # Create PanoWorld          
            pworld = bpy.data.worlds.new(name= "new")
            pworld.use_nodes = True
            pworld.use_fake_user = True
            pworld.name = pn + "_WORLD"
            
            pano_node = pworld.node_tree.nodes.new('ShaderNodeTexEnvironment')
            pworld.node_tree.nodes["Environment Texture"].label = "Panorama"
            pano_node.image = bpy.data.images.load(imgpath)   
            pano_node.location = (-400,500)
            
            panobw_node = pworld.node_tree.nodes.new('ShaderNodeHueSaturation')
            pworld.node_tree.nodes["Hue Saturation Value"]
            pworld.node_tree.nodes["Hue Saturation Value"].inputs[1].default_value = 0 
            panobw_node.location = (-100,500)

            
            pano_m_node2 = pworld.node_tree.nodes.new('ShaderNodeMapping')
            pworld.node_tree.nodes["Mapping"].label = "Pre Leveling Panorama" 
            pworld.node_tree.nodes["Mapping"].name = "PanoMapping02"
            pworld.node_tree.nodes["PanoMapping02"].inputs[2].default_value[2] = -1.5708 
            pano_m_node2.location = (-800,300)
            
            pano_co_node = pworld.node_tree.nodes.new('ShaderNodeTexCoord')
            pano_co_node.location = (-1000,300)
            pworld.node_tree.nodes["Texture Coordinate"].object = prot

        
            #Creating Links between the Nodes
            background_node = pworld.node_tree.nodes["Background"]
            
            pworld.node_tree.links.new(pano_co_node.outputs[3], pano_m_node2.inputs[0])
            pworld.node_tree.links.new(pano_m_node2.outputs[0], pano_node.inputs[0])
            pworld.node_tree.links.new(pano_node.outputs[0], panobw_node.inputs[4])
            pworld.node_tree.links.new(panobw_node.outputs[0], background_node.inputs[0])

            pworld.node_tree.nodes["Background"].inputs[0].show_expanded = True
            pworld.node_tree.nodes["Hue Saturation Value"].inputs[4].show_expanded = True
            pmat.node_tree.nodes["Mix Shader"].inputs[2].show_expanded = True
            pmat.node_tree.nodes["Emission"].inputs[0].show_expanded = True
            # activate new world
            bpy.context.scene.world = pworld

            self.report({'INFO'}, 'PanoCam, material and world created.')

                    
        
            prot.select_set(state=False)
            pemty.select_set(state=True)      
            bpy.context.view_layer.objects.active = pemty
  
       
        return {'FINISHED'}    





class PCAF_OT_addhsop(bpy.types.Operator):
    """Open The Add Hotspot Dialog Box"""
    bl_label = "Add Hotspot"
    bl_idname = "pcaf.addhs"
    bl_options = {'UNDO'}
    
    hsname : bpy.props.StringProperty(name= "Name: ", default= "My Hotspot")
    hscolor : bpy.props.FloatVectorProperty(name="Color: ", subtype="COLOR", size=3, min=0.0, max=1.0, default=(1.0, 1.0, 1.0))
    
    
    def execute(self, context):
        
        hsn = self.hsname

        #clean input str
        hsn = hsn.strip()
        hsn = hsn.replace('ä', 'ae')
        hsn = hsn.replace('ö', 'oe')
        hsn = hsn.replace('ü', 'ue')
        hsn = hsn.replace('Ä', 'Ae')
        hsn = hsn.replace('Ö', 'Oe')
        hsn = hsn.replace('Ü', 'Ue')
        hsn = hsn.replace('ß', 'ss')
        hsn = hsn.replace(' ', '_')

    
        hsbgr = self.hscolor[0]
        hsbgg = self.hscolor[1]
        hsbgb = self.hscolor[2]             

        
        
        #Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        
        #Define vertices, faces, edges    
        verts = [(-0.7, 0.7, 0),
            (0.7, 0.7, 0), 
            (-0.2394, 0.174748, 0),
            (-0.174587, 0.174748, 0),
            (-0.13516, 0.174748, 0),
            (-0.066888, 0.174748, 0),
            (0.066888, 0.174748, 0),
            (0.13516, 0.174748, 0),
            (0.174587, 0.174748, 0),
            (0.2394, 0.174748, 0),
            (-0.2394, 0.106514, 0),
            (-0.174587, 0.106514, 0),
            (0.174587, 0.106514, 0),
            (0.2394, 0.106514, 0),
            (-0.066888, 0.024117, 0),
            (0.066888,  0.024117,  0),
            (-0.066888, -0.024117, 0),
            (0.066888,  -0.024117,  0),
            (-0.2394, -0.106514, 0),
            (-0.174587, -0.106514, 0),
            (0.174587, -0.106514, 0),
            (0.2394, -0.106514, 0),
            (-0.2394, -0.174748, 0),
            (-0.174587, -0.174748, 0),
            (-0.13516, -0.174748, 0),
            (-0.066888, -0.174748, 0),
            (0.066888, -0.174748, 0),
            (0.13516, -0.174748, 0),
            (0.174587, -0.174748, 0),
            (0.2394, -0.174748, 0),
            (-0.7, -0.7, 0),
            (0.7, -0.7, 0)]
            
        faces = [(0,1,9,2),
            (1,31,29,9),
            (31,30,22,29),
            (30,0,2,22),
            (2,3,11,10),
            (10,11,19,18),
            (18,19,23,22),
            (3,4,24,23),
            (5,6,15,14),
            (16,17,26,25),
            (7,8,28,27),
            (8,9,13,12),
            (12,13,21,20)]

        #Define mesh and object
        mymesh = bpy.data.meshes.new("HotSpot")
        myobject = bpy.data.objects.new("HotSpot", mymesh)

        #Set location and scene of object
        myobject.location = bpy.context.scene.cursor.location
        bpy.context.collection.objects.link(myobject)

        #Create mesh
        mymesh.from_pydata(verts,[],faces)
        mymesh.update(calc_edges=True)
        
        #Select and make active
        myobject.select_set(True)
        bpy.context.view_layer.objects.active = myobject 
        
        # recalculate normals
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=True)

        # Scale to 0.5
        #bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        #bpy.ops.transform.resize(value=(2, 2, 2))
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))
        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'



        bpy.context.object.name = hsn
        
        
        # Create Emission Material
        obj = bpy.context.active_object        
        objname = bpy.context.active_object.name
        
        #remove all materials
        for s in obj.material_slots:
            bpy.ops.object.material_slot_remove()

        hsmat = bpy.data.materials.new(name= "new")
        hsmat.use_nodes = True
        hsmat.name = objname + "_HSMAT"
        # alpha blend mode / viewportcolor
        hsmat.blend_method = 'BLEND'
        hsmat.diffuse_color = (hsbgr, hsbgg, hsbgb, 1.0)
        
        # Remove default material
        hsmat.node_tree.nodes.remove(hsmat.node_tree.nodes.get('Principled BSDF')) #title of the existing node when materials.new
        hsmat_output = hsmat.node_tree.nodes.get('Material Output')
        # add transparent shader
        transparent = hsmat.node_tree.nodes.new('ShaderNodeBsdfTransparent') 
        transparent.location = (-10,380)
        transparent.inputs[0].default_value = (1, 1, 1, 1.0)
        # add emission shader
        emission = hsmat.node_tree.nodes.new('ShaderNodeEmission')
        emission.location = (-10,280)
        # add mix shader
        mixer = hsmat.node_tree.nodes.new('ShaderNodeMixShader')
        mixer.name = 'pca-hsalpha-mixer'
        mixer.label = 'PCA Alpha Mixer'
        mixer.inputs[0].default_value = 1.0
        mixer.location = (145,280)       
        # add rgb shader
        color = hsmat.node_tree.nodes.new('ShaderNodeRGB')
        color.name = 'pca-hscolor'
        color.label = 'PCA Hotspot Color'
        color.outputs[0].default_value = (hsbgr, hsbgg, hsbgb, 1.0)
        color.location = (-200,350)
        
        
        # link shaders
        hsmat.node_tree.links.new(mixer.outputs[0], hsmat_output.inputs[0])
        hsmat.node_tree.links.new(transparent.outputs[0], mixer.inputs[1])
        hsmat.node_tree.links.new(emission.outputs[0], mixer.inputs[2])
        hsmat.node_tree.links.new(color.outputs[0], emission.inputs[0])
        
        obj.active_material = hsmat
              
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        return context.window_manager.invoke_props_dialog(self)
        



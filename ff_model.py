import bpy
import os
from bpy import context as context
from . ff_sk import SkZeroAll_OT_Operator,SkAnimateAll_OT_Operator,SkBindToBone_OT_Operator


def isTexIssue(texImage):
    ''' texImage is actually node
    function will return True if files doesn't exists on disk
    '''
    #filepath = texImage.image.filepath
    #filename = texImage.image.name
    if texImage.image != None:
        actualFile = bpy.path.abspath(texImage.image.filepath)
        if not os.path.exists(actualFile):
            return True
        else:
            return False
        #directory = os.path.dirname(actualFile)
        #basefile = os.path.basename(actualFile)
    else:
        return False

class SelectHalfMesh_OT_Operator (bpy.types.Operator):
    '''Select half mesh vertices'''
    bl_idname = "ffgen.select_half"
    bl_label = "ffgen_SelectHalfMesh"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.active_object.type=='MESH' ) and ( context.object.mode=='OBJECT' or context.object.mode == 'EDIT')):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        if obj.type == 'MESH':
            bpy.ops.object.mode_set(mode = 'EDIT')

            if obj.data.total_vert_sel > 0:
                bpy.ops.mesh.select_all() # select none
                #bpy.ops.mesh.select_all() # selecting all

            bpy.ops.object.mode_set(mode = 'OBJECT')
            selected_idx = [i.index for i in obj.data.vertices if i.select]
            # get locations
            # ob.matrix_world = full matrix.
            world_coordinates = []
            for each in obj.data.vertices:
                point = each.co
                # world_coord = point * ob.matrix_world
                #world_coord = obj.matrix_world * point
                if each.co[0] < -0.001:
                    each.select = True
            bpy.ops.object.mode_set(mode = 'EDIT')
            self.report({'INFO'}, "Done")
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class ReMirror_OT_Operator (bpy.types.Operator):
    '''Delete Half Mesh and Apply Mirror Modifier'''
    bl_idname = "ffgen.re_mirror"
    bl_label = "ffgen_ReMirror"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.active_object.type=='MESH' ) and (context.object.mode=='OBJECT' or context.object.mode == 'EDIT')):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        if obj.type == 'MESH':
            bpy.ops.object.mode_set(mode = 'EDIT')

            if obj.data.total_vert_sel > 0:
                bpy.ops.mesh.select_all() # select none
                #bpy.ops.mesh.select_all() # selecting all

            bpy.ops.object.mode_set(mode = 'OBJECT')
            selected_idx = [i.index for i in obj.data.vertices if i.select]
            # get locations
            # ob.matrix_world = full matrix.
            world_coordinates = []
            for each in obj.data.vertices:
                point = each.co
                # world_coord = point * ob.matrix_world
                #world_coord = obj.matrix_world * point
                if each.co[0] < -0.001:
                    each.select = True
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_add(type='MIRROR')
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}

class FindMissingFiles_OT_Operator (bpy.types.Operator):
    '''Find Missing Files In Selected Objects\nIf Nothing is selected, whole scene checked'''
    bl_idname = "ffgen.find_missing_files"
    bl_label = "ffgen_FindMissingFiles"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            return (1)
        else:
            return(0)
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) == 0:
            objs = bpy.data.objects
        # NOW ITERATING OBJECTS
        for o in objs:
            # Iterate over all of the current object's material slots
            print ("INSPECTING OBJECT: ",o.name)
            for m in o.material_slots:
                print ("INSPECTING MATERIAL: ",m.name)
                if m.material and m.material.use_nodes:
                    # Iterate over all the current material's texture slots
                    #for t in m.material.texture_slots:
                    for n in m.material.node_tree.nodes:
                        # If this is an image texture, with an active image append its name to the list
                        #if t and t.texture.type == 'IMAGE' and t.texture.image:
                        #    imageTextures.append( t.texture.image.name )
                        if n.type == 'TEX_IMAGE':
                            r = isTexIssue(n)
                            if r:
                                print ("ISSUE:",bpy.path.abspath(n.image.filepath))
                        elif n.type == 'GROUP':
                            for each in n.node_tree.nodes:
                                if each.type == 'TEX_IMAGE':
                                    r = isTexIssue(each)
                                    if r:
                                        print ("ISSUE:",bpy.path.abspath(each.image.filepath))
            self.report({'INFO'}, "Please check console")
        return{"FINISHED"}

class FixDuplicateMaterials_OT_Operator (bpy.types.Operator):
    '''if object 1 using "wood" and object 2 using "wood.001"\nScript will replace all "wood.001" slots with "wood"\nworks on scene materials'''
    bl_idname = "ffgen.fix_duplicate_materials"
    bl_label = "ffgen_FixDuplicateMaterials"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            return (1)
        else:
            return(0)
    def execute(self, context):
        mat_list = bpy.data.materials
        for o in bpy.data.objects:
            for s in o.material_slots:
                if s.material.name[-3:].isnumeric():
                    # the last 3 characters are numbers
                    if s.material.name[:-4] in mat_list:
                        # there is a material without the numeric extension so use it
                        s.material = mat_list[s.material.name[:-4]]
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class FfPollGen():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    @classmethod
    def poll(cls, context):
        return(context.scene.ff_general == True)

class FF_PT_Model(FfPollGen, bpy.types.Panel):
    bl_idname = "FF_PT_Model"
    bl_label = "Miscellaneous"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # testValue = 5

    def draw(self, context):
        skSrcObj = context.selected_objects[0]
        skb = 0
        if skSrcObj.type == 'MESH':
            sk = skSrcObj.data.shape_keys
            if sk:
                skb = sk.key_blocks
                skb = len(skb) - 1
        layout = self.layout

        # Modeling
        box_rg = layout.box()
        col = box_rg.column(align = True)
        col.label(text='Modeling Helpers')
        row = col.row(align = True)
        row.operator("ffgen.select_half", text="Select Half")
        row.operator("ffgen.re_mirror", text="Re-Mirror ")
        # TEXTURE / SHADING
        col1 = box_rg.column(align = True)
        col1.label(text='TEXTURE / SHADING')
        row = col1.row(align = True)
        row.operator("ffgen.find_missing_files", text="Find Missing Files")
        row = col1.row(align = True)
        row.operator("ffgen.fix_duplicate_materials", text="Fix Duplicate Mats")
        # SHAPEKEYS
        col2 = box_rg.column(align = True)
        col2.label(text='Shapekey Helpers')
        row = col2.row(align = True)
        row.operator("ffgen.sk_zero_all", text="Zero All")
        row.operator("ffgen.sk_animate_all", text="Animate All")
        # row = col2.row(align = True)
        # row.prop(bpy.context.scene,"ff_skFilter",text="filter")
        col2 = box_rg.column(align = True)
        col2.label(text='Bind Shapekeys To Bones(Classic)')
        row = col2.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"sk_filterStr",text="filter")
        row = col2.row(align = True)
        row.label(text="Info: %s Shapekeys Count:%s"%(skSrcObj.name,skb))
        # row = col2.row(align = True)
        # row.label(text="Info2: %s "%(self.testValue))
        row = col2.row(align = True)
        row.operator("ffgen.sk_bind_to_bone", text="Bind Shapekeys")


def UpdatedFunction(self, context):
    print ("Updating Function")
    print (self.sk_filterStr)
    # FF_PT_Model.testValue = self.sk_filterStr
    return
# from . ff_model import MyPropertyGroup

class FfModelingPropGrp(bpy.types.PropertyGroup):
    sk_filterStr = bpy.props.StringProperty(name ="Empty Filter will bind all shapekeys to selected Bone \nAfter changing filter text, hit enter key to refresh",default='',update=UpdatedFunction)
    # custom_Boolean = bpy.props.BoolProperty(update = UpdatedFunction)

bpy.utils.register_class(FfModelingPropGrp)

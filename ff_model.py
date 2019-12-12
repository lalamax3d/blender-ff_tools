import bpy

from bpy import context as context
from . ff_sk import SkZeroAll_OT_Operator,SkAnimateAll_OT_Operator,SkBindToBone_OT_Operator

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
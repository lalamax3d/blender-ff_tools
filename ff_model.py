import bpy

from bpy import context as context


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

    def draw(self, context):
        active_obj = context.active_object
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
        row.prop(bpy.context.scene,"ff_skFilter",text="filter")
        row = col2.row(align = True)
        row.operator("ffgen.re_mirror", text="Zero All")
        row.operator("ffgen.re_mirror", text="Animate All")
        row = col2.row(align = True)
        row.prop(bpy.context.scene.my_prop_grp,"custom_String",text="filter")
        row.prop(bpy.context.scene.my_prop_grp,"custom_Boolean",text="cb")


def UpdatedFunction(self, context):
    print ("here")
    # print (context)
    print (self.custom_String)
    print (context.scene.ff_skFilter)
    return
# from . ff_model import MyPropertyGroup

class MyPropertyGroup(bpy.types.PropertyGroup):
    custom_String = bpy.props.StringProperty(name ="My String",default='django',update=UpdatedFunction)
    custom_Boolean = bpy.props.BoolProperty(update = UpdatedFunction)

bpy.utils.register_class(MyPropertyGroup)
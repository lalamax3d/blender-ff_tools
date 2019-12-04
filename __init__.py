# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "FF_Tools",
    "author" : "lalamax3d",
    "description" : "simple tools for myself",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 3),
    "location" : "View3D",
    "warning" : "",
    "category" : "Animation"
}

import bpy
from bpy import context as context

from . ff_model import SelectHalfMesh_OT_Operator, ReMirror_OT_Operator, FF_PT_Model
from . ff_rig import UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator, exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator, FF_PT_Rig
from . ff_anim import CopyIklegs_OT_Operator, CopyIkArms_OT_Operator, KeySelectionOp_OT_Operator, KeyDeletionOp_OT_Operator, FF_PT_Anim

def UpdatedFunction(self, context):
    print ("here")
    print (context)
    print (self.custom_String)
    return
# from . ff_model import MyPropertyGroup

class MyPropertyGroup(bpy.types.PropertyGroup):
    custom_String = bpy.props.StringProperty(name ="My String",default='django',update=UpdatedFunction)
    custom_Boolean = bpy.props.BoolProperty(update = UpdatedFunction)

bpy.utils.register_class(MyPropertyGroup)

# VARIABLES - globals for GUI button presses
bpy.types.Scene.ff_general = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_rigging = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_anim = bpy.props.BoolProperty(default=False)

bpy.types.Scene.ff_skFilter = bpy.props.StringProperty(default='search shape')
bpy.types.Scene.ff_anim_kr = bpy.props.IntProperty(default=4,min=2,max=9,step=1)

bpy.types.Scene.my_prop_grp = bpy.props.PointerProperty(type=MyPropertyGroup)





# MAIN PANEL CONTROL
class FF_PT_Panel(bpy.types.Panel):
    bl_idname = "FF_PT_Panel"
    bl_label = "Film Factory Tools"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self,context):
        #active_obj = context.active_object
        layout = self.layout

        col = layout.column(align=1)
        row = col.row(align = True)
        row.prop(bpy.context.scene,"ff_general",text="Misc",icon="EDITMODE_HLT")
        row.prop(bpy.context.scene,"ff_rigging",text="Rigg",icon="ARMATURE_DATA")
        row.prop(bpy.context.scene,"ff_anim",text="Anim",icon="POSE_HLT")

classes = (
        SelectHalfMesh_OT_Operator,ReMirror_OT_Operator,
        UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator,
        exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator,
        CopyIkArms_OT_Operator, CopyIklegs_OT_Operator,
        KeySelectionOp_OT_Operator,KeyDeletionOp_OT_Operator,
        FF_PT_Panel, FF_PT_Model, FF_PT_Rig, FF_PT_Anim)

register,unregister = bpy.utils.register_classes_factory(classes)

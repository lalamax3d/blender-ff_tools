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

from . ff_model import FfModelingPropGrp
from . ff_anim import FfAnimPropGrp
from . ff_model import SelectHalfMesh_OT_Operator, ReMirror_OT_Operator, FindMissingFiles_OT_Operator, FixDuplicateMaterials_OT_Operator, FF_PT_Model
from . ff_facecap import FfFaceCapPropGrp
from . ff_rig import UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator, SetQuatRotations_OT_Operator , exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator, FF_PT_Rig
from . ff_anim import CopyIklegs_OT_Operator, CopyIkArms_OT_Operator, KeySelectionOp_OT_Operator, KeyDeletionOp_OT_Operator, FF_PT_Anim
from . ff_anim import EnableFcurveModifers_OT_Operator, EnableFcurveModifersAll_OT_Operator, DisableFcurveModifers_OT_Operator, DisableFcurveModifersAll_OT_Operator
from . ff_anim import MirrorFcurveModifers_OT_Operator, CopyFcurveModifiers_OT_Operator
from . ff_rend import setupPrismOutput_OT_Operator,setupPrismPreview_OT_Operator, setupBackGroundRender_OT_Operator, FF_PT_Rend


from . ff_sk import SkZeroAll_OT_Operator,SkAnimateAll_OT_Operator,SkBindToBone_OT_Operator
from . ff_facecap import ReadFaceCapJson_OT_Operator, SetupFcBoneProps_OT_Operator, SetupFcSingleDriver_OT_Operator, SetupFcDrivers_OT_Operator
# VARIABLES - globals for GUI button presses
bpy.types.Scene.ff_general = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_rigging = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_anim = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_facecap = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_rend = bpy.props.BoolProperty(default=False)

# bpy.types.Scene.ff_skFilter = bpy.props.StringProperty(default='search shape')
bpy.types.Scene.ff_anim_kr = bpy.props.IntProperty(default=4,min=2,max=9,step=1)

# below line is special
bpy.types.Scene.ff_model_prop_grp = bpy.props.PointerProperty(type=FfModelingPropGrp)
bpy.types.Scene.ff_anim_prop_grp = bpy.props.PointerProperty(type=FfAnimPropGrp)
bpy.types.Scene.ff_rig_prop_grp = bpy.props.PointerProperty(type=FfFaceCapPropGrp)





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
        row.prop(bpy.context.scene,"ff_rend",text="Rend",icon="IMAGE_PLANE")

classes = (
        SelectHalfMesh_OT_Operator, ReMirror_OT_Operator, FindMissingFiles_OT_Operator, FixDuplicateMaterials_OT_Operator,
        SkZeroAll_OT_Operator, SkAnimateAll_OT_Operator, SkBindToBone_OT_Operator,
        UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator,SetQuatRotations_OT_Operator,
        exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator,
        CopyIkArms_OT_Operator, CopyIklegs_OT_Operator,
        KeySelectionOp_OT_Operator,KeyDeletionOp_OT_Operator,
        EnableFcurveModifers_OT_Operator,EnableFcurveModifersAll_OT_Operator,
        DisableFcurveModifers_OT_Operator, DisableFcurveModifersAll_OT_Operator,
        MirrorFcurveModifers_OT_Operator, CopyFcurveModifiers_OT_Operator, 
        ReadFaceCapJson_OT_Operator, SetupFcBoneProps_OT_Operator,SetupFcSingleDriver_OT_Operator,SetupFcDrivers_OT_Operator,
        setupPrismOutput_OT_Operator, setupPrismPreview_OT_Operator, setupBackGroundRender_OT_Operator,
        FF_PT_Panel, FF_PT_Model, FF_PT_Rig, FF_PT_Anim, FF_PT_Rend)

register,unregister = bpy.utils.register_classes_factory(classes)

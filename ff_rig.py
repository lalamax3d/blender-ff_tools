import bpy
from bpy import context as context

from . ff_drivers import importDriversFromJson, exportDriversToJson

def countRigifyBones():
    # assume rig object is selected
    rig = context.active_object
    print(str(len(rig.pose.bones)) + " bones")

def getOppositeCntShapeByName(cntName):
    if cntName.find(".R") != -1:
        cntName.replace(".R",".L")
    elif cntName.find(".L") != -1:
        cntName.replace(".L",".R")
    else:
        pass
    return cntName

def updateCntShapesOnOneSide(side=".R"):
    #opp = ""
    if side==".R":
        opp = ".L"
    else:
        opp = ".R"
    rig = bpy.context.active_object
    print ("i m here..")
    for pbone in rig.pose.bones:
        if pbone.custom_shape != None and pbone.custom_shape.name.find(side) != -1:
            newName = pbone.custom_shape.name.replace(side,".L")
            newObj = bpy.data.objects[newName]
            print(pbone.custom_shape.name + " >> " + newObj.name)
            pbone.custom_shape = newObj
def selectCntObjsOnOneSide(side=".R"):
    so = bpy.context.selected_objects
    # clear selection ( none )
    bpy.ops.object.select_all(action='TOGGLE')
    for each in so:
        if each.name.find(side) != -1:
            each.select = True
class UseSingleSideControls_OT_Operator (bpy.types.Operator):
    '''Update all Right side control bones to use left side shapes as well'''

    bl_idname = "ffrig.use_single_side_controls"
    bl_label = "ffrig_Use_Single_Side_Controls"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((pollCheckArmatureObject(context.object)) and ((context.object.mode =="POSE") or (context.object.mode =="OBJECT"))):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        self.report({'INFO'}, "Changing all 'R' Cnt shapes to 'L' Cnt shape")
        updateCntShapesOnOneSide()
        return{"FINISHED"}
class SelectOneSidedObjects_OT_Operator (bpy.types.Operator):
    '''Update all Right side control bones to use left side shapes as well'''

    bl_idname = "ffrig.select_one_sided_objects"
    bl_label = "ffrig_SelectOneSidedObjects"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((pollCheckMeshObject(context.object)) and context.object.mode=='OBJECT'):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        self.report({'INFO'}, "Updating Selection.")
        selectCntObjsOnOneSide()
        return{"FINISHED"}

class SetEulerRotations_OT_Operator (bpy.types.Operator):
    '''Selected Pose Bones to Euler'''
    bl_idname = "ffrig.set_euler_rotations"
    bl_label = "ffrig_EulerRotationsOnSelectedPoseBones"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((pollCheckArmatureObject(context.object)) and (context.object.mode =="POSE") and (len(context.selected_pose_bones) > 0)):
                return (1)
        else:
            return(0)

    def execute(self, context):
        obj = bpy.context.object
        pBones = bpy.context.selected_pose_bones
        print (pBones)
        for pbone in pBones:
            pbone.rotation_mode = 'ZXY'
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class exportDriversToJson_OT_Operator(bpy.types.Operator):
    bl_idname = "ffrig.export_drivers_json"
    bl_label = "FF Export Drivers To Json"
    bl_description = "FF Export Drivers To Json"

    def execute(self, context):
        exportDriversToJson()
        return {'FINISHED'}
class importDriversFromJson_OT_Operator(bpy.types.Operator):
    bl_idname = "ffrig.import_drivers_json"
    bl_label = "FF Import Drivers From Json"
    bl_description = "FF Import Drivers From Json"

    def execute(self, context):
        importDriversFromJson()
        return {'FINISHED'}
class FfPollRig():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    @classmethod
    def poll(cls, context):
        return(context.scene.ff_rigging == True)
def pollCheckMeshObject(obj):
    ''' check to see if mesh object is selected'''
    try:
        if obj.type=='MESH':
            return(1)
    except:
        return(0)
def pollCheckArmatureObject(obj):
    ''' check to see if armature object is selected'''
    try:
        if obj.type=='ARMATURE':
            return(1)
    except:
        return(0)

class FF_PT_Rig(FfPollRig, bpy.types.Panel):
    bl_idname = "FF_PT_Rig"
    bl_label = "Rigging"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        #active_obj = context.active_object
        layout = self.layout

        # new stuff
        box = layout.box()
        col = box.column(align = True)
        col.label(text='Rigify')
        row = col.row(align = True)
        row.operator("ffrig.use_single_side_controls", text="Use One Sided CNTs")
        row = col.row(align = True)
        row.operator("ffrig.select_one_sided_objects", text="Select One Sided CNT Objs")
        row = col.row(align = True)
        row.operator("ffrig.set_euler_rotations", text="Set Euler Rotations")
        # drivers
        col2 = box.column(align = True)
        col2.label(text='Drivers')
        row2 = col2.row(align = True)
        row2.operator("ffrig.import_drivers_json", text="Import")
        row2.operator("ffrig.export_drivers_json",text="Export")

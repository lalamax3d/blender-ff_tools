import bpy
from bpy import context as context



def keySelection(step):
    ''' reduces key on selectedBone by step '''
    obj = bpy.context.object
    bone = bpy.context.active_pose_bone
    action = obj.animation_data.action

    grp = action.groups[bone.name]

    # deselect all keyframes
    #bpy.ops.graph.select_all_toggle(invert=False)

    for chan in grp.channels:
        kfs = chan.keyframe_points
        #for kf in kfs:
            #print (kf.co[0])
        for i in range(0,len(kfs)):
            if i % step == 0:
                kfs[i].select_control_point = False
                #print (kfs[i].co[0])
            else:
                kfs[i].select_control_point = True


        #bpy.ops.graph.delete()

    # chan.keyframe_delete(chan.data_path,index=-1,frame = bpy.context.scene.frame_current,group = grp.name)
    # i checked later on and below works on selected bone, current time
    # bpy.ops.anim.keyframe_delete(type='Rotation')
# APPROACH
#can be done in two ways, just clean up action ( empty channels )
#or
#can active pose bones, channels names > fcurves > then remove those

def cleanEmptyChannels():
    ''' delete all channels which have single keyframe
        from selected pose bones in current action '''
    obj = bpy.context.object
    bone = bpy.context.active_pose_bone
    action = obj.animation_data.action
    fcurves = obj.animation_data.action.fcurves
    grp = action.groups[bone.name]

    # deselect all keyframes
    #bpy.ops.graph.select_all_toggle(invert=False)

    for chan in grp.channels:
        kfs = chan.keyframe_points
        if len(kfs) == 1:
            print ("Delete Channel")
            #bpy.ops.anim.channels_delete()
            # OR

            #fcu = fcurves[1] # for instance, you would need to loop over all and check data_path and array_index in real code
            fcurves.remove(chan)

def keyDeletion(step):
    ''' delete key on selectedBone by step '''
    obj = bpy.context.object
    bone = bpy.context.active_pose_bone

    action = obj.animation_data.action
    scene = bpy.context.scene
    # deselect all keyframes
    #bpy.ops.graph.select_all_toggle(invert=False)

    for i in range(scene.frame_start,scene.frame_end):
        if i % step != 0:
            scene.frame_set(i)
            bpy.ops.anim.keyframe_delete(type='Rotation')
            bpy.ops.anim.keyframe_delete(type='Location')

# OPERATORS HERE


class CopyIklegs_OT_Operator (bpy.types.Operator):
    '''Copy ik legs to fk legs per frame'''
    bl_idname = "ffbody.copy_ik_legs"
    bl_label = "ffbody_copyIkLegs"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and context.object.type =="ARMATURE" and ('rig_id' in context.object.data)):
                return (1)
        else:
            return(0)

    def execute(self, context):
        rigAO = bpy.context.object # assuming rigify rig
        ikBones = [ rigAO.pose.bones["foot_ik.R"], rigAO.pose.bones["foot_ik.L"]]
        fkBones = [rigAO.pose.bones["foot.R"], rigAO.pose.bones["foot.L"]]

        # goto pose mode if not already
        bpy.ops.object.mode_set(mode='POSE')
        # select ik bones, so keys goes there
        bpy.ops.pose.select_all(action='DESELECT')
        for each in ikBones:
            each.bone.select = True

        scene = bpy.context.scene
        for i in range(scene.frame_start,scene.frame_end):
            scene.frame_set(i)
            ikBones[0].matrix = fkBones[0].matrix.copy()
            ikBones[1].matrix = fkBones[1].matrix.copy()
            bpy.ops.anim.keyframe_insert(type='LocRot')
            print ("frame "+ str(i) + "keyframe set for " + ikBones[0].name)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class CopyIkArms_OT_Operator (bpy.types.Operator):
    '''Copy ik legs to fk arms per frame'''
    bl_idname = "ffbody.copy_ik_arms"
    bl_label = "ffbody_copyIkArms"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and context.object.type =="ARMATURE" and ('rig_id' in context.object.data)):
                return (1)
        else:
            return(0)

    def execute(self, context):
        rigAO = bpy.context.object # assuming rigify rig
        ikBones = [rigAO.pose.bones["hand_ik.R"], rigAO.pose.bones["hand_ik.L"]]
        fkBones = [rigAO.pose.bones["hand.R"], rigAO.pose.bones["hand.L"]]

        # goto pose mode if not already
        bpy.ops.object.mode_set(mode='POSE')
        # select ik bones, so keys goes there
        bpy.ops.pose.select_all(action='DESELECT')
        for each in ikBones:
            each.bone.select = True

        scene = bpy.context.scene
        for i in range(scene.frame_start,scene.frame_end):
            scene.frame_set(i)
            ikBones[0].matrix = fkBones[0].matrix.copy()
            ikBones[1].matrix = fkBones[1].matrix.copy()
            bpy.ops.anim.keyframe_insert(type='LocRot')
            print ("frame "+ str(i) + "keyframe set for " + ikBones[0].name)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class KeySelectionOp_OT_Operator (bpy.types.Operator):
    '''Select keyframes on selected bones in pose mode'''
    bl_idname = "ffbody.key_selection"
    bl_label = "ffbody_keySelection"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ( (context.object) and context.object.type =="ARMATURE" and context.object.mode == "POSE" and context.selected_pose_bones):
                return (1)
        else:
            return(0)

    def execute(self, context):
        steping = bpy.context.scene.ff_anim_kr
        keySelection(steping)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class KeyDeletionOp_OT_Operator (bpy.types.Operator):
    '''Delete keyframes on selected bones in pose mode'''
    bl_idname = "ffbody.key_deletion"
    bl_label = "ffbody_keyDeletion"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and context.object.type =="ARMATURE" and context.object.mode == "POSE" and context.selected_pose_bones):
                return (1)
        else:
            return(0)

    def execute(self, context):
        steping = bpy.context.scene.ff_anim_kr
        keyDeletion(steping)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}

class FfPollMoCap():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    @classmethod
    def poll(cls, context):
        return(context.scene.ff_anim == True)

class FF_PT_Anim(FfPollMoCap, bpy.types.Panel):
    bl_idname = "FF_PT_Anim"
    bl_label = "Animation"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        active_obj = context.active_object
        layout = self.layout
        # new stuff
        box = layout.box()
        col = box.column(align = True)
        col.label(text='MotionCapture')
        row = col.row(align = True)
        row.operator("ffbody.copy_ik_legs",text="Snap Ik Legs")
        row.operator("ffbody.copy_ik_arms",text="Snap Ik Arms")

        box = layout.box()
        col = box.column(align = True)
        col.label(text='Key Reduction')
        row = col.row(align = True)
        row.prop(bpy.context.scene,"ff_anim_kr",text="Steps")
        row = col.row(align = True)
        row.operator("ffbody.key_selection", text="Select keyframes")
        row = col.row(align = True)
        row.operator("ffbody.key_deletion", text="Delete Keyframes")

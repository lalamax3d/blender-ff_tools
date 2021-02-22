import bpy
from bpy import context as context



def keySelection(step):
    ''' reduces key on selectedBone by step '''
    obj = bpy.context.object
    # try to get action keys 
    if obj.type == 'ARMATURE':
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
    if obj.type == 'MESH' and obj.data.shape_keys != None:
        action = obj.data.shape_keys.animation_data.action   
        for g in action.groups:
            for c in g.channels:
                kfs = c.keyframe_points
                #for kf in kfs:
                    #print (kf.co[0])
                for i in range(0,len(kfs)):
                    if i % step == 0:
                        kfs[i].select_control_point = False
                        #print (kfs[i].co[0])
                    else:
                        kfs[i].select_control_point = True
    
    # try normal objects selection 
    objs = obj = bpy.context.selected_objects
    for obj in objs:
        if obj.animation_data != None:
            action = obj.animation_data.action
            for g in action.groups:
                for c in g.channels:
                    kfs = c.keyframe_points
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



def getOppositeBone():
    bn = bpy.context.active_pose_bone
    if bn.name.find('.L') != -1:
        obn = bn.name.replace('.L','.R')
        ob = bpy.context.active_object.pose.bones.get(obn)
    elif bn.name.find('.R') != -1:
        obn = bn.name.replace('.R','.L')
        ob = bpy.context.active_object.pose.bones.get(obn)
    if ob:
        return ob
    else:
        return None
    
def setOppositeRotation():
    bn = bpy.context.active_pose_bone
    obn = getOppositeBone()
    if obn != None:
        obn.rotation_euler.x  = bn.rotation_euler.x #* (3.1415/180)
        obn.rotation_euler.y  = bn.rotation_euler.y #* (3.1415/180)
        obn.rotation_euler.z  = - bn.rotation_euler.z #* (3.1415/180)

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
            if (context.object):
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

class EnableFcurveModifers_OT_Operator (bpy.types.Operator):
    '''Enable Fcurve Modifiers on selected pose bones'''
    bl_idname = "ffbody.enable_fcurve_modifers"
    bl_label = "ffbody_enableFcurveModifers"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and (context.object.type =="ARMATURE")):
                return (1)
        else:
            return(0)

    def execute(self, context):
        for each in context.active_object.animation_data.action.fcurves:
            if len(each.modifiers) > 0:
                for mod in each.modifiers:
                    mod.active  = True
                    mod.mute = False
                    print (each.data_path)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class DisableFcurveModifers_OT_Operator (bpy.types.Operator):
    '''Disable Fcurve Modifiers on selected pose bones'''
    bl_idname = "ffbody.disable_fcurve_modifers"
    bl_label = "ffbody_disableFcurveModifers"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and (context.object.type =="ARMATURE")):
                return (1)
        else:
            return(0)

    def execute(self, context):
        for each in context.active_object.animation_data.action.fcurves:
            if len(each.modifiers) > 0:
                for mod in each.modifiers:
                    mod.active  = False
                    mod.mute = True
                    print (each.data_path)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class EnableFcurveModifersAll_OT_Operator (bpy.types.Operator):
    '''Enable Fcurve Modifiers on Current Action'''
    bl_idname = "ffbody.enable_fcurve_modifers_all"
    bl_label = "ffbody_enableFcurveModifersAll"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and (context.object.type =="ARMATURE")):
                return (1)
        else:
            return(0)

    def execute(self, context):
        for each in context.active_object.animation_data.action.fcurves:
            if len(each.modifiers) > 0:
                for mod in each.modifiers:
                    mod.active  = True
                    mod.mute = False
                    print (each.data_path)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class DisableFcurveModifersAll_OT_Operator (bpy.types.Operator):
    '''Disable Fcurve Modifiers on Current Action'''
    bl_idname = "ffbody.disable_fcurve_modifers_all"
    bl_label = "ffbody_disableFcurveModifersAll"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and (context.object.type =="ARMATURE")):
                return (1)
        else:
            return(0)

    def execute(self, context):
        for each in context.active_object.animation_data.action.fcurves:
            if len(each.modifiers) > 0:
                for mod in each.modifiers:
                    mod.active  = False
                    mod.mute = True
                    print (each.data_path)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}

class MirrorFcurveModifers_OT_Operator (bpy.types.Operator):
    '''Mirror Fcurve Modifiers of active Bone on opposite bone'''
    bl_idname = "ffbody.mirror_fcurve_modifers"
    bl_label = "ffbody_MirrorFcurveModifers"
    bl_options =  {"REGISTER","UNDO"}
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and (context.object.type =="ARMATURE")):
                return (1)
        else:
            return(0)

    def execute(self, context):
        bn = context.active_pose_bone    
        obn = getOppositeBone()
        action = context.active_object.animation_data.action
        groups = action.groups
        fcurves = action.fcurves
        #print (len(groups))
        #print (len(fcurves))
        g = groups[bn.name]
        channels = g.channels # precise 3 fcurves :D
        og = groups[obn.name]
        ochannels = og.channels
        
        #for fc in channels:
        for i in range(0,3):
            fc1 = channels[i]
            fc2 = ochannels[i]
            # assumming single modifier of my typical need here (very bad)
            if len(fc1.modifiers) > 0:
                print ('Src Data Path:', fc1.data_path,i)
                print ('Tar Data Path:', fc2.data_path,i)
                m1 = fc1.modifiers[0]
                m2 = fc2.modifiers[0]
                print ('Additive', m1.use_additive)
                print ('Amplitude', round(m1.amplitude,2), 'Tar:', round(m2.amplitude,2))
                print ('Phase Multiplier', round(m1.phase_multiplier,2), 'Tar:', round(m2.phase_multiplier,2))
                print ('Phase Offset', round(m1.phase_offset,2), 'Tar:', round(m2.phase_offset,2))
                print ('Value Offset', round(m1.value_offset,2), 'Tar:', round(m2.value_offset,2))
                m2.amplitude = m1.amplitude
                m2.phase_multiplier = m1.phase_multiplier
                m2.phase_offset = m1.phase_offset
                if (i == 2): # flip z values only
                    m2.value_offset = - m1.value_offset
                    m2.phase_offset = - m1.phase_offset - 3
                    print ('value_offset_fixed')
                
        print ("DONE")
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

        col = box.column(align = True)
        col.label(text='FCurveModifiers')
        row = col.row(align = True)
        row.operator("ffbody.enable_fcurve_modifers",text="En F Modifiers(sel)")
        row.operator("ffbody.disable_fcurve_modifers",text="Di F Modifiers(sel)")

        #col = box.column(align = True)
        #col.label(text='FCurveModifiers')
        row = col.row(align = True)
        row.operator("ffbody.enable_fcurve_modifers_all",text="En F Modifiers(All)")
        row.operator("ffbody.disable_fcurve_modifers_all",text="Di F Modifiers(All)")

        
        col = box.column(align = True)
        col.label(text='FCurve Mirror')
        row = col.row(align = True)
        row.operator("ffbody.mirror_fcurve_modifers",text="Mirror FCurve Mod Values")
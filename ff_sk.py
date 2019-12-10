import bpy
from bpy import context as context
fc_skList = [
'browInnerUp', 'browDown_L', 'browDown_R', 'browOuterUp_L', 'browOuterUp_R',
'eyeLookUp_L', 'eyeLookUp_R', 'eyeLookDown_L', 'eyeLookDown_R', 'eyeLookIn_L', 'eyeLookIn_R', 'eyeLookOut_L', 'eyeLookOut_R',
'eyeBlink_L', 'eyeBlink_R', 'eyeSquint_L', 'eyeSquint_R', 'eyeWide_L', 'eyeWide_R',
'cheekPuff', 'cheekSquint_L', 'cheekSquint_R', 'noseSneer_L', 'noseSneer_R',
'jawOpen', 'jawForward', 'jawLeft', 'jawRight', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight',
'mouthRollUpper', 'mouthRollLower', 'mouthShrugUpper', 'mouthShrugLower', 'mouthClose',
'mouthSmile_L', 'mouthSmile_R', 'mouthFrown_L', 'mouthFrown_R', 'mouthDimple_L', 'mouthDimple_R',
'mouthUpperUp_L', 'mouthUpperUp_R', 'mouthLowerDown_L', 'mouthLowerDown_R', 'mouthPress_L', 'mouthPress_R',
'mouthStretch_L', 'mouthStretch_R', 'tongueOut']


def addPropsInPbone():
    sk = obj.data.shape_keys
    skb = sk.key_blocks
    # TODO make sure, its workable with 2.81 by making property exportable
    for i in range(1,len(skb)):
        print(skb[i])
        pbone[skb[i].name]=0.0


def addDriversToShapeKeys():
    sk = obj.data.shape_keys
    skb = sk.key_blocks
    for i in range(1,len(skb)):
        #print(skb[i])
        #pbone[skb[i].name]=0.0
        data_path = "key_blocks[\"" + skb[i].name + "\"].value"
        print (data_path)
        dr = obj.data.shape_keys.driver_add(data_path)
        dr.driver.type='SCRIPTED'

        var = dr.driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = rig
        var.targets[0].data_path = "pose.bones[\""+pbone.name+"\"][\""+ skb[i].name +"\"]"
        print (var.targets[0].data_path)
        dr.driver.expression = "var"

#addPropsInPbone()
#addDriversToShapeKeys()


class SkZeroAll_OT_Operator (bpy.types.Operator):
    '''Reset All Shapekey values to zero'''
    bl_idname = "ffgen.sk_zero_all"
    bl_label = "ffgen_SkZeroAll"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if (context.active_object.type=='MESH') and (context.active_object.data.shape_keys !='None'):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        sk = obj.data.shape_keys
        if sk :
            skb = sk.key_blocks
            print ("Shape Key Blocks %s"% len(skb))
            for i in range(1,len(skb)):
                skb[i].value = 0
            self.report({'INFO'}, "Done")
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}

class SkAnimateAll_OT_Operator (bpy.types.Operator):
    '''Animate All Shapekey values to 1 for each frame(helpful for testing)'''
    bl_idname = "ffgen.sk_animate_all"
    bl_label = "ffgen_SkAnimateAll"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if  (context.active_object.type=='MESH') and (context.active_object.data.shape_keys !='None'):
                return (1)
        else:
            return(0)
    def execute(self, context):
        obj = context.object
        sk = obj.data.shape_keys
        if sk :
            skb = sk.key_blocks
            print ("Shape Key Blocks %s"% len(skb))
            for i in range(1,len(skb)):
                skb[i].value = 0
                skb[i].keyframe_insert("value",frame=i-1)
                skb[i].value = 1
                skb[i].keyframe_insert("value",frame=i)
                skb[i].value = 0
                skb[i].keyframe_insert("value",frame=i+1)
            self.report({'INFO'}, "Done")
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}

class SkBindToBone_OT_Operator (bpy.types.Operator):
    '''Create shapekey name property in selected pose bone and set expression on shapekey'''
    bl_idname = "ffgen.sk_bind_to_bone"
    bl_label = "ffgen_SkBindToBone"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if  (len(context.selected_objects)==2) and (context.selected_object[0].type=='MESH') and (context.active_object.type =='ARMATURE'):
                return (1)
        else:
            return(0)
    def execute(self, context):
        skSrcObj = context.selected_objects[0]
        armObj = context.active_object
        pbone = context.active_pose_bone
        sk = skSrcObj.data.shape_keys
        if sk :
            skb = sk.key_blocks
            print ("Shape Key Blocks %s"% len(skb))
            fs = bpy.context.scene.ff_model_prop_grp.sk_filterStr
            
            self.report({'INFO'}, "Done")
        else :
            self.report({'INFO'}, "No ShapeKeys Found")
        return{"FINISHED"}
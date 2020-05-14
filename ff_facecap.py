import bpy
from bpy import context as context

from . ff_drivers import importDriversFromJson, exportDriversToJson

data = None


def ReadFromJson():
    import json
    import os
    #obj = bpy.context.object
    infile = state().fc_activeJson
    print ("Json FOund:", os.path.isfile(state().fc_activeJson))
    with open(infile) as json_data:
        d = json.load(json_data)
    drivers = d['drivers']
    props = d['properties']
    state().fc_boneProps = str(len (props))
    state().fc_drivers = str(len (drivers))
    state().fc_aDriver = 0
    state().data = d

# clean / remove drivers ( setup by me ) helps to develope testing
def createBoneProp (bone,prop):
    ''' create property on bone if it doesn't exist already'''
    o = bpy.context.active_object # active object (assuming armature)
    b = o.pose.bones.get(bone) # get bone
    # create property if it doesn't exist
    if not b.get(prop):
        b[prop] = 0.5
        print ("Creating %s on Bone:%s"%(prop,bone))
    else:
        print ("Skipping %s creation on Bone:%s"%(prop,bone))

def createBasicPropertiesFromJson(jsondata):
    ''' read json, extract properties, creates whats needed'''
    properties = []
    for each in jsondata:
        for i in range(5,len(each)):
            vd = each[i]
            dp = vd['data_path']
            if dp.find('pose') != -1:
                print (each[0],vd['data_path'])
                properties.append(vd['data_path'])
    properties = list(set(properties))
    for each in properties:
        d = each.split('"')
        b = d[1]
        p = d[-2]
        createBoneProp(b,p)
class ReadFaceCapJson_OT_Operator (bpy.types.Operator):
    '''Read Drivers Json File'''
    bl_idname = "ffrig.read_facecap_json"
    bl_label = "ffrig_ReadFaceCapJson"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D':
            if context.object:
                return (1)
        else:
            return(0)

    def execute(self, context):
        ReadFromJson()
        return{"FINISHED"}

class SetupFcBoneProps_OT_Operator (bpy.types.Operator):
    '''Setup Bone Properties and Attributes'''
    bl_idname = "ffrig.setup_fc_bone_props"
    bl_label = "ffrig_SetupFcBoneProps"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D' and context.object:
            return (1)
        else:
            return(0)

    def execute(self, context):
        infile = state().fc_activeJson
        print ("Json FOund:", os.path.isfile(state().fc_activeJson))
        with open(infile) as json_data:
            d = json.load(json_data)
        drivers = d['drivers']
        createBasicPropertiesFromJson(drivers)
        return{"FINISHED"}
## TUNE VALUES OPERATOR HERE


class SetupFcSingleDriver_OT_Operator (bpy.types.Operator):
    '''Setup Single indexed driver'''
    bl_idname = "ffrig.setup_fc_single_driver"
    bl_label = "ffrig_SetupFcSingleDriver"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D' and context.object:
            return (1)
        else:
            return(0)

    def execute(self, context):

        return{"FINISHED"}

def UpdatedFunction(self, context):
    print("Updating Function")
    print(self.fc_activeJson)
    # FF_PT_Model.testValue = self.sk_filterStr
    return
# from . ff_model import MyPropertyGroup

def state():
    return bpy.context.scene.ff_rig_prop_grp

class FfFaceCapPropGrp(bpy.types.PropertyGroup):

    fc_activeJson: bpy.props.StringProperty(name="Reads Json Config \n Refresh", default='presets/data.json', update=UpdatedFunction)
    fc_boneProps: bpy.props.StringProperty(name="", default='')
    fc_drivers: bpy.props.StringProperty(name="", default='')
    fc_aDriver: bpy.props.IntProperty(default=0)

    selected_head: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH' and obj != bpy.context.object and obj.data.shape_keys != None,
        update=lambda self, ctx: state().update_source()
    )
    selected_eye: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH' and obj != bpy.context.object,
        update=lambda self, ctx: state().update_source()
    )
    invalid_selected_source: bpy.props.PointerProperty(
        type=bpy.types.Object,
    )
    source: bpy.props.PointerProperty(type=bpy.types.Object)
    target: bpy.props.PointerProperty(type=bpy.types.Object)

    def update_source(self):
        self.target = bpy.context.object
        if self.selected_head == None:
            print("NOTHING")
            return
        else:
            print ("SKIPPING")
            return


bpy.utils.register_class(FfFaceCapPropGrp)

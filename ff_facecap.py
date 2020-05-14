import bpy
from bpy import context as context

from . ff_drivers import importDriversFromJson, exportDriversToJson

data = None


def ReadFromJson():
    import json
    import os
    #obj = bpy.context.object
    infile = state().fc_activeJson
    print ("Json Found:", os.path.isfile(state().fc_activeJson), infile)
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
def loadPropertyValuesFromJson(props):
    o = bpy.context.active_object #assuming rig
    for each in props:
        b = each[0]
        p = each[1]
        v = each[2]
        bone = o.pose.bones.get(b)
        if bone.get(p):
            bone[p] = v #loading value in prop
            print ("Setting Bone %s param %s to value %f" %(b,p,v))
        else:
            print ("Skipping Bone %s param %s to value " %(b,p))
def setupDriver(dd):
    #TODO , make sure, ROtation is Euler XYZ
    o = bpy.context.active_object
    # get bone by name
    bone = o.pose.bones.get(dd[0])
    # add driver to prop on axis and wait for (scripted expression)
    d = bone.driver_add(dd[1],dd[2])
    # set variables
    print ("Starting ITEM")
    for i in range(5,len(dd)):
        vd = dd[i]
        print (i, '\t', vd)
        var = d.driver.variables.new()
        var.name = vd['name']
        var.type = vd['type'] # SINGLE_PROP OR TRANFORMS
        # depending on above type, process is different
        if var.type == 'SINGLE_PROP':
            var.targets[0].id_type = vd["id_type"] # KEY , TODO: can be object
            if var.targets[0].id_type == 'KEY' :

                # this is shapekey id from json
                idv = vd['id'].split('"')[1]
                # APPROACH: get that shape key id from scene

                #allKeys = bpy.data.shape_keys
                #sk = allKeys[idv]
                #var.targets[0].id = sk

                # above is issue. not necessary shape key exists so, get user head shape key
                # GET NEW SHAPE KEY FROM FFRIGPROPGROUP USER HEAD SHAPE KEY
                userHead = bpy.context.scene.ff_rig_prop_grp.selected_head
                sk = userHead.data.shape_keys.id_data
                var.targets[0].id = sk
                var.targets[0].data_path = vd['data_path']
            elif var.targets[0].id_type == 'OBJECT' :
                idv = vd['id'].split('"')[1]
                objects = bpy.data.objects
                obj = objects[idv]
                var.targets[0].id = obj
                var.targets[0].data_path = vd['data_path']
        elif var.type == 'TRANSFORMS':
            # in this case id_type is always OBJECT
            # var.targets[0].id_type = vd["id_type"]
            idv = vd['id'].split('"')[1]
            objects = bpy.data.objects
            obj = objects[idv]
            var.targets[0].id = obj
            var.targets[0].transform_space = vd['transform_space']
            var.targets[0].transform_type = vd['transform_type']
            if 'ROT' in var.targets[0].transform_type:
                var.targets[0].rotation_mode = vd['rotation_mode']
            #var.targets[0].data_path = vd['data_path']
    d.driver.type = dd[4] # set to scripted etc
    d.driver.expression = dd[3] # set expression
    print ("DONE")
class ReadFaceCapJson_OT_Operator (bpy.types.Operator):
    '''Read Drivers Json File'''
    bl_idname = "ffrig.read_facecap_json"
    bl_label = "ffrig_ReadFaceCapJson"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D' and context.object:
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
        import os,json
        infile = state().fc_activeJson
        print ("Json Used:", os.path.isfile(state().fc_activeJson))
        with open(infile) as json_data:
            d = json.load(json_data)
        drivers = d['drivers']
        props = d['properties']
        print ("Creating Required Properties")
        createBasicPropertiesFromJson(drivers)
        print ("Tuning Required Properties Values")
        loadPropertyValuesFromJson(props)
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
        import os,json
        infile = state().fc_activeJson
        print ("Json Found:",state().fc_activeJson)
        with open(infile) as json_data:
            d = json.load(json_data)
        drivers = d['drivers']
        driver = drivers[state().fc_aDriver]
        dd1 = driver[1]
        print (driver[0],'\t', driver[1])
        if dd1 != 'influence':
            #print (drivers[state().fc_aDriver])
            setupDriver(driver)
        else:
            print ("SKIPPING DRIVER AS ITS CONSTRAINT")
        return{"FINISHED"}
class SetupFcDrivers_OT_Operator (bpy.types.Operator):
    '''Setup Single indexed driver'''
    bl_idname = "ffrig.setup_fc_drivers"
    bl_label = "ffrig_SetupFcDrivers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D' and context.object:
            return (1)
        else:
            return(0)

    def execute(self, context):
        import os,json
        infile = state().fc_activeJson
        print ("Json Found:",state().fc_activeJson)
        with open(infile) as json_data:
            d = json.load(json_data)
        drivers = d['drivers']
        for driver in drivers:
            dd1 = driver[1]
            print (driver[0],'\t', driver[1])
            if dd1 != 'influence':
                #print (drivers[state().fc_aDriver])
                setupDriver(driver)
            else:
                print ("SKIPPING DRIVER AS ITS CONSTRAINT")
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
        poll=lambda self, obj: obj.type == 'EMPTY' and obj != bpy.context.object,
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

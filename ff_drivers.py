import bpy

def getDriversInfo():
    o = bpy.context.active_object
    drivers = o.animation_data.drivers
    data = []
    for each in drivers:
        dp = each.data_path
        if dp == 'pass_index':
            print ("SKIP")
        else:
            bone = dp.split('"')[1]
            prop = dp.split('.')[-1]
            axis = each.array_index
            print (bone, prop, axis)
            # now driver details ( expressions / variables / etc )
            dr = each.driver
            exp = dr.expression
            print (exp)
            type = dr.type # SCRIPTED / AVERAGE ETC
            print (type)
            item = [bone,prop,axis,exp,type]
            allVars = dr.variables
            print ("VARS: ",len(allVars))
            for v in allVars:
                vd = {}
                vd['name'] = v.name
                vd['type'] = v.type
                for target in v.targets:
                    vd['id_type'] = target.id_type # KEY
                    vd['id'] = str(target.id)
                    vd['data_path'] = target.data_path
                item.append(vd)
            data.append(item)
    return data




def exportDriversToJson():
    import json,os
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    outfile = os.path.join(desktop,'data.json')
    data = getDriversInfo()
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(list(data), f,  ensure_ascii=False, indent=4)



def setupDriver(dd):
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
        var.type = vd['type']
        var.targets[0].id_type = vd["id_type"] # KEY , TODO: can be object
        idv = vd['id'].split('"')[1]
        allKeys = bpy.data.shape_keys
        sk = allKeys[idv]
        var.targets[0].id = sk
        var.targets[0].data_path = vd['data_path']
    d.driver.type = dd[4] # set to scripted etc
    d.driver.expression = dd[3] # set expression
    print ("DONE")

def importDriversFromJson():
    import json,os
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    infile = os.path.join(desktop,'data.json')
    with open(infile) as json_data:
        d = json.load(json_data)
    for each in d:
        setupDriver(each)

# exportDriversToJson()
# importDriversFromJson()


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

# PROCESS
# save json ( best config )

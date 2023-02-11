import bpy
import os
from bpy import context as context
from . ff_sk import SkZeroAll_OT_Operator,SkAnimateAll_OT_Operator,SkBindToBone_OT_Operator
from bpy import context as C
from bpy import data as D

#Recursivly transverse layer_collection for a particular name

def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

# above function was taken from here:https://blender.stackexchange.com/questions/127403/change-active-collection

def updateSceneMatsNormalStrength(self,context):
    for mat in bpy.data.materials:
        ndt = mat.node_tree
        if ndt:
            nodes = mat.node_tree.nodes
            for node in nodes:
                if node.type=='NORMAL_MAP':
                    node.inputs[0].default_value = self.sceneMatsNormalStrength


def isTexIssue(texImage):
    ''' texImage is actually node
    function will return True if files doesn't exists on disk
    '''
    #filepath = texImage.image.filepath
    #filename = texImage.image.name
    if texImage.image != None:
        actualFile = bpy.path.abspath(texImage.image.filepath)
        if not os.path.exists(actualFile):
            return True
        else:
            return False
        #directory = os.path.dirname(actualFile)
        #basefile = os.path.basename(actualFile)
    else:
        return False

def makeAssetFromChildren(grpObj,alignPivotToBase=False,applyScale=True,applyRot=True):
    parentIsNull = grpObj.parent
    if parentIsNull == None:
        print ("Seems obj in world")
        # deselect everything
        bpy.ops.object.select_all(action='DESELECT')
        # selecting grpObj
        bpy.data.objects[grpObj.name].select_set(True)
        # selecting all children
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
        selObjs = bpy.context.selected_objects
        print (len(selObjs))
        bpy.ops.object.select_all(action='DESELECT')
        # now iterate selObjs and select only meshes
        for each in selObjs:
            if each.type == 'MESH':
                each.select_set(True)
        # now all meshes are selected.
        bpy.ops.object.join()
        newObj = bpy.context.active_object
        # check parent helper name to decide new name
        if grpObj.name.find('_grp') != -1:
            newObj.name = grpObj.name.split('_grp')[0]
        else:
            newObj.name = grpObj.name + "_obj"
        # now unparent with keep transform, then apply transform.
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        if applyScale:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if applyRot:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # now marking as an asset
        #bpy.ops.asset.mark()
        # now deselect
        bpy.ops.object.select_all(action='DESELECT')
    else:
        print ("This obj is under some heirarchy, Make sure..")
def makeAssetFromMeshAndChildren(grpObj,alignPivotToBase=False,applyScale=True,applyRot=True):
    parentIsNull = grpObj.parent
    if parentIsNull == None:
        print ("Seems obj in world")
        # deselect everything
        bpy.ops.object.select_all(action='DESELECT')
        # selecting grpObj
        bpy.data.objects[grpObj.name].select_set(True)
        # selecting all children
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        selObjs = bpy.context.selected_objects
        print (len(selObjs))
        bpy.ops.object.select_all(action='DESELECT')
        # now iterate selObjs and select only meshes
        for each in selObjs:
            if each.type == 'MESH':
                each.select_set(True)
        # now all meshes are selected.
        bpy.context.view_layer.objects.active=grpObj
        bpy.ops.object.join()
        newObj = bpy.context.active_object
        # check parent helper name to decide new name
        # if grpObj.name.find('_grp') != -1:
        #     newObj.name = grpObj.name.split('_grp')[0]
        # else:
        #     newObj.name = grpObj.name + "_obj"
        # now unparent with keep transform, then apply transform.
        #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        if applyScale:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if applyRot:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        # now marking as an asset
        #bpy.ops.asset.mark()
        # now deselect
        bpy.ops.object.select_all(action='DESELECT')
    else:
        print ("This obj is under some heirarchy, Make sure..")

class SelectHalfMesh_OT_Operator (bpy.types.Operator):
    '''Select half mesh vertices'''
    bl_idname = "ffgen.select_half"
    bl_label = "ffgen_SelectHalfMesh"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D' and context.active_object != None:
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
        if context.area.type=='VIEW_3D' and context.active_object != None:
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
class UpdateSceneMatsNormalMapStrength_OT_Operator (bpy.types.Operator):
    '''Find Missing Files In Selected Objects\nIf Nothing is selected, whole scene checked'''
    bl_idname = "ffgen.update_scene_mats_normal_map_strength"
    bl_label = "ffgen_UpdateSceneMatsNormalMapStrength"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            return (1)
        else:
            return(0)
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) == 0:
            objs = bpy.data.objects
        # NOW ITERATING OBJECTS
        for o in objs:
            # Iterate over all of the current object's material slots
            print ("INSPECTING OBJECT: ",o.name)
            for i in range(len(o.material_slots)):
                mat = o.material_slots[i].material
                if mat:
                    print ("INSPECTING MATERIAL: ",mat.name)
                    for n in mat.node_tree.nodes:
                        if n.type == 'NORMAL_MAP':
                            n.inputs[0].default_value = bpy.context.scene.ff_model_prop_grp.nor_strength
        self.report({'INFO'}, "Done")
        return{"FINISHED"}
        
class FindMissingFiles_OT_Operator (bpy.types.Operator):
    '''Find Missing Files In Selected Objects\nIf Nothing is selected, whole scene checked'''
    bl_idname = "ffgen.find_missing_files"
    bl_label = "ffgen_FindMissingFiles"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            return (1)
        else:
            return(0)
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) == 0:
            objs = bpy.data.objects
        # NOW ITERATING OBJECTS
        for o in objs:
            # Iterate over all of the current object's material slots
            print ("INSPECTING OBJECT: ",o.name)
            for m in o.material_slots:
                print ("INSPECTING MATERIAL: ",m.name)
                if m.material and m.material.use_nodes:
                    # Iterate over all the current material's texture slots
                    #for t in m.material.texture_slots:
                    for n in m.material.node_tree.nodes:
                        # If this is an image texture, with an active image append its name to the list
                        #if t and t.texture.type == 'IMAGE' and t.texture.image:
                        #    imageTextures.append( t.texture.image.name )
                        if n.type == 'TEX_IMAGE':
                            r = isTexIssue(n)
                            if r:
                                print ("ISSUE:",bpy.path.abspath(n.image.filepath))
                        elif n.type == 'GROUP':
                            for each in n.node_tree.nodes:
                                if each.type == 'TEX_IMAGE':
                                    r = isTexIssue(each)
                                    if r:
                                        print ("ISSUE:",bpy.path.abspath(each.image.filepath))
            self.report({'INFO'}, "Please check console")
        return{"FINISHED"}

class FixDuplicateMaterials_OT_Operator (bpy.types.Operator):
    '''if object 1 using "wood" and object 2 using "wood.001"\nScript will replace all "wood.001" slots with "wood"\nworks on scene materials'''
    bl_idname = "ffgen.fix_duplicate_materials"
    bl_label = "ffgen_FixDuplicateMaterials"
    bl_options =  {"REGISTER","UNDO"}

    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            return (1)
        else:
            return(0)
    def execute(self, context):
        mat_list = bpy.data.materials
        for o in bpy.data.objects:
            for s in o.material_slots:
                if s.material.name[-3:].isnumeric():
                    # the last 3 characters are numbers
                    if s.material.name[:-4] in mat_list:
                        # there is a material without the numeric extension so use it
                        s.material = mat_list[s.material.name[:-4]]
        else :
            self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class BulkImportClass_OT_Operator (bpy.types.Operator):
    '''import all files from subfolders'''
    bl_idname = "ffgen.bulk_import_sudirs_class"
    bl_label = "ffgen_BulkImportSubdirsClass"
    bl_options =  {"REGISTER","UNDO"}

    # @classmethod
    # def poll(cls,context):
    #     if context.area.type=='VIEW_3D':
    #         return (1)
    #     else:
    #         return(0)
    def execute(self, context):
        selObjects = context.selected_objects
        #bpy.ops.object.select_all(action='DESELECT')
        from pathlib import Path
        folder = Path(bpy.context.scene.ff_model_prop_grp.bulkImportDir)
        fileType = bpy.context.scene.ff_model_prop_grp.bulkImportFileType
        # folder = Path(r"C:\path\to\your\folder")
        fbx_files = [f for f in folder.glob("**/*."+fileType) if f.is_file()]
        for fbx_file in fbx_files:
            bpy.ops.object.select_all(action='DESELECT')

            # creating collection (named after the file)
            collectionName = str(fbx_file).split('/')[-1].split('.')[0]
            print ('collectionName', collectionName)
            # New Collection
            # bpy.ops.collection.create(name='Collection')
            my_coll = bpy.data.collections.new(collectionName)
            # Add collection to scene collection
            bpy.context.scene.collection.children.link(my_coll)
            print ("Creating Collection: ", collectionName)
            # making it active
            #Change the Active LayerCollection to 'My Collection'
            layer_collection = bpy.context.view_layer.layer_collection
            layerColl = recurLayerCollection(layer_collection, collectionName)
            bpy.context.view_layer.active_layer_collection = layerColl

            print ('Importing..>> ', fbx_file)
            bpy.ops.import_scene.fbx(filepath=str(fbx_file))
            

            

            # Get cube object
            # obj = bpy.context.scene.objects.get("Cube")

            # for obj in bpy.context.selected_objects:
            #     # obj.name = fbx_file.stem
            #     my_coll.objects.link(obj)
            # if obj:
                # Link the cube 
        
        return{"FINISHED"}
class UpdateSelectionFilterClass_OT_Operator (bpy.types.Operator):
    '''keep the specific class, deselect others'''
    bl_idname = "ffgen.update_selection_filter_class"
    bl_label = "ffgen_UpdateSelectionFilterClass"
    bl_options =  {"REGISTER","UNDO"}

    # @classmethod
    # def poll(cls,context):
    #     if context.area.type=='VIEW_3D':
    #         return (1)
    #     else:
    #         return(0)
    def execute(self, context):
        selObjects = context.selected_objects
        #bpy.ops.object.select_all(action='DESELECT')
        keepClass = bpy.context.scene.ff_model_prop_grp.sel_filterStr
        print (keepClass)
        for each in selObjects:
            if each.type != keepClass:
                each.select_set(False)
            #self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class UpdateDeselectionFilterClass_OT_Operator (bpy.types.Operator):
    '''ignore the specific class, deselect others'''
    bl_idname = "ffgen.update_deselection_filter_class"
    bl_label = "ffgen_UpdateDeselectionFilterClass"
    bl_options =  {"REGISTER","UNDO"}

    # @classmethod
    # def poll(cls,context):
    #     if context.area.type=='VIEW_3D':
    #         return (1)
    #     else:
    #         return(0)
    def execute(self, context):
        selObjects = context.selected_objects
        #bpy.ops.object.select_all(action='DESELECT')
        ignoreClass = bpy.context.scene.ff_model_prop_grp.sel_filterStr
        print (ignoreClass)
        for each in selObjects:
            if each.type == ignoreClass:
                each.select_set(False)
            #self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class CreateAssetsFromSelectionEmpty_OT_Operator (bpy.types.Operator):
    '''convert selected heirarchies to single meshes\n1-selecting child meshes n join\n2-apply rot/scale,unparent,keeptransform,rename'''
    bl_idname = "ffgen.create_assets_from_selection_empty"
    bl_label = "ffgen_CreateAssetsFromSelectionEmpty"
    bl_options =  {"REGISTER","UNDO"}

    # @classmethod
    # def poll(cls,context):
    #     if context.area.type=='VIEW_3D':
    #         return (1)
    #     else:
    #         return(0)
    def execute(self, context):
        selObjects = context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for each in selObjects:
            makeAssetFromChildren(each)
            #self.report({'INFO'}, "Select some mesh object")
        return{"FINISHED"}
class CreateAssetsFromSelectionMesh_OT_Operator (bpy.types.Operator):
    '''convert selected Mesh and related child objs\n1-selecting child meshes n join\n2-apply rot/scale'''
    bl_idname = "ffgen.create_assets_from_selection_mesh"
    bl_label = "ffgen_CreateAssetsFromSelectionMesh"
    bl_options =  {"REGISTER","UNDO"}

    # @classmethod
    # def poll(cls,context):
    #     if context.area.type=='VIEW_3D':
    #         return (1)
    #     else:
    #         return(0)
    def execute(self, context):
        selObjects = context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for each in selObjects:
            makeAssetFromMeshAndChildren(each)
            #self.report({'INFO'}, "Select some mesh object")
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
        #active_obj = context.active_object
        layout = self.layout

        # Modeling
        box_rg = layout.box()
        col = box_rg.column(align = True)
        col.label(text='Modeling Helpers')
        row = col.row(align = True)
        row.operator("ffgen.select_half", text="Select Half")
        row.operator("ffgen.re_mirror", text="Re-Mirror ")
        # TEXTURE / SHADING
        col1 = box_rg.column(align = True)
        col1.label(text='TEXTURE / SHADING')
        row = col1.row(align = True)
        row.operator("ffgen.find_missing_files", text="Find Missing Files")
        row = col1.row(align = True)
        row.operator("ffgen.fix_duplicate_materials", text="Fix Duplicate Mats")
        row = col1.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"nor_strength",text="normal value")
        row = col1.row(align = True)
        row.operator("ffgen.update_scene_mats_normal_map_strength", text="Scene")
        # row.operator("ffgen.create_assets_from_selection_mesh", text="Selection")
        # IMPORT BULK
        col2 = box_rg.column(align = True)
        col2.label(text='BULK IMPORT')
        row = col2.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"bulkImportDir",text="Path")
        row = col2.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"bulkImportFileType",text="FileType")
        row.operator("ffgen.bulk_import_sudirs_class", text="TEST RUN")
        # Selection
        col2 = box_rg.column(align = True)
        col2.label(text='Selection Filter')
        row = col2.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"sel_filterStr",text="filter")
        row = col2.row(align = True)
        row.operator("ffgen.update_selection_filter_class", text="Keep")
        row.operator("ffgen.update_deselection_filter_class", text="Ignore")
        # Assets
        col3 = box_rg.column(align = True)
        col3.label(text='Asset Creation')
        row = col3.row(align = True)
        row.operator("ffgen.create_assets_from_selection_empty", text="Heirarchy Under Empty")
        row.operator("ffgen.create_assets_from_selection_mesh", text="Heirarchy Under Mesh")
        # SHAPEKEYS
        col2 = box_rg.column(align = True)
        col2.label(text='Shapekey Helpers')
        row = col2.row(align = True)
        row.operator("ffgen.sk_zero_all", text="Zero All")
        row.operator("ffgen.sk_animate_all", text="Animate All")
        # row = col2.row(align = True)
        # row.prop(bpy.context.scene,"ff_skFilter",text="filter")
        col2 = box_rg.column(align = True)
        col2.label(text='Bind Shapekeys To Bones(Classic)')
        row = col2.row(align = True)
        row.prop(bpy.context.scene.ff_model_prop_grp,"sk_filterStr",text="filter")
        row = col2.row(align = True)
        # row.label(text="Info: %s Shapekeys Count:%s"%(skSrcObj.name,skb))
        # row = col2.row(align = True)
        # row.label(text="Info2: %s "%(self.testValue))
        row = col2.row(align = True)
        row.operator("ffgen.sk_bind_to_bone", text="Bind Shapekeys")


def UpdatedFunction(self, context):
    print ("Updating Function")
    print (self.sk_filterStr)
    # FF_PT_Model.testValue = self.sk_filterStr
    return
# from . ff_model import MyPropertyGroup

class FfModelingPropGrp(bpy.types.PropertyGroup):
    nor_strength: bpy.props.FloatProperty(default=.3)
    bulkImportDir : bpy.props.StringProperty(
        name ="file extension to import",
        default='/home/user/Downloads/',
        description="file extension to import",
        update=UpdatedFunction)
    bulkImportFileType : bpy.props.StringProperty(
        name ="file extension to import",
        default='fbx',
        description="file extension to import",
        update=UpdatedFunction)
    sel_filterStr : bpy.props.StringProperty(
        name ="filter to update selection \nAfter changing filter text, hit enter key to refresh",
        default='',
        description="selection filter",
        update=UpdatedFunction)
    sk_filterStr : bpy.props.StringProperty(
        name ="Empty Filter will bind all shapekeys to selected Bone \nAfter changing filter text, hit enter key to refresh",
        default='',
        description="shape key filter",
        update=UpdatedFunction)
    lockHead : bpy.props.BoolProperty(
        name="Enable or Disable",
        description="Lock the head position of the bone",
        default=False
        )
    # custom_Boolean = bpy.props.BoolProperty(update = UpdatedFunction)

bpy.utils.register_class(FfModelingPropGrp)

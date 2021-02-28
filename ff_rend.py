import bpy
from bpy import context as context

from pathlib import Path

import PrismCore

global pcore
pcore = PrismCore.PrismCore(app="Blender")


def renderPngPasses(context):
    ''' 
        this function will setup PNG and output passes as well
    '''
    pcore.projectPath
    pcore.scenePath # points to workflow dir
    pcore.shotPath # points to shots folder
    pcore.fileInPipeline(bpy.data.filepath)
    bfp = Path(bpy.data.filepath) 
    #filename = bpy.path.basename(bpy.data.filepath)
    filename = bfp.name
    filepath = bfp.parent
    shotdir = bfp.parent.parent.parent.parent
    if shotdir.is_dir():
        rendDir = shotdir.joinpath("Rendering","3dRender")
    # now get file version string
    verInfo = filename.split(pcore.filenameSeparator)[4] # .sequenceSeparato
    verFormat = pcore.versionFormat
    
    # create / output dir exists
    print ("RENDERING DIR EXPECTED PATH:", rendDir)
    print ("RENDERING DIR FOUND:", rendDir.exists())
    renderer = context.scene.render.engine #.split('_')[1]
    rendDir = rendDir.joinpath(renderer)
    rendDir.mkdir(parents=True, exist_ok=True) # will create EEVEE or CYCLES Directory

    # set relative path in output (main area)
    #fo = C.scene.render.filepath
    #bpy.path.abspath, to replace os.path.abspath
    #bpy.path.relpath, to replace os.path.relpath
    context.scene.render.filepath = rendDir.as_posix() + '/'+verInfo+'/beauty/image_'

    # remove all fileoutput nodes in comp area
    outputNodes = [x for x in context.scene.node_tree.nodes if x.type == 'OUTPUT_FILE']
    print ('OUTPUT NODES COUNT:', len(outputNodes))
    for node in outputNodes:
        context.scene.node_tree.nodes.remove(node)
    # setup new output comp nodes in comp area
    #n = bpy.context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
    # set new node location >> n.location = ((50,50))
    # Get Render Layer
    rendLyrNodes = [x for x in context.scene.node_tree.nodes if x.type == 'R_LAYERS']
    if len(rendLyrNodes) ==1:
        rendLyrNode = rendLyrNodes[0]
    else:
        #create new render layer node
        pass
    # get output passes list from node or blender
    #rendLyrNode.outputs # all possible passes here (todo)
    tree = context.scene.node_tree
    print ("TREE:", tree)
    np = rendLyrNode.viewLocation
    iteration = 1
    renderPasses = {
        "DiffCol": context.scene.view_layers[0].use_pass_diffuse_color,
        "DiffDir": context.scene.view_layers[0].use_pass_diffuse_direct,
        "GlossCol": context.scene.view_layers[0].use_pass_glossy_color,
        "GlossDir": context.scene.view_layers[0].use_pass_glossy_direct,
        "Shadow": context.scene.view_layers[0].use_pass_shadow,
        "AO": context.scene.view_layers[0].use_pass_ambient_occlusion,
        "Mist": context.scene.view_layers[0].use_pass_mist,
        "Emit": context.scene.view_layers[0].use_pass_emit,
        "Normal": context.scene.view_layers[0].use_pass_normal,
        "Depth": context.scene.view_layers[0].use_pass_z
    }
    #if context.scene.view_layers[0].use_pass_diffuse_color:
    #    n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
    #    tree.links.new(rendLyrNode.outputs['DiffCol'], n.inputs[0])
    for each in renderPasses:
        if renderPasses[each]:
            n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
            tree.links.new(rendLyrNode.outputs[each], n.inputs[0])
            n.base_path =  rendDir.as_posix() + '/'+verInfo+'/'+each
            npx = np.x + 800
            npy = np.y - (iteration * 100)
            n.location = ((npx,npy))
            iteration = iteration + 1
    # create links
    # C.scene.node_tree.links.new('','')
    # fix zdepth
    
    # make sure compositing is ticked 

def useCompositing_toggle():
    C.scene.render.use_compositing = not C.scene.render.use_compositing
 
def getRenderInfo():
    fo = C.scene.render.filepath
    #bpy.path.abspath, to replace os.path.abspath
    #bpy.path.relpath, to replace os.path.relpath

     
def setRP_FileOuts(type='png'):
    pass
def updateRP_FileOuts(type='png'):
    for node in C.scene.node_tree.nodes:
        if node.type == 'OUTPUT_FILE':
            no = node.base_path



# OPERATORS HERE


class setupPrismOutput_OT_Operator (bpy.types.Operator):
    '''setup local png render'''
    bl_idname = "ffrend.setup_prism_output"
    bl_label = "ffrend_setupPrismOutput"
    bl_options =  {"REGISTER","UNDO"}
    '''
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if ((context.object) and context.object.type =="ARMATURE" and ('rig_id' in context.object.data)):
                return (1)
        else:
            return(0)
    '''
    def execute(self, context):
        renderPngPasses(context)
        self.report({'INFO'}, "Done.")
        return{"FINISHED"}
class FfPollRend():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    @classmethod
    def poll(cls, context):
        return(context.scene.ff_rend == True)
class FF_PT_Rend(FfPollRend, bpy.types.Panel):
    bl_idname = "FF_PT_Rend"
    bl_label = "Rendering"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        active_obj = context.active_object
        layout = self.layout
        # new stuff
        box = layout.box()
        col = box.column(align = True)
        col.label(text='PRISM ASSIST')
        row = col.row(align=True)
        row.operator("ffrend.setup_prism_output", text="Setup Masks AOV")
        row = col.row(align=True)
        row.operator("ffrend.setup_prism_output", text="PNG Render")
        row = col.row(align=True)
        row.operator("ffrend.setup_prism_output", text="EXR RENDER")
        
        row = col.row(align=True)
        row.operator("ffrend.setup_prism_output", text="Setup Playblast mp4")
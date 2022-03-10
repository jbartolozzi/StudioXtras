import c4d
import json
import os

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_RESP2 = 2012
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990
ARNOLD_C4D_SHADER_GV = 1034190

# Cinema Codes
CINEMA_SHADER_NETWORK = 5703

# from api/util/NodeIds.h
C4DAIN_IMAGE = 262700200

# from res/description/gvarnoldshader.h
C4DAI_GVSHADER_TYPE = 200

# from res/description/gvc4dshader.h
C4DAI_GVC4DSHADER_TYPE = 200

# from res/description/ainode_image.h
C4DAIP_IMAGE_FILENAME = 1737748425

ARNOLD_PROCEDURAL_ALEMBIC_FILE = 313392193
ARNOLD_PROCEDURAL_USD_FILE = 617912960
ARNOLD_PROCEDURAL_ASS_FILE = c4d.C4DAI_PROCEDURAL_PATH


class BaseAsset:
    '''
    Base class for the object/parameter pairs
    '''

    def __init__(self, c4d_object):
        self.c4d_object = c4d_object

    def getFilePath(self):
        return None

    def setFilePath(self, new_path):
        pass

    def getName(self):
        try:
            return self.c4d_object.GetName()
        except:
            return "Unnamed"

    def __bool__(self):
        return self.c4d_object is not None


class ArnoldTexture(BaseAsset):
    def getFilePath(self):
        if self.c4d_object is None:
            return None

        data = self.c4d_object.GetOpContainerInstance()

        if self.c4d_object.GetOperatorID() == ARNOLD_SHADER_GV:
            nodeId = data.GetInt32(C4DAI_GVSHADER_TYPE)
            if nodeId == C4DAIN_IMAGE:
                return data.GetFilename(C4DAIP_IMAGE_FILENAME)

        if self.c4d_object.GetOperatorID() == ARNOLD_C4D_SHADER_GV:
            nodeId = data.GetInt32(C4DAI_GVC4DSHADER_TYPE)
            if nodeId == c4d.Xbitmap:
                # the C4D shader is attached to the GV node
                c4d_shader = self.c4d_object.GetFirstShader()
                if c4d_shader is not None:
                    return c4d_shader.GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)

        return None

    def setFilePath(self, new_path):
        MATERIAL_COMMAND_IMAGE = 1737748425
        self.c4d_object[MATERIAL_COMMAND_IMAGE] = new_path
        c4d.EventAdd()

    def __bool__(self):
        return bool(self.c4d_object is not None and self.getFilePath() is not None)


class CinemaTexture(BaseAsset):
    def getFilePath(self):
        return self.c4d_object[c4d.BITMAPSHADER_FILENAME]

    def setFilePath(self, new_path):
        self.c4d_object[c4d.BITMAPSHADER_FILENAME] = new_path
        c4d.EventAdd()

    def __bool__(self):
        return bool(self.c4d_object is not None and self.c4d_object[c4d.BITMAPSHADER_FILENAME] is not None)


class ArnoldProcedural(BaseAsset):
    def __init__(self, c4d_object, parm_id):
        self.c4d_object = c4d_object
        self.parm_id = parm_id

    def getFilePath(self):
        return self.c4d_object[self.parm_id]

    def setFilePath(self, new_path):
        self.c4d_object[self.parm_id] = new_path
        c4d.EventAdd()

    def __bool__(self):
        return bool(self.c4d_object is not None and self.c4d_object[self.parm_id] is not None and self.c4d_object[self.parm_id] != "")


class CinemaProcedural(BaseAsset):
    def __init__(self, c4d_object):
        self.c4d_object = c4d_object

    def getFilePath(self):
        return self.c4d_object[c4d.ALEMBIC_PATH]

    def setFilePath(self, new_path):
        self.c4d_object[c4d.ALEMBIC_PATH] = new_path
        c4d.EventAdd()

    def __bool__(self):
        return bool(self.c4d_object is not None and self.c4d_object[c4d.ALEMBIC_PATH] is not None and self.c4d_object[c4d.ALEMBIC_PATH] != "")


class PathMapper:
    def __init__(self):
        pathmap_file_path = self.getPathMapFile()
        self.is_valid = False
        if not pathmap_file_path:
            c4d.gui.MessageDialog("Need to set C4D_PATHMAP environment variable.")
            return

        if not os.path.exists(pathmap_file_path):
            c4d.gui.MessageDialog("Cannot find pathmap file: %s." % pathmap_file_path)
            return

        if pathmap_file_path is not None:
            self.correction_dict = {}
            with open(pathmap_file_path, 'r') as infile:
                self.correction_dict = json.load(infile)
                self.is_valid = True

        print("Loaded pathmap file: " + pathmap_file_path)

    def getPathMapFile(self):
        default = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pathmap.json")
        if "C4D_PATHMAP" in os.environ:
            return os.environ["C4D_PATHMAP"]
        elif os.path.exists(default):
            return default
        else:
            return None

    def updatePath(self, texture_path):
        def toUnix(inputpath):
            return inputpath.replace("\\", "/")

        original = texture_path
        for correction in self.correction_dict.keys():
            if toUnix(correction) in toUnix(original):
                corrected_string = toUnix(original).replace(
                    toUnix(correction), toUnix(self.correction_dict[correction]))
                return corrected_string

        return texture_path

    def updateFilePaths(self, assets_to_check):
        num_missing = 0
        num_updated = 0
        for asset in assets_to_check:
            updated = self.updatePath(asset.getFilePath())
            if not os.path.exists(updated):
                num_missing += 1
                print("CheckPaths Updated Path \"%s\" doesnt exist for node \"%s\"." %
                      (updated, asset.getName()))
            elif updated != asset.getFilePath():
                asset.setFilePath(updated)
                print("CheckPaths Updated: %s" % updated)
                num_updated += 1
        return (num_updated, num_missing)


def getAllCinemaTextures(doc):
    output = []
    for mat in list(mat for mat in doc.GetMaterials() if mat.GetType() == CINEMA_SHADER_NETWORK):
        for mid in [c4d.MATERIAL_COLOR_SHADER, c4d.MATERIAL_ALPHA_SHADER, c4d.MATERIAL_DIFFUSION_SHADER, c4d.MATERIAL_LUMINANCE_SHADER, c4d.MATERIAL_NORMAL_SHADER, c4d.MATERIAL_TRANSPARENCY_SHADER, c4d.MATERIAL_ENVIRONMENT_SHADER, c4d.MATERIAL_BUMP_SHADER, ]:
            new_object = CinemaTexture(mat[mid])
            if new_object:
                output.append(new_object)

        if mat[c4d.MATERIAL_USE_REFLECTION]:
            for layernum in range(mat.GetReflectionLayerCount()):
                layer = mat.GetReflectionLayerIndex(layernum)
                new_object = CinemaTexture(
                    mat[layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE])
                if new_object:
                    output.append(new_object)

    return output


def getAllArnoldTextures(doc):
    def queryMaterialNetwork(material):
        msg = c4d.BaseContainer()
        msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
        material.Message(c4d.MSG_BASECONTAINER, msg)
        return msg

    output = []
    for mat in doc.GetMaterials():
        if mat.GetType() == ARNOLD_SHADER_NETWORK:
            network = queryMaterialNetwork(mat)
            numShaders = network.GetInt32(C4DTOA_MSG_RESP1)
            for i in range(0, numShaders):
                new_object = ArnoldTexture(network.GetLink(10000 + i))
                if new_object:
                    output.append(new_object)
    return output


def getAllArnoldProcedurals(doc, all_objects):
    output = []
    arnold_procedurals = list(
        obj for obj in all_objects if obj.GetTypeName() == "Arnold Procedural")
    for procedural in arnold_procedurals:
        for parm_id in [ARNOLD_PROCEDURAL_ASS_FILE, ARNOLD_PROCEDURAL_USD_FILE, ARNOLD_PROCEDURAL_ALEMBIC_FILE]:
            new_object = ArnoldProcedural(procedural, parm_id)
            if new_object:
                output.append(new_object)
    return output


def getAllCinemaProcedurals(doc, all_objects):
    output = []
    procedurals = list(obj for obj in all_objects if obj.GetTypeName() == "Alembic Generator")
    for procedural in procedurals:
        new_object = CinemaProcedural(procedural)
        if new_object:
            output.append(new_object)
    return output


def getAllObjects(doc):
    def recurse_hierarchy(op, output):
        while op:
            output.append(op)
            recurse_hierarchy(op.GetDown(), output)
            op = op.GetNext()
    all_nodes = []
    recurse_hierarchy(doc.GetFirstObject(), all_nodes)
    return all_nodes

def main(doc):

    all_objects = getAllObjects(doc)
    all_assets = getAllCinemaTextures(doc)
    all_assets.extend(getAllArnoldTextures(doc))
    all_assets.extend(getAllCinemaProcedurals(doc, all_objects))
    all_assets.extend(getAllArnoldProcedurals(doc, all_objects))

    num_missing = 0
    num_updated = 0

    # Setup pathmapper object
    pathmapper = PathMapper()
    if not pathmapper.is_valid:
        return

    if len(all_assets):
        (num_img_updated, num_img_missing) = pathmapper.updateFilePaths(all_assets)
        num_updated += num_img_updated
        num_missing += num_img_missing

    popup_text = "Checked %s file paths.\nUpdated %s file paths.\nMissing %s file paths.\n\nCheck console for more information." % (
        len(all_assets), num_updated, num_missing)

    c4d.gui.MessageDialog(popup_text)


if __name__ == '__main__':
    doc = c4d.GetActiveDocument()
    main(doc)

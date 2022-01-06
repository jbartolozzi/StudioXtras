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


class ArnoldTexture:
    @staticmethod
    def queryMaterialNetwork(material):
        msg = c4d.BaseContainer()
        msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
        material.Message(c4d.MSG_BASECONTAINER, msg)
        return msg

    @staticmethod
    def getPaths(doc):
        '''
        Return tuple of (object, file_path)
        '''
        output = []
        for mat in doc.GetMaterials():
            if mat.GetType() == ARNOLD_SHADER_NETWORK:
                network = ArnoldTexture.queryMaterialNetwork(mat)
                numShaders = network.GetInt32(C4DTOA_MSG_RESP1)
                for i in range(0, numShaders):
                    shader = network.GetLink(10000 + i)
                    texture_path = ArnoldTexture.getTexturePath(shader)
                    if texture_path:
                        output.append((shader, texture_path))
        return output

    @staticmethod
    def getTexturePath(shader):
        if shader is None:
            return None

        data = shader.GetOpContainerInstance()

        if shader.GetOperatorID() == ARNOLD_SHADER_GV:
            nodeId = data.GetInt32(C4DAI_GVSHADER_TYPE)
            if nodeId == C4DAIN_IMAGE:
                return data.GetFilename(C4DAIP_IMAGE_FILENAME)

        if shader.GetOperatorID() == ARNOLD_C4D_SHADER_GV:
            nodeId = data.GetInt32(C4DAI_GVC4DSHADER_TYPE)
            if nodeId == c4d.Xbitmap:
                # the C4D shader is attached to the GV node
                c4d_shader = shader.GetFirstShader()
                if c4d_shader is not None:
                    return c4d_shader.GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)

        return None

    @staticmethod
    def setShaderUpdatedPath(shader, texture_path):
        MATERIAL_COMMAND_IMAGE = 1737748425
        shader[MATERIAL_COMMAND_IMAGE] = texture_path
        c4d.EventAdd()


class ArnoldProcedural:
    @staticmethod
    def getPaths(doc):
        output = []
        arnold_procedurals = list(obj for obj in doc.GetObjects() if obj.GetType() == 1032509)
        for arnold_procedural in arnold_procedurals:
            for parm_id in [ARNOLD_PROCEDURAL_ASS_FILE, ARNOLD_PROCEDURAL_USD_FILE, ARNOLD_PROCEDURAL_ALEMBIC_FILE]:
                if arnold_procedural[parm_id]:
                    output.append((arnold_procedural, parm_id))
        return output

    @staticmethod
    def setPath(arnold_procedural, parm_id, texture_path):
        arnold_procedural[parm_id] = texture_path
        c4d.EventAdd()


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


def updateImageTexturePaths(image_textures_to_check, pathmapper):
    num_missing = 0
    num_updated = 0
    for shader, texture_path in image_textures_to_check:
        updated = pathmapper.updatePath(texture_path)
        if not os.path.exists(updated):
            num_missing += 1
            print("CheckPaths Cant find: %s" % updated)
        elif updated != texture_path:
            ArnoldTexture.setShaderUpdatedPath(shader, updated)
            print("CheckPaths Updated: %s" % updated)
            num_updated += 1
    return (num_updated, num_missing)


def updateProceduralPaths(procedurals_to_check, pathmapper):
    num_missing = 0
    num_updated = 0
    for (arnold_procedural, parm_id) in procedurals_to_check:
        file_path = arnold_procedural[parm_id]
        updated = pathmapper.updatePath(file_path)
        if not os.path.exists(updated):
            num_missing += 1
            print("CheckPaths Cant find: %s" % updated)
        elif updated != file_path:
            ArnoldProcedural.setPath(arnold_procedural, parm_id, updated)
            print("CheckPaths Updated: %s" % updated)
            num_updated += 1
    return (num_updated, num_missing)

def main(doc):

    image_textures_to_check = ArnoldTexture.getPaths(doc)
    procedurals_to_check = ArnoldProcedural.getPaths(doc)

    num_missing = 0
    num_updated = 0

    if len(image_textures_to_check):
        # Setup pathmapper object
        pathmapper = PathMapper()
        if not pathmapper.is_valid:
            return

        # Update arnold texture image paths
        (num_img_updated, num_img_missing) = updateImageTexturePaths(
            image_textures_to_check, pathmapper)
        num_updated += num_img_updated
        num_missing += num_img_missing

        # Update arnold procedural paths
        (num_img_updated, num_img_missing) = updateProceduralPaths(procedurals_to_check, pathmapper)
        num_updated += num_img_updated
        num_missing += num_img_missing

    popup_text = "Checked %s file paths.\nUpdated %s file paths.\nMissing %s file paths.\n\nCheck console for more information." % (
        len(image_textures_to_check) + len(procedurals_to_check), num_updated, num_missing)

    c4d.gui.MessageDialog(popup_text)

if __name__ == '__main__':
    main(doc)

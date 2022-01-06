import hou
SETTINGS_LOW = \
    {"render": {"ar_AA_samples": 1,
                "ar_enable_adaptive_sampling": True,
                "ar_AA_samples_max": 2,
                "ar_AA_adaptive_threshold": 0.05,
                "ar_GI_diffuse_samples": 1,
                "ar_GI_specular_samples": 1,
                "ar_GI_transmission_samples": 1,
                "ar_GI_sss_samples": 1,
                "ar_GI_volume_samples": 1,
                },
     "denoiser": {
        "variance": 0.8,
    }}

SETTINGS_MED = \
    {"render": {"ar_AA_samples": 2,
                "ar_enable_adaptive_sampling": True,
                "ar_AA_samples_max": 4,
                "ar_AA_adaptive_threshold": 0.025,
                "ar_GI_diffuse_samples": 2,
                "ar_GI_specular_samples": 2,
                "ar_GI_transmission_samples": 2,
                "ar_GI_sss_samples": 2,
                "ar_GI_volume_samples": 2,
                },
     "denoiser": {
        "variance": 0.4,
    }}
SETTINGS_HIGH = \
    {"render": {"ar_AA_samples": 3,
                "ar_enable_adaptive_sampling": True,
                "ar_AA_samples_max": 8,
                "ar_AA_adaptive_threshold": 0.01,
                "ar_GI_diffuse_samples": 2,
                "ar_GI_specular_samples": 2,
                "ar_GI_transmission_samples": 2,
                "ar_GI_sss_samples": 2,
                "ar_GI_volume_samples": 2,
                },
     "denoiser": {
        "variance": 0.25,
    }}


def updateArnoldPreset():
    arnold_rop = hou.node(hou.pwd().path() + "/arnold1")
    if arnold_rop is None:
        raise hou.NodeWarning("Cannot locate arnold ROP")

    mode = hou.pwd().parm("preset").eval()
    if mode == 0:
        for parm_name, val in SETTINGS_LOW["render"].items():
            arnold_rop.parm(parm_name).set(val)
    elif mode == 1:
        for parm_name, val in SETTINGS_MED["render"].items():
            arnold_rop.parm(parm_name).set(val)
    elif mode == 2:
        for parm_name, val in SETTINGS_HIGH["render"].items():
            arnold_rop.parm(parm_name).set(val)

    if hou.pwd().parm("enable_denoiser"):
        denoiser_rop = hou.node(hou.pwd().path() + "/arnold_denoiser1")
        if denoiser_rop is None:
            raise hou.NodeWarning("Cannot locate arnold ROP")

        mode = hou.pwd().parm("preset").eval()
        if mode == 0:
            for parm_name, val in SETTINGS_LOW["denoiser"].items():
                denoiser_rop.parm(parm_name).set(val)
        elif mode == 1:
            for parm_name, val in SETTINGS_MED["denoiser"].items():
                denoiser_rop.parm(parm_name).set(val)
        elif mode == 2:
            for parm_name, val in SETTINGS_HIGH["denoiser"].items():
                denoiser_rop.parm(parm_name).set(val)

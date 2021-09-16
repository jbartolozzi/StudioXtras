import hou
low = {"ar_AA_samples": 1,
       "ar_enable_adaptive_sampling": True,
       "ar_AA_samples_max": 2,
       "ar_AA_adaptive_threshold": 0.05,
       "ar_GI_diffuse_samples": 1,
       "ar_GI_specular_samples": 1,
       "ar_GI_transmission_samples": 1,
       "ar_GI_sss_samples": 1,
       "ar_GI_volume_samples": 1,
       }

med = {"ar_AA_samples": 2,
       "ar_enable_adaptive_sampling": True,
       "ar_AA_samples_max": 4,
       "ar_AA_adaptive_threshold": 0.025,
       "ar_GI_diffuse_samples": 2,
       "ar_GI_specular_samples": 2,
       "ar_GI_transmission_samples": 2,
       "ar_GI_sss_samples": 2,
       "ar_GI_volume_samples": 2,
       }
high = {"ar_AA_samples": 3,
        "ar_enable_adaptive_sampling": True,
        "ar_AA_samples_max": 8,
        "ar_AA_adaptive_threshold": 0.01,
        "ar_GI_diffuse_samples": 2,
        "ar_GI_specular_samples": 2,
        "ar_GI_transmission_samples": 2,
        "ar_GI_sss_samples": 2,
        "ar_GI_volume_samples": 2,
        }


def updateArnoldPreset():
    arnold_rop = hou.node(hou.pwd().path() + "/arnold1")
    if arnold_rop is None:
        raise hou.NodeWarning("Cannot locate arnold ROP")

    mode = hou.pwd().parm("preset").eval()
    if mode == 0:
        for parm_name, val in low.items():
            arnold_rop.parm(parm_name).set(val)
    elif mode == 1:
        for parm_name, val in med.items():
            arnold_rop.parm(parm_name).set(val)
    elif mode == 2:
        for parm_name, val in high.items():
            arnold_rop.parm(parm_name).set(val)

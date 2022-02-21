from omegaconf import OmegaConf
from scripts.local_env import DEFAULT_PRESETS
import logging
from omegaconf_helpers import omegaconf_universal_load
import copy
logger = logging.getLogger(__name__)

# def send_udp_sync(self, brightness=255, col=[255,0,0, 0], fx=0, fx_speed=10, fx_intensity=255, transition_delay=1000, palette=0, 
#         nightlightActive=0, nightlightDelayMins=60,
#         secondary_color=[0, 255, 0, 0], tertiary_color=[0, 0, 255, 0],
#         follow_up=False, sync_groups={1}, timebase_shift=0):

# https://github.com/Aircoookie/WLED/blob/bc403440bac6d8f3d074153d2d8a2f5c838efe2e/wled00/json.cpp#L149

def get_preset_by_id(ps_id):
    return default_presets[str(ps_id)]

def _get_udp_kwargs(preset):
    kwargs = {}
    try:
        kwargs["brightness"] = preset["bri"]
    except Exception as e:
        logger.debug(f"No brightness in ps {ps_id}: {e}")
    try:
        kwargs["transition_delay"] = int(preset["transition"] * 100)
    except Exception as e:
        logger.debug(f"No transition in ps {ps_id}: {e}")
    mainseg = preset.get("mainseg", 0)
    try:
        seg = preset.seg
        mainseg = seg[mainseg]
    except Exception as e:
        logger.debug(f"No mainseg in ps {ps_id}: {e}")
        return kwargs
    try:
        kwargs["col"] = list(mainseg.col[0])
    except Exception as e:
        logger.debug(f"No col in ps {ps_id}: {e}")
    try:
        kwargs["secondary_color"] = list(mainseg.col[1])
    except Exception as e:
        logger.debug(f"No secondary_color in ps {ps_id}: {e}")
    try:
        kwargs["tertiary_color"] = list(mainseg.col[2])
    except Exception as e:
        logger.debug(f"No tertiary_color in ps {ps_id}: {e}")
    try:
        kwargs["fx"] = mainseg["fx"]
    except Exception as e:
        logger.debug(f"No fx in ps {ps_id}: {e}")
    try:
        kwargs["fx_speed"] = mainseg["sx"]
    except Exception as e:
        logger.debug(f"No fx_speed in ps {ps_id}: {e}")
    try:
        kwargs["fx_intensity"] = mainseg["ix"]
    except Exception as e:
        logger.debug(f"No fx_intensity in ps {ps_id}: {e}")
    try:
        kwargs["palette"] = mainseg["pal"]
    except Exception as e:
        logger.debug(f"No palette in ps {ps_id}: {e}")
    try:
        grp = mainseg["grp"]
        sync_groups = []
        for i in range(8):
            if grp & 1: sync_groups.append(i+1)
            grp >>= 1
        kwargs["sync_groups"] = sync_groups
    except Exception as e:
        logger.debug(f"No palette in ps {ps_id}: {e}")
    return kwargs    

def get_udp_kwargs(ps_id, eff_intensity=None, eff_speed=None, follow_up=None, transition_delay=None):
    kwargs = copy.copy(__preset_kwargs[ps_id])
    if eff_intensity is not None:
        kwargs["fx_intensity"] = eff_intensity
    if eff_speed is not None:
        kwargs["fx_speed"] = eff_speed
    if follow_up is not None:
        kwargs["follow_up"] = follow_up
    if transition_delay is not None:
        kwargs["transition_delay"] = transition_delay
    return kwargs

default_presets = list(DEFAULT_PRESETS())
default_presets = [omegaconf_universal_load(f) for f in default_presets]
default_presets = OmegaConf.merge(*default_presets)

__preset_kwargs = {}
for ps_id, preset in default_presets.items():
    __preset_kwargs[int(ps_id)] = _get_udp_kwargs(preset)
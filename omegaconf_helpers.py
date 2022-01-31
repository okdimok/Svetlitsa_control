from omegaconf import OmegaConf
from ruamel.yaml import YAML
import dictdiffer as dd
import logging
logger = logging.getLogger(__name__)


def omegaconf_universal_load(conf):
    if isinstance(conf, str):
        if conf.endswith(".yaml"):
            return OmegaConf.load(conf)
        else: return OmegaConf.create(conf)
    elif OmegaConf.is_config(conf):
        return conf
    else:
        return OmegaConf.create(conf)

def create_patch_from_omegaconf(custom_cfg, general_cfg):
    patch = list(dd.swap(dd.diff(custom_cfg, general_cfg, expand=True, dot_notation=False)))
    new_patch = []
    for p in patch:
        if p[0] == "remove":
            continue
        elif p[0] == "add":
            new_patch.append(p)
        elif p[0] == "change":
            new_patch.append(("add", p[1], p[2][1]))
        else:
            raise ValueError()
    new_cfg = OmegaConf.create()
    new_cfg = {}
    for p in new_patch:
        keys = list(p[1])
        v = p[2] 
        if isinstance(p[2], list):
            keys += [p[2][0][0]]
            v = p[2][0][1]

        if len(keys) == 1:
            new_cfg[keys[0]] = v
        elif len(keys) > 1:
            curr = new_cfg
            orig = general_cfg
            prev = None
            for k, kn in zip(keys[:-1], keys[1:]): # key, key_next
                orig = orig[k]
                try:
                    curr = curr[k]
                except KeyError: # it is for dicts
                    if isinstance(kn, int):
                        curr[k] = orig # as far as we create list we need to copy it from the main config
                    elif isinstance(kn, str):
                        curr[k] = dict()
                    curr = curr[k]
                except IndexError: # for lists
                    if isinstance(kn, int):
                        curr.append(list())
                    elif isinstance(kn, str):
                        curr.append(dict())
                    curr = curr[-1]
            try:
                curr[kn] = v
            except IndexError:
                curr.append(v)
        else:
            raise ValueError
            

    new_cfg = OmegaConf.create(new_cfg)

    # dbg("="*20)
    # dbg(patch)
    # dbg("#"*20)
    # dbg(new_patch)
    # dbg("*"*20)
    # dbg(new_cfg)
    # dbg(">"*20  )
    # result = Wled.from_omegaconf(additional_confs=[OmegaConf.to_container(new_cfg)]).cfg
    # dbg(list(dd.diff(result, custom_cfg)))
    return new_cfg

def tidy_yaml(f):
    yaml = YAML()
    with open(f, encoding="utf-8") as fr:
        d = yaml.load(fr)
    yaml.default_flow_style = True
    d.fa.set_block_style()
    for k in d.keys():
        try:
            d[k].fa.set_block_style()
            for kk in d[k].keys():
                try:
                    d[k][kk].fa.set_flow_style()
                except AttributeError:
                    pass
        except AttributeError:
            pass
    with open(f, "w", encoding="utf-8") as fw:
        yaml.dump(d, fw)

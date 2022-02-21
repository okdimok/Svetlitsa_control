from inspect import ismethod

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class NamingEnum:
    @classmethod
    def __init_names__(cls):
        for attr in cls.keys():
            getattr(cls, attr).name = attr
            # print(f"{attr}: {type(getattr(cls, attr))}")

    @classmethod
    def keys(cls):
        return [a for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]
    
    @classmethod
    def items(cls):
        return [(a,v) for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]

    @classmethod
    def values(cls):
        return [v for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]

from IPython.display import display_html, clear_output

def display_dicts(wleds, dicts, fields=["ver"], seg_fields=["fx"]):
    clear_output(wait=True)
    r = "<br><table><tr><th>WLED name</th><th>IP</th>"
    for field in fields:
        r += f"<th>{field}</th>"
    for field in seg_fields:
        r += f"<th>{field}</th>"
    r+="</tr>"
    for wled, state in zip(wleds, dicts):
        r += f"<tr><td>wl.wleds['{wled.name}']</td><td>{wled.ip}</td>"
        for field in fields:
            if field in state.keys():
                value = state[field]
                r += f"<td>{value}</td>"
            else:
                r += f"<td>NO {field}</td>"
        if "seg" not in state.keys():
            for field in seg_fields:
                r += f"<td>NO {field}</td>"
        else:
            seg = state["seg"][0]
            for field in seg_fields:
                if field in seg.keys():
                    value = seg[field]
                    r += f"<td>{value}</td>"
                else:
                    r += f"<td>NO {field}</td>"

        r += "</tr>"
    r += "</table>"
    display_html(r, raw=True)
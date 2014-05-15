import json

def clean(s):
    try:
        s = s.decode('ascii').strip()
        return s if len(s) > 0 and s != "Default" else None
    except:
        return None

def map(k, d, v, cx):
    j = json.loads(v)

    addons = j['addonDetails'].get('XPI', {})
    addon_names = set()

    for addon, desc in addons.iteritems():
        if "name" in desc:
            name = clean(desc["name"])

            if name is not None:
                addon_names.add(name)

    addon_names = list(addon_names)

    if len(addon_names) > 0:
        cx.write(",".join(addon_names), 1)

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(k, v, cx):
    cx.write(sum(v), k)

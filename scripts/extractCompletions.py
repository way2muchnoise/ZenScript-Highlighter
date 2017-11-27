import urllib2

import re


def fetch_page(url):
    try:
        response = urllib2.urlopen(url)
        return response.read()
    except urllib2.HTTPError:
        return None


def param_clean(param):
    if ' ' not in param and '...' in param:
        param = param.replace('...', '... ')
    param_splited = param.split(' ')
    param_name = param_splited[-1]
    param_type = param_splited[-2]
    if param.startswith('@Optional'):
        param_name = 'optional' + param_name[0].capitalize() + param_name[1:]
    while param_type.endswith('[]'):
        param_name += '[]'
        param_type = param_type[:-2]
    if param_type.endswith('...'):
        param_name += '...'
    return param_name


def write_trigger(out, class_name, method_name, params):
    out.write('      { "trigger": "' + method_name + '\\t' + class_name +
              '", "contents": "' + class_name + '.' + method_name + '(' + ', '.join(params) + ');" },\n')

zen_class = re.compile('@ZenClass\((value = )?"(.*?)"\)')
zen_method = re.compile('@ZenMethod\n\s+.*?void (.*?)\s?\((.*?)\)')

out = open('ZenScript.sublime-completions', 'w')
out.write('{\n   "scope": "plain.text.zs, source.zs",\n\n   "completions":\n   [\n')
remaps = {}
errors = []
with open('remaps.txt') as f:
    for line in f.readlines():
        splitted = line.strip().split(':')
        remaps[splitted[0]] = splitted[1]
with open('classes.txt') as f:
    for line in f.readlines():
        url = line.strip()
        if len(url) is 0 or url.startswith('#'):
            continue
        page = fetch_page(url)
        if page is None:
            errors.append(url)
            continue
        class_name = zen_class.search(page).group(2)
        if class_name in remaps:
            class_name = remaps[class_name]
        methods = re.findall(zen_method, page)
        print class_name
        for method in methods:
            method_name = method[0]
            params = method[1].split(', ')
            if params[0] != '':
                params = map(param_clean, params)
            print '\t' + method_name + '(' + ', '.join(params) + ')'
            write_trigger(out, class_name, method_name, params)
out.write('   ]\n}')
print "Errored urls"
for error in errors:
    print error

import urllib2

import re


def fetch_page(url):
    response = urllib2.urlopen(url)
    return response.read()


def param_clean(param):
    param_splited = param.split(' ')
    param_name = param_splited[-1]
    param_type = param_splited[-2]
    if param.startswith('@Optional'):
        param_name = 'optional' + param_name[0].capitalize() + param_name[1:]
    while param_type.endswith('[]'):
        param_name += '[]'
        param_type = param_type[:-2]
    return param_name


def write_trigger(out, class_name, method_name, params):
    out.write('      { "trigger": "' + method_name + '\\t' + class_name +
              '", "contents": "' + class_name + '.' + method_name + '(' + ', '.join(params) + ');" },\n')

zen_class = re.compile('@ZenClass\("(.*?)"\)')
zen_method = re.compile('@ZenMethod\n\s+.*?void (.*?)\((.*?)\)')

out = open('ZenScript.sublime-completions', 'w')
out.write('{\n   "scope": "plain.text.zs, source.zs",\n\n   "completions":\n   [\n')
remaps = {}
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
        class_name = zen_class.search(page).group(1)
        if class_name in remaps:
            class_name = remaps[class_name]
        methods = re.findall(zen_method, page)
        print class_name
        for method in methods:
            method_name = method[0]
            params = method[1].split(', ')
            params = map(param_clean, params)
            print '\t' + method_name + '(' + ', '.join(params) + ')'
            write_trigger(out, class_name, method_name, params)
out.write('   ]\n}')

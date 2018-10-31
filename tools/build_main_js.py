#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/tools/build_main_js.py
# description: 自动汇总所有的 js 代码，构建 main.js


import os
import re
import jinja2


Root_Dir = os.path.join(os.path.dirname(__file__), "../app/")
Template_Dir = os.path.join(Root_Dir, "templates/")
Admin_Dir = os.path.join(Template_Dir, "admin/")
Order_Dir = os.path.join(Template_Dir, "order/")
Static_Dir = os.path.join(Root_Dir, "static/")
JS_Dir = os.path.join(Static_Dir, "js/")


def get_filelist(folder):
    return [os.path.join(folder, filename) for filename in os.listdir(folder)]

def read_file(file):
    with open(file, "r", encoding="utf-8-sig") as fp:
        content = fp.read()
    return content

def write_file(file, content):
    with open(file, "w", encoding="utf-8") as fp:
        fp.write(content)


regex_script_block = re.compile(r"""{%\s*block\s+script\s*%}\s*<script.*?>\s*("use strict";)*\s*(?P<js>.*?)</script>.*?{%\s*endblock\s+(script)*\s*%}""", re.S)
regex_script_tag = re.compile(r"""<script type="text/javascript">\s*("use strict";)*\s*(?P<js>.*?)</script>""", re.S)

function_wrap = jinja2.Template(r"""

/* {{ filename }} */
(function(){
  "use strict";

{{ js }}
})();

""")


main_js = ""


site_base_html = "site-base.html"
res = regex_script_tag.search(read_file(os.path.join(Template_Dir, site_base_html)))
main_js += function_wrap.render(filename=site_base_html, js=res.groupdict()["js"])

for file in get_filelist(Admin_Dir) + get_filelist(Order_Dir):
    filename = os.path.basename(file)
    ext = os.path.splitext(filename)[1]
    if ext not in (".html",".htm"):
        continue
    content = read_file(file)
    res = regex_script_block.search(content)
    if not res:
        continue
    main_js += function_wrap.render(filename=filename, js=res.groupdict()["js"])


write_file(os.path.join(JS_Dir, "main.js"), main_js)
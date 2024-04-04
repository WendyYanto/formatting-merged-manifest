# Reference:
# https://proandroiddev.com/android-ci-reveal-manifest-changes-in-a-pull-request-a5cdd0600afa

import subprocess
import xml.etree.ElementTree as Tree

TARGET_MANIFEST_PATH = "source/AndroidManifest.xml"
SORTED_MANIFEST_PATH = "target/MergedAndroidManifest.xml"

print(f"sort manifest {TARGET_MANIFEST_PATH} to {SORTED_MANIFEST_PATH}")

def get_sorting_weight(node):
    rootWeights = ["uses-sdk", "uses-feature", "uses-permission", "permission", "application", "queries"]

    for index, item in enumerate(rootWeights):
        if node.tag.startswith(item):
            return index

    return len(rootWeights)


def get_attribute(node):
    name_attribute = "{http://schemas.android.com/apk/res/android}name"
    if name_attribute in node.attrib:
        return node.attrib[name_attribute]
    else:
        return ""

def sort_tree(node):
    node[:] = sorted(node, key=lambda child: (
        get_sorting_weight(child),
        child.tag,
        get_attribute(child)))
    if node.text is not None:
        node.text = node.text.strip()
    for item in node:
        # will sort by alphabets if outside of rootWeights scopes
        sort_tree(item)

def register_all_namespaces(filename):
    namespaces = dict([node for _, node in Tree.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        Tree.register_namespace(ns, namespaces[ns])

register_all_namespaces(TARGET_MANIFEST_PATH)

# sort xml
tree = Tree.ElementTree(file=TARGET_MANIFEST_PATH)
root = tree.getroot()
sort_tree(root)

output = Tree \
    .tostring(root, encoding="utf-8", method="xml", short_empty_elements=True) \
    .decode()

# write result to file
manifestFile = open(SORTED_MANIFEST_PATH, "w")
manifestFile.write(output)
manifestFile.truncate()

# pretty format xml to clean up redundant lines
subprocess.run(['tidy', '-config', "tidy.ini", '-o', SORTED_MANIFEST_PATH, SORTED_MANIFEST_PATH])
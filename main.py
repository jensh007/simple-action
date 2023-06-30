#! /usr/bin/env python3
import os
import pprint
import sys
# from ruamel.yaml import YAML
import yaml

import other

def main():
    global_dict:dict[str, any] = {}
    comp_root = os.getenv("ocm_comp_root")
    name = os.getenv("ocm_name")
    version = os.getenv("ocm_version")
    provider = os.getenv("ocm_provider")
    image_yaml = os.getenv("ocm_images")
    helm_charts_yaml =  os.getenv('ocm_helm_charts')
    references_yaml =  os.getenv('ocm_references')
    files_yaml =  os.getenv('ocm_files')
    labels_yaml =  os.getenv('ocm_labels')

    print(f'my input variable "ocm_images": {image_yaml}')
    other.other()
    print(f' Python version: {sys.version_info}')

    global_dict['name'] = name
    global_dict['version'] = version
    global_dict['provider'] = provider

    if image_yaml:
        d = yaml.safe_load(image_yaml)
        global_dict['images'] = d
    if helm_charts_yaml:
        d = yaml.safe_load(helm_charts_yaml)
        global_dict['helm_charts'] = d
    if references_yaml:
        d = yaml.safe_load(references_yaml)
        global_dict['references'] = d
    if files_yaml:
        d = yaml.safe_load(files_yaml)
        global_dict['files'] = d
    if labels_yaml:
        d = yaml.safe_load(labels_yaml)
        global_dict['labels'] = d

    print("Global Dictionary:")
    pprint.pprint(global_dict)


if __name__ == '__main__':
    main()

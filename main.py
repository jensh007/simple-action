#! /usr/bin/env python3
import os
import sys
from ruamel.yaml import YAML

import other

def main():
    image_yaml = os.getenv("ocm_images")
    print(f'my input variable "ocm_images": {image_yaml}')
    other.other()
    print(f' Python version: {sys.version_info}')

    yaml=YAML(typ='safe')
    d = yaml.load(image_yaml)
    print(f'loaded yaml input: {d}')

if __name__ == '__main__':
    main()

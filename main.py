#! /usr/bin/env python3
import os
import sys

import other

def main():
    print(f'{os.environ=}')
    print(f'my input variable "ocm_images": {os.getenv("ocm_images")}')
    other.other()
    print(f' Python version: {sys.version_info}')

if __name__ == '__main__':
    main()

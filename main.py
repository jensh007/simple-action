#! /usr/bin/env python3
import os
import other

def main():
    print(f'{os.environ=}')
    print(f'my input variable "ocm_images": {os.getenv("ocm_images")}')
    other.other()


if __name__ == '__main__':
    main()

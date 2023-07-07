import hashlib
import sys

def file_digest(temp_file) -> str:
    py_version = sys.version_info
    if py_version.major >= 3 and py_version.minor >= 11:
        with open(temp_file, 'rb') as f:
            digest = hashlib.file_digest(f, 'sha256')
        hex_digest = digest.hexdigest()
    else:
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()
        with open(temp_file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha256.update(data)
        hex_digest = sha256.hexdigest()

    return hex_digest

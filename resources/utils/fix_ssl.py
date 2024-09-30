# taken from https://stackoverflow.com/a/66094151

# install_certifi.py
#
# sample script to install or update a set of default Root Certificates
# for the ssl module.  Uses the certificates provided by the certifi package:
#       https://pypi.python.org/pypi/certifi


import os
import ssl
import stat
import certifi
from pathlib import Path

STAT_0o775 = (
    stat.S_IRUSR
    | stat.S_IWUSR
    | stat.S_IXUSR
    | stat.S_IRGRP
    | stat.S_IWGRP
    | stat.S_IXGRP
    | stat.S_IROTH
    | stat.S_IXOTH
)


def fixSSL():
    ssl_default_path = Path(ssl.get_default_verify_paths().openssl_cafile)

    openssl_cafile = ssl_default_path.name
    openssl_dir = ssl_default_path.parent

    # change working directory to the default SSL directory
    previous_cwd = Path.cwd()

    os.chdir(openssl_dir)

    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass

    os.symlink(relpath_to_certifi_cafile, openssl_cafile)

    os.chmod(openssl_cafile, STAT_0o775)

    os.chdir(previous_cwd)

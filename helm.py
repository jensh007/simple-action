from pathlib import Path
import re
import shutil
import tempfile
import tarfile
import json
import os

import yaml

import oci.model as om
import util


def package_helm_as_oci(chart_path: str):
    CHART_NAME = 'Chart.yaml'
    CHART_PATTERN = r'^[^\/]+\/Chart.yaml$' # any dir name followed by /Chart.yaml
    MANIFEST_MIME_TYPE_OCI = 'application/vnd.oci.image.manifest.v1+json'
    MIME_TYPE_HELM_CONFIG = "application/vnd.cncf.helm.config.v1+json"
    MIME_TYPE_HELM_TGZ = "application/vnd.cncf.helm.chart.content.v1.tar+gzip"

    with tempfile.TemporaryDirectory(prefix='helm_in_', suffix='_tar') as tmp:
        print('created temporary directory for helm input chart', tmp)
        with tarfile.open(chart_path) as tar:
            names = tar.getnames()
            for name in names:
                print(name)
                if re.match(CHART_PATTERN, name):
                    print(f'found chart {name}')
                    chart_file = name
                    break;
            if not chart_path:
                raise ValueError(f'Could not find a Chart.yaml file in archive {chart_path}')
            tar.extract(name, path=tmp)

        # print(os.listdir(tmp))
        chart_file = Path(tmp) / name
        with open(chart_file) as f:
            chart_dict = yaml.safe_load(f)

    with tempfile.TemporaryDirectory(prefix='helm', suffix='_tar') as tmp:
        print('created temporary directory for helm output', tmp)
        tmp = Path(tmp)
        cfg_path = tmp / 'chart.json'
        with open(cfg_path, 'w') as f:
            json.dump(chart_dict, f)
        sha_cfg_file = util.file_digest(cfg_path)
        sha_cfg_path = tmp / f'sha256.{sha_cfg_file}'
        cfg_path = cfg_path.rename(sha_cfg_path)
        print(f'renamed {cfg_path.name=}')

        tgz_path = tmp / 'chart.tgz'
        shutil.copyfile(chart_path, tgz_path)
        sha_tgz_file = util.file_digest(tgz_path)
        tgz_path = tgz_path.rename(tmp / f'sha256.{sha_tgz_file}')
        print(f'renamed {tgz_path.name=}')

        manifest = om.OciImageManifest(
            config = om.OciBlobRef(
                digest=f'sha256:{sha_cfg_file}',
                mediaType=MIME_TYPE_HELM_CONFIG,
                size=cfg_path.stat().st_size,
            ),
            layers = [om.OciBlobRef(
                digest=f'sha256:{sha_tgz_file}',
                mediaType=MIME_TYPE_HELM_TGZ,
                size=tgz_path.stat().st_size,
            )],
            mediaType = MANIFEST_MIME_TYPE_OCI,
        )

        manifest_path = tmp / 'index.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest.as_dict(), f)
        sha_manifest_file = util.file_digest(manifest_path)
        manifest_path = manifest_path.rename(tmp / f'sha256.{sha_manifest_file}')
        print(f'renamed {manifest_path.name=}')
        print(os.listdir(tmp))

        # TODO: create a tar file from this dir


if __name__ == '__main__':
    package_helm_as_oci('charts/mariadb.tgz')
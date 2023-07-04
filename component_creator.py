from dataclasses import dataclass
import dataclasses
import datetime
import os
from pathlib import Path
import gci.componentmodel as cm
import yaml
import shutil
import hashlib

import ocm_input_model

def get_cd_from_file(cd_file: str) -> cm.ComponentDescriptor:
    with open(cd_file) as f:
        cd_dict = yaml.safe_load(f)
    cd = cm.ComponentDescriptor.from_dict(cd_dict, cm.ValidationMode.NONE)
    return cd


def create_cd() -> cm.ComponentDescriptor:
    component = cm.Component(
        name = 'acme.org/simpleserver',
        provider = 'github.com/acme',
        repositoryContexts=[
            cm.OciRepositoryContext(
                baseUrl='ghcr.io',
                subPath='jensh007/ocm',
                type=cm.AccessType.OCI_REGISTRY
            )
        ],
        version='1.0.0',
        sources=None,
        componentReferences=None,
        resources=None,
    )
    cd = cm.ComponentDescriptor(
        meta=cm.Metadata(schemaVersion=cm.SchemaVersion.V2),
        component=component,
        signatures=None,
    )
    return cd


def write_cd(fname: str, cd: cm.ComponentDescriptor):
    dict = dataclasses.asdict(cd)
    with open(fname, 'w') as f:
        yaml.dump(data=dict, stream=f, Dumper=cm.EnumValueYamlDumper)


def digest_file(fname: str) -> str:
    with open(hashlib.__file__, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")

    return digest.hexdigest()


def normalize_name(name: str) -> str:
    return name.lower().replace('.', '_')


def digest_and_store_file(fname: str, path: Path | str) -> tuple[str, int]:
    sha = digest_file(fname)
    blobs_dir = Path(path) / 'blobs'
    blobs_dir.mkdir(exist_ok=True)
    dest_name = path / f'blobs/sha256.{sha}'
    shutil.copyfile(fname, dest_name)
    len = dest_name.stat().st_size
    return sha, len


def process_resources(ocm_input: ocm_input_model.OcmInput, path: Path | str) -> list[cm.Resource]:
    resources = []
    if ocm_input.images:
        for image in ocm_input.images:
            name, ver = image.split(':')
            _, _, name = name.rpartition('/')
            res = cm.Resource(
                name=name,
                version=ver,
                access=cm.OciAccess(imageReference=image),
                type=cm.ArtefactType.OCI_IMAGE,
            )
            resources.append(res)
    if ocm_input.helm_charts:
        for chart_name in ocm_input.helm_charts:
            if chart_name.startswith('http://') or chart_name.startswith('https://'):
                print('http chart reference not yet implemented, will be ignored.')
                _, name, ver = chart_name.split(':')
                _, _, res_name = name.rpartition('/')
            else:
                name, ver = chart_name.split(':')
                _, _, res_name = name.rpartition('/')
                res_name = normalize_name(res_name)
                sha, len  = digest_and_store_file(name, path)
                # print(f'sha of {chart_name} is: {sha}')
                access = cm.OciBlobAccess(
                    type=cm.AccessType.LOCAL_BLOB,
                    imageReference=chart_name,
                    mediaType='application/vnd.oci.image.manifest.v1+tar+gzip',
                    digest=sha,
                    size=len,
                )
            res = cm.Resource(
                name=res_name,
                version=ver,
                access=access,
                type=cm.ArtefactType.HELM_CHART,
            )
            resources.append(res)

    if ocm_input.files:
        for file in ocm_input.files:
            sha, len  = digest_and_store_file(file.name, path)
            name = normalize_name(file.name)
            # print(f'sha of {chart_name} is: {sha}')
            access = cm.OciBlobAccess(
                type=cm.AccessType.LOCAL_BLOB,
                imageReference=name,
                mediaType=file.content_type,
                digest=sha,
                size=len,
            )
            res = cm.Resource(
                name=name,
                version=ver,
                access=access,
                type=cm.ArtefactType.BLOB,
            )
            resources.append(res)

    return resources


def process_labels(ocm_input: ocm_input_model.OcmInput) -> list[cm.Label] :
    labels = []
    # position currently ignored, only top-level
    for label in ocm_input.labels:
        labels.append(cm.Label(name=label.name, value=label.value))
    return labels


def parse_input_data(ocm_input: ocm_input_model.OcmInput, repoCtx: str, path: Path | str) -> cm.ComponentDescriptor:
    repoCtx = cm.OciRepositoryContext(
                baseUrl=repoCtx,
                subPath=None,
                type=cm.AccessType.OCI_REGISTRY
    )
    resources = process_resources(ocm_input, path)
    labels = process_labels(ocm_input)

    component = cm.Component(
        creationTime=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
        name=ocm_input.name,
        version=ocm_input.version,
        provider=ocm_input.provider,
        repositoryContexts=[repoCtx],
        sources=[],
        componentReferences=[],
        resources=resources,
        labels=labels,
    )

    cd = cm.ComponentDescriptor(
        meta=cm.Metadata(schemaVersion=cm.SchemaVersion.V2),
        component=component,
        signatures=[],
    )
    return cd

def process_input(ocm_input: ocm_input_model.OcmInput, repoCtx: str, out_prefix: str):
    path = Path(out_prefix)
    path.mkdir(parents=True, exist_ok=True)
    cd = parse_input_data(ocm_input, repoCtx, path)
    path = path / 'component-descriptor.yaml'
    write_cd(path, cd)

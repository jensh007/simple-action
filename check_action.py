from dataclasses import dataclass
import dataclasses
import datetime
import os
import dacite
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

def digest_and_store_file(fname: str) -> tuple[str, int]:
    sha = digest_file(fname)
    os.makedirs('blobs', exist_ok=True)
    dest_name = f'blobs/sha256.{sha}'
    shutil.copyfile(fname, dest_name)
    len = os.path.getsize(dest_name)
    return sha, len


def process_resources(ocm_input: ocm_input_model.OcmInput) -> list[cm.Resource]:
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
                res_name = res_name.replace('.', '_')
                sha, len  = digest_and_store_file(name)
                print(f'sha of {chart_name} is: {sha}')
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
    return resources


def parse_input_data(ocm_input: ocm_input_model.OcmInput, repoCtx: str) -> cm.ComponentDescriptor:
    repoCtx = cm.OciRepositoryContext(
                baseUrl=repoCtx,
                subPath=None,
                type=cm.AccessType.OCI_REGISTRY
    )
    resources = process_resources(ocm_input)

    component = cm.Component(
        creationTime=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
        name=ocm_input.name,
        version=ocm_input.version,
        provider=ocm_input.provider,
        repositoryContexts=[repoCtx],
        sources=[],
        componentReferences=[],
        resources=resources,
    )
    cd = cm.ComponentDescriptor(
        meta=cm.Metadata(schemaVersion=cm.SchemaVersion.V2),
        component=component,
        signatures=[],
    )
    return cd


def main():
    in_dict = {
        'name': 'github.com/jensh007/microblog',
        'provider': 'github.com/jensh007',
        'helm_charts': [
            'charts/mariadb.tgz:11.4.2',
            'https://charts.bitnami.com/bitnami/mariadb:10.11.2'
        ],
        'images': [
            'ghcr.io/jensh007/ocm/ocm.software/ocmcli-image:0.3.0-rc.2',
            'foo/bar:1.0.0'
        ],
        'files': [
            {
                'content_type': 'text/markdown',
                'name': 'readme.md'
            },
        ],
        'labels': [
            {
                'name': 'last-scanned',
                'value': '2023-06-21T18:00:00'
            },
            {
                'name': 'registry-provider',
                'position': 'resources/images',
                'value': 'Google'
            }
        ],
        'references': [
            {
                'componentName': 'github.com/jensh007/mariadb:10.11.2',
                'name': 'mariadb',
                'version': '10.11.2'
            }
        ],
        'version': '1.0.0'
    }

    ocm_input = dacite.from_dict(
            data_class=ocm_input_model.OcmInput,
            data=in_dict
    )

    repoCtx = 'ghcr.io/jensh007/microblog/ocm'

    cd = parse_input_data(ocm_input, repoCtx)

    print(f'OCM-Input is {ocm_input}')
    # cd = create_cd()
    write_cd('component-descriptor.yaml', cd)


if __name__ == '__main__':
    main()
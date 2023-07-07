import dacite

import component_creator

import ocm_input_model

def main():
    in_dict = {
        'name': 'github.com/jensh007/microblog',
        'provider': 'github.com/jensh007',
        'helm_charts': [
            'charts/mariadb.tgz:11.4.2',
            # 'https://charts.bitnami.com/bitnami/mariadb:10.11.2'
        ],
        'images': [
            'docker.io/library/bitnami/mariadb:10.11.2',
        ],
        'files': [
            {
                'content_type': 'text/markdown',
                'name': 'README.md'
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
    print(f'OCM-Input is {ocm_input}')

    component_creator.process_input(ocm_input, repoCtx, 'gen/ca')


if __name__ == '__main__':
    main()
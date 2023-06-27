# simple-action

Simple Github action for simplified providing bill-of-deliveries using [Open Component Model](https://ocm.software/)

## Ideas:

* restrict on commonly used types and access/input-types:
  * oci images
  * helm charts
  * plain files
  * labels
* no additional config files: `resource.yaml`, `components.yaml`

## Disclaimer:

Work-in-progress, evaluation state, no working code, do not try

## Example:

```yaml
name: ocm-components
run-name: Build component version using simple-action
on:
  workflow_dispatch:
env:
  COMP_NAME: acme.org/simpleserver
  PROVIDER: github.com/acme
  CD_REPO: ghcr.io/acme/ocm
  OCI_URL: ghcr.io/acme
jobs:
  build-and-create-ocm:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3
      # setup workflow to use the OCM github action:
      - name: setup OCM
        uses: open-component-model/ocm-setup-action@main
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      - name: Set up Docker Context for Buildx
        id: buildx-context
        run: |
          docker context create builders
      - name: Set up Docker Buildx
        timeout-minutes: 5
        uses: docker/setup-buildx-action@v2
        with:
          version: latest
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build amd64 and arm64
        id: build_amd64
        uses: docker/build-push-action@v3
        with:
          push: true
          platforms: linux/amd64,linux/arm64
          tags: ${{ env.OCI_URL }}/${{ env.COMP_NAME }}:${{ env.VERSION }}
     # Create an OCM component descriptor:
      - name: create OCM
        uses: jensh007/simple-action@main
        with:
          name: microblog
          version: 1.0.0
          provider: github.com/jensh007
          images:
          - ${{ env.OCI_URL }}/${{ env.COMP_NAME }}:${{ env.VERSION }}
          - eu.gcr.io/k8s-lm/landscaper-controller:4.8.6
          helm_charts:
          - ./my-charts
          - https://charts.bitnami.com/bitnami/mariadb:10.11.2
          files:
            name: readme.md
            content-type: text/markdown
          references:
          - name: mariadb
            componentName: github.com/jensh007/mariadb:10.11.2
            version: ${MARIADB_VERSION}
          labels:
          - key: last-scanned
            value: 2023-06-21T18:00:00
          - position: resources/images
            key: registry-provider
            value: Google
```

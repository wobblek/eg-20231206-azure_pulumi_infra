# ...

```bash
poetry install
poetry run example.kron.pulumi_azure_20231204-cli


task help
task validate:fix validate

```

## Using docker devtools

```bash
make -C devtools -B
docker compose build


docker compose run --rm python-devtools task help
docker compose run --rm python-devtools task validate:fix validate

```

## Updating from template base

```bash
pipx run --spec=cruft cruft update
```

## ...

```bash
export PULUMI_BACKEND_URL="file://~"
pulumi whoami --verbose
pulumi stack init dev
poetry run pulumi --cwd infrastructure/pulumi up --yes --stack organization/20231204-pulumi-azure/dev


PULUMI_BACKEND_URL="file://~" poetry run pulumi --cwd infrastructure/pulumi stack export --stack dev | jq .
```

```bash

export PULUMI_BACKEND_URL="azblob://main?storage_account=sagt8izydevpulumi"
pulumi whoami --verbose
pulumi --cwd infrastructure/pulumi stack init organization/20231204-pulumi-azure/dev

# Transfer state
PULUMI_BACKEND_URL="file://~" poetry run pulumi --cwd infrastructure/pulumi stack export --stack organization/20231204-pulumi-azure/dev --show-secrets | poetry run pulumi --cwd infrastructure/pulumi stack import --stack organization/20231204-pulumi-azure/dev
PULUMI_BACKEND_URL="file://~" pulumi stack rm organization/20231204-pulumi-azure/dev --yes --force

# poetry run pulumi --cwd infrastructure/pulumi stack export --stack dev | jq .
poetry run pulumi --cwd infrastructure/pulumi up --yes --stack organization/20231204-pulumi-azure/dev





poetry run pulumi --cwd infrastructure/pulumi stack --show-urns --stack dev


```

"""An Azure RM Python Pulumi program"""

import itertools
from uuid import UUID
import pulumi
import pulumi_azure_native as azure_native
import pulumi_azuread as azuread
import enum

# https://github.com/hashicorp/terraform-provider-azurerm/blob/83be143cdc3d35d366eae54fa1f35e16f9f7e20a/internal/services/subscription/subscription_resource.go

# pwgen -sA 6 1000 | grep '^[a-z]' | head
PROJECT_KEY = "gt8izy"

stack = pulumi.get_stack()

azure_client_config = azure_native.authorization.get_client_config()

pulumi.export("azure_client_config", azure_client_config)

azuread_client_config = azuread.get_client_config()

pulumi.export("azuread_client_config", azuread_client_config)

azuread_current_user = azuread.get_user(object_id=azuread_client_config.object_id)

pulumi.export("azuread_current_user", azuread_current_user)

resource_group = azure_native.resources.ResourceGroup(
    "pulumi",
    resource_group_name=f"rg-sb-{PROJECT_KEY}{stack}-pulumi",
    location="germanywestcentral",
)

storage_account = azure_native.storage.StorageAccount(
    "pulumi",
    account_name=f"sa{PROJECT_KEY}{stack}pulumi",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku=azure_native.storage.SkuArgs(
        name=azure_native.storage.SkuName.STANDARD_ZRS,
    ),
    kind=azure_native.storage.Kind.STORAGE_V2,
    minimum_tls_version=azure_native.storage.MinimumTlsVersion.TLS1_2,
    is_hns_enabled=True,
)

blob_container = azure_native.storage.BlobContainer(
    "main",
    container_name="main",
    resource_group_name=resource_group.name,
    account_name=storage_account.name,
)

USER_PRINCIPAL_NAMES = [
    "iwan.aucamp_outlook.com#EXT#@iwanaucampoutlook.onmicrosoft.com",
]

USERS: dict[str, azuread.GetUserResult] = {
    user.user_principal_name: user
    for user in azuread.get_users(user_principal_names=USER_PRINCIPAL_NAMES).users
}

USER_IDS = [user.object_id for user in USERS.values()]

class AzureRole(str, enum.Enum):
    # https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
    STORAGE_BLOB_DATA_OWNER = UUID("b7e6dc6d-f1e8-4753-8033-0f276bb0955b")

    def definition_id(self, subscription_id: str | None = None) -> str:
        if subscription_id is None:
            subscription_id = azure_client_config.subscription_id
        return f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{self.value}"


for user, role in itertools.product(
    USERS.values(), [AzureRole.STORAGE_BLOB_DATA_OWNER]
):
    azure_native.authorization.RoleAssignment(
        f"{user.user_principal_name}-{role.name}",
        principal_id=user.object_id,
        principal_type="User",
        role_definition_id=AzureRole.STORAGE_BLOB_DATA_OWNER.definition_id(),
        scope=storage_account.id,
    )

# https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-portal%2Clinux
# https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure



github_actions_application = azuread.Application("github-actions",
    display_name=f"urn:fdc:kron.example.com:20231206:{stack}:{PROJECT_KEY}:github-actions",
    owners=USER_IDS)
github_actions_service_principal = azuread.ServicePrincipal("github-actions",
    client_id=github_actions_application.client_id,
    app_role_assignment_required=False,
    owners=USER_IDS)

user_assigned_identity = azure_native.managedidentity.UserAssignedIdentity("userAssignedIdentity",
    location="eastus",
    resource_group_name="rgName",
    resource_name_="resourceName",
    tags={
        "key1": "value1",
        "key2": "value2",
    })


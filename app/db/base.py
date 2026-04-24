from app.shared.base import Base

# USERS + RBAC
from app.modules.users.models import (
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
)

# CLIENTS / PROJECTS
from app.modules.clients.models import (
    Client,
    ClientUser,
    Project,
)

# LEADS
from app.modules.leads.models import Lead

# QUOTATIONS
from app.modules.quotations.models import (
    Quotation,
    QuotationVersion,
    QuotationLineItem,
)

# PROJECT MODULES
from app.modules.project_modules.models import (
    ProjectModule,
    ModuleAssignment,
    ModuleVersion,
)

# APPROVALS
#from app.modules.approvals.models import Approval

# INVOICES
from app.modules.invoices.models import (
    Invoice,
    CreditNote,
)

# PAYMENTS
from app.modules.payments.models import Payment

# VAULT / RESOURCES
from app.modules.vault.models import Resource
import random
from langchain_core.tools import tool


@tool
def check_vm_status(vm_name: str, resource_group: str) -> str:
    """Check the status of an Azure Virtual Machine."""
    statuses = ["Running", "Stopped", "Deallocated", "Starting"]
    status = random.choice(statuses)
    return f"VM '{vm_name}' in resource group '{resource_group}': {status}"


@tool
def check_aks_cluster_health(cluster_name: str, resource_group: str) -> str:
    """Check the health of an Azure Kubernetes Service (AKS) cluster."""
    node_ready = random.randint(2, 5)
    node_total = node_ready + random.randint(0, 1)
    pod_count = random.randint(20, 80)
    health = "Healthy" if node_ready == node_total else "Degraded"
    return (
        f"AKS cluster '{cluster_name}' in '{resource_group}': {health}, "
        f"{node_ready}/{node_total} nodes ready, {pod_count} pods running"
    )


@tool
def get_azure_monitor_alerts(resource_group: str) -> str:
    """Get active Azure Monitor alerts for a resource group."""
    mock_alerts = [
        "[HIGH] CPU usage >90% on vm-prod-01 (triggered 15m ago)",
        "[MEDIUM] Memory pressure on aks-nodepool-01 (triggered 2h ago)",
        "[LOW] Storage account capacity >80% on stproddata (triggered 1d ago)",
    ]
    alert_count = random.randint(0, len(mock_alerts))
    if alert_count == 0:
        return f"No active alerts in resource group '{resource_group}'"
    selected = random.sample(mock_alerts, alert_count)
    return f"Active alerts in '{resource_group}':\n" + "\n".join(f"  • {a}" for a in selected)


@tool
def check_storage_account(account_name: str) -> str:
    """Check the status and usage of an Azure Storage Account."""
    used_gb = round(random.uniform(10, 900), 1)
    return (
        f"Storage account '{account_name}': Available, "
        f"{used_gb} GB used / 1 TB capacity ({round(used_gb / 10.24, 1)}% used)"
    )


@tool
def get_resource_group_cost(resource_group: str, period_days: int = 7) -> str:
    """Get estimated cost for a resource group over the specified number of days."""
    daily_cost = round(random.uniform(20, 500), 2)
    total_cost = round(daily_cost * period_days, 2)
    return (
        f"Cost estimate for '{resource_group}' over last {period_days} days: "
        f"${total_cost} USD (avg ${daily_cost}/day)"
    )

# ZETTADEMO2

Azure Function that tracks and stores Azure Virtual Network (VNET) configurations in Cosmos DB.

---

## 🌐 Features

- ✅ Automatic discovery of all VNETs in Azure subscription
- ✅ Detailed tracking of subnets and address spaces
- ✅ Storage in Cosmos DB for historical tracking

---

## 📁 Project Structure

```bash

vnet_tracker/
├── function_app/              # Function code
│   ├── __init__.py            # Main function
│   ├── function.json          # Function configuration
│   └── requirements.txt       # Python dependencies
├── host.json                  # Function host configuration
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11
- Azure CLI (logged in)
- Azure Functions Core Tools (for local dev and testing)
- Cosmos DB account
- Storage Account (for zip deploy)

---

### 🧪 Local Development

```bash
cd zettademo2
cp local.settings.example.json local.settings.json # Edit with your credentials
python -m zetta2venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install azure-functions-core-tools
func start
```

Access at http://localhost:7071/api/vnet-tracker

---



## ☁️ Deploy to Azure via URL with zip

### ✅ Prerequisites:
- An existing Function App
- A Storage Account with a Blob container
- The following app settings will be configured:
  - AZURE_SUBSCRIPTION_ID
  - COSMOS_ENDPOINT
  - COSMOS_KEY

```bash
cd zettademo2
zip -r functionapp.zip .

# Upload zip to blob
az storage blob upload \
  --account-name <storage-account> \
  --container-name <container-name> \
  --name functionapp.zip \
  --file ../functionapp.zip

# Generate SAS token
az storage blob generate-sas \
  --account-name <storage-account> \
  --container-name <container-name> \
  --name functionapp.zip \
  --permissions r \
  --expiry $(date -u -d "1 day" '+%Y-%m-%dT%H:%MZ') \
  --output tsv

# Provide the zip to the function app
az functionapp config appsettings set \
  --name <function-name> \
  --resource-group <resource-group> \
  --settings WEBSITE_RUN_FROM_PACKAGE="https://<storage-account>.blob.core.windows.net/<container-name>/functionapp.zip?<sas-token>"

# Restart just in case
az functionapp restart \
  --name <function-name> \
  --resource-group <resource-group>
```

## 📦 Example Output

```bash
{
  "status": "success",
  "data": [
    {
      "id": "zettademo2-zettademo2",
      "resource_id": "/subscriptions/********-****-****-****-************/resourceGroups/zettademo2/providers/Microsoft.Network/virtualNetworks/zettademo2",
      "name": "zettademo2",
      "location": "francecentral",
      "address_space": [
        "10.0.0.0/16"
      ],
      "subnets": [
        {
          "name": "default",
          "address_prefix": null,
          "id": "/subscriptions/********-****-****-****-************/resourceGroups/zettademo2/providers/Microsoft.Network/virtualNetworks/zettademo2/subnets/default"
        }
      ],
      "resource_group": "zettademo2"
    }
  ]
}

```
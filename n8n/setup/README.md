# Real Estate Agent Workflow — Setup

## What this is
A self-hosted n8n workflow that answers WhatsApp and Telegram customer messages about flats for **sale** or **rent**. If a customer wants to **sell**, the agent asks for the size and then shows matching inventory.

Inventory is stored in **Google Sheets**.

---

## Prereqs
- Docker + Docker Compose
- Google Cloud OAuth Client ID + Secret with Sheets access
- Gemini API key (`gemini-2.0-mini`)
- Plivo account + number
- Meta WhatsApp Business Platform account
- Telegram bot token from @BotFather

---

## 1) Run n8n
```bash
cd n8n
docker compose up -d
```
Open `http://localhost:5678`. On first login, change the default password.

---

## 2) Google Sheets
1. Create a spreadsheet named after your project.
2. Create a worksheet named exactly: `inventory`
3. Use these headers:
   ```
   m2,title,address,price,status,notes
   ```
4. Add rows for only these sizes: `86, 96, 92, 120`

A starter file is at `setup/google-sheets-template.csv`.

---

## 3) Credentials in n8n
Add under **Settings → Credentials**:
- **Google Sheets OAuth2** (`googleSheetsOAuth2Api`)
- **Gemini API key** (`googlePalmApi`)
- **Plivo** (`plivoApi`)
- **WhatsApp Business Cloud API** (`whatsappApi`)

---

## 4) Import workflow
1. Open **Workflows → Import from File**
2. Select `workflows/real-estate-agent-workflow.json`
3. After import, open each node and:
   - Select the matching credential
   - Replace placeholder expressions with real field mappings
   - For lookup nodes, choose the exact spreadsheet + `inventory` worksheet
   - For reply nodes, map `chat_id`, `recipient_wa_id`, and `message_text` from your trigger

---

## 5) Route messages in
Point your WhatsApp Business Cloud API and Plivo inbound webhooks to:
```
http://<your-server>:5678/webhook/real-estate-agent
```

If you use Telegram too, use the in-workflow Telegram reply node as the outbound channel.

---

## Supported flows
| Customer says | Agent does |
|---|---|
| “I want to buy a 96 m² flat” | Searches 96 m² inventory |
| “I want to rent a flat” | Asks preferred size: 86/96/92/120 |
| “I want to sell a flat” | Asks 86/96/92/120, then searches inventory |
| “Do you have any 120 m² flats?” | Searches 120 m² inventory |

---

## Security
- Never commit API keys.
- Regenerate the Telegram bot token if it was pasted in chat.
- Restrict webhook access by IP if possible.

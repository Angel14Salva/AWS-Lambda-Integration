# WhatsApp AI Bot — Moda Trujillo

A serverless WhatsApp chatbot for a retail store, built with Python on AWS Lambda. Handles product catalog browsing, price inquiries, and order placement — all through WhatsApp conversations.

**Live demo available on request.**

---

## Features

- Conversational menu with 4 flows: catalog, pricing, orders, order history
- Natural language understanding (handles variations like "quiero un polo", "cuánto cuesta el jean")
- Stock availability check before confirming orders
- Serverless architecture — scales automatically, zero server maintenance
- Response time under 1 second

## Tech Stack

| Layer | Technology |
|---|---|
| Messaging channel | WhatsApp (via Twilio) |
| Compute | AWS Lambda (Python 3.13) |
| API | AWS API Gateway (HTTP API) |
| Language | Python 3.13 |
| WhatsApp SDK | Twilio Helper Library |

## Architecture

```
Customer (WhatsApp)
        │
        ▼
  Twilio Sandbox
        │  POST /webhook
        ▼
AWS API Gateway
        │  trigger
        ▼
  AWS Lambda
  lambda_function.py
        │
        ▼
  TwiML Response
        │
        ▼
Customer receives reply
```

## Project Structure

```
moda-trujillo-bot/
├── lambda_function.py   # Main handler — all bot logic
├── package/             # Dependencies (Twilio SDK + deps)
├── bot.zip              # Deployment package for Lambda
└── README.md
```

## How It Works

1. Customer sends a WhatsApp message to the Twilio number
2. Twilio forwards the request as HTTP POST to the API Gateway endpoint
3. Lambda parses the message body, runs it through the conversation logic
4. Returns a TwiML XML response that Twilio delivers back to the customer

## Bot Conversation Flow

```
Customer: "hola"
Bot: Welcome menu (4 options)

Customer: "1"
Bot: Full product catalog with prices and availability

Customer: "quiero un polo"
Bot: Order confirmation with sizes, price, next steps

Customer: "2" or "precio jean"
Bot: Price, stock status, available sizes
```

## Setup & Deployment

### Prerequisites
- AWS account
- Twilio account with WhatsApp Sandbox enabled
- Python 3.10+

### Local setup

```bash
git clone https://github.com/YOUR_USERNAME/moda-trujillo-bot
cd moda-trujillo-bot
pip install twilio -t package/
cp lambda_function.py package/
cd package && zip -r ../bot.zip .
```

### Deploy to AWS Lambda

1. Create a Lambda function (Python 3.13, x86_64)
2. Upload `bot.zip` via the AWS Console
3. Add an HTTP API Gateway trigger (open security)
4. Copy the API Gateway endpoint URL

### Configure Twilio

1. Go to Twilio Console → Messaging → Try it out → WhatsApp Sandbox
2. In **Sandbox settings**, paste the API Gateway URL in "When a message comes in"
3. Set method to **POST**
4. Save

### Test

Send `hola` to your Twilio WhatsApp sandbox number. The bot should respond with the welcome menu.

## Customization

To adapt this bot for a different business, edit the `CATALOGO` dictionary in `lambda_function.py`:

```python
CATALOGO = {
    "producto_key": {
        "nombre": "Display Name",
        "precio": 99,
        "stock": True,
        "tallas": ["S", "M", "L"]
    },
}
```

No other changes needed for basic catalog customization.

---

## About

Built as a portfolio project demonstrating serverless WhatsApp automation on AWS.  
Stack: Python · AWS Lambda · API Gateway · Twilio WhatsApp API

Open to freelance projects — [Upwork profile](https://www.upwork.com)

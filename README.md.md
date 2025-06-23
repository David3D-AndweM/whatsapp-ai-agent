# 🌱 Resilient Equity WhatsApp AI Agent

An intelligent automated response system for WhatsApp Business API, built specifically for Resilient Equity Green Tech Foundation.

## 🚀 Features

- **Automated Message Processing**: Intelligent categorization and response to incoming WhatsApp messages
- **Template-Based Responses**: Pre-configured responses for common inquiries (partnerships, volunteering, CSR, etc.)
- **AI-Powered Responses**: Optional OpenAI integration for advanced conversational capabilities
- **Knowledge Base Integration**: Built-in information about Resilient Equity's mission, projects, and services
- **Web Dashboard**: Simple web interface to monitor agent status
- **WhatsApp Business API Integration**: Full integration with Meta's WhatsApp Business Platform

## 📋 Prerequisites

- Python 3.8 or higher
- WhatsApp Business Account
- Meta Developer Account
- (Optional) OpenAI API key for advanced AI responses

## 🛠️ Installation

1. **Clone or download this project**
   ```bash
   cd whatsapp-ai-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

## ⚙️ Configuration

### WhatsApp Business API Setup

1. **Create a Meta Developer Account**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a new app and select "Business"

2. **Set up WhatsApp Business API**
   - Add WhatsApp product to your app
   - Get your Phone Number ID: `740549401652542` (already configured)
   - Generate an access token

3. **Configure Webhook**
   - Set webhook URL: `https://your-domain.com/webhook`
   - Set verify token: `resilient_equity_verify_token`
   - Subscribe to `messages` events

### Environment Variables

Edit your `.env` file with the following values:

```env
# Required
WHATSAPP_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=740549401652542
VERIFY_TOKEN=resilient_equity_verify_token

# Optional (for AI responses)
OPENAI_API_KEY=your_openai_api_key

# Application settings
PORT=5000
DEBUG=False
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The application will be available at:
- **Dashboard**: http://localhost:5000
- **Webhook**: http://localhost:5000/webhook
- **Health Check**: http://localhost:5000/health

## 📱 Message Categories

The AI agent automatically categorizes and responds to different types of messages:

### 🤝 Partnership Inquiries
**Keywords**: partner, collaboration, work together, cooperate
**Response**: Information about partnership opportunities and next steps

### 🙋‍♀️ Volunteer/Internship
**Keywords**: volunteer, intern, join, help, contribute
**Response**: Volunteer application process and requirements

### 💰 CSR/Donor Engagement
**Keywords**: csr, donation, funding, sponsor, support
**Response**: CSR services and partnership information

### 💻 Project Information
**Keywords**: project, platform, claro, system, technology
**Response**: Details about Claro Non-Profit OS and other platforms

### 👋 General Inquiries
**Keywords**: hello, hi, info, about, what
**Response**: General foundation information and available services

## 🏗️ Project Structure

```
whatsapp-ai-agent/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This documentation
└── knowledge_base/       # Foundation information (from resilient_equity_kb)
    ├── email_templates.txt
    ├── faq.txt
    ├── mission.txt
    └── projects_summary.txt
```

## 🔧 Customization

### Adding New Message Templates

To add new response templates, edit the `MESSAGE_TEMPLATES` list in `app.py`:

```python
MessageTemplate(
    category='your_category',
    keywords=['keyword1', 'keyword2'],
    template="""Your response template here"""
)
```

### Updating Knowledge Base

The knowledge base is embedded in the `KNOWLEDGE_BASE` dictionary in `app.py`. Update this section to reflect any changes in:
- Foundation mission and values
- Project information
- Contact details
- Services offered

## 🚀 Deployment

### Using Heroku

1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git or GitHub integration

### Using Railway

1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically

### Using DigitalOcean App Platform

1. Create new app from GitHub
2. Configure environment variables
3. Set run command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

## 📊 Monitoring

- **Dashboard**: Access the web dashboard to monitor agent status
- **Logs**: Check application logs for message processing details
- **Health Check**: Use `/health` endpoint for uptime monitoring

## 🔒 Security

- Never commit your `.env` file to version control
- Use strong, unique tokens for webhook verification
- Regularly rotate your API keys
- Monitor webhook endpoint for unauthorized access

## 🆘 Troubleshooting

### Common Issues

1. **Webhook verification fails**
   - Check that `VERIFY_TOKEN` matches in both Meta console and `.env`
   - Ensure webhook URL is accessible from the internet

2. **Messages not being processed**
   - Verify WhatsApp token is valid and has necessary permissions
   - Check that phone number ID is correct
   - Review application logs for errors

3. **AI responses not working**
   - Ensure OpenAI API key is valid and has credits
   - Check OpenAI API status

## 📞 Support

For support with this WhatsApp AI Agent:

- **Email**: info@regtech.agency
- **Website**: https://resgreentech.tech/
- **Foundation**: Resilient Equity Green Tech Foundation

## 📄 License

Built for Resilient Equity Green Tech Foundation
*Empowering communities through technology, sustainability, and innovation.*

---

**Last Updated**: June 2025
**Version**: 1.0.0
**Built with**: Python, Flask, WhatsApp Business API, OpenAI
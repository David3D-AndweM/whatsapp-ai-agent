#!/usr/bin/env python3
"""
Resilient Equity WhatsApp AI Agent
Automated response system for WhatsApp Business API
Built for Resilient Equity Green Tech Foundation
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from flask import Flask, request, jsonify
import requests
import openai
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '740549401652542')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'resilient_equity_verify_token')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

@dataclass
class MessageTemplate:
    category: str
    keywords: List[str]
    template: str
    
# Knowledge Base - Loaded from the files we found
KNOWLEDGE_BASE = {
    'mission': """We are a Zambian youth-led non-profit organization dedicated to building resilient, transparent, and sustainable communities through the innovative use of technology and environmental stewardship.
    
    Our mission is to empower underserved communities, particularly young people, by:
    - Bridging the gap between technology and community development through practical, accessible digital solutions
    - Promoting environmental sustainability through education, awareness, and action on conservation, waste management, and climate resilience
    - Supporting transparency and accountability in community resource distribution, such as CSR projects and the Community Development Fund (CDF)
    - Offering training and capacity-building programs that equip young people with the skills needed to drive digital transformation
    - Championing inclusion by engaging schools, civil society, traditional leaders, and local government in tech-driven development conversations""",
    
    'projects': [
        {
            'name': 'Claro Non-Profit OS',
            'description': 'A comprehensive operating system designed for non-profits, CSR departments, and community development arms of corporate institutions.',
            'features': ['Project tracking dashboards', 'Real-time beneficiary reports', 'Fund request & approval workflows', 'Bulk SMS & alerts', 'Automated accountability and reporting']
        },
        {
            'name': 'CSR Transparency & Accountability Suite',
            'description': 'Custom-built digital platforms that help companies track and report on their CSR contributions across communities.',
            'features': ['Geo-tagged impact reports', 'Budget vs actual tracking', 'Survey tools and beneficiary feedback loops', 'Multi-user permissions and audit logs']
        },
        {
            'name': 'Youth Tech Hubs',
            'description': 'Grassroots initiative to establish mini tech hubs in peri-urban towns.',
            'features': ['Coding and AI literacy training', 'Civic tech education', 'Entrepreneurship support', 'Career mentorship']
        }
    ],
    
    'contact': {
        'email': 'info@regtech.agency',
        'website': 'https://resgreentech.tech/',
        'coordinator': 'M. Jeanee'
    }
}

# Message Templates based on the email templates we found
MESSAGE_TEMPLATES = [
    MessageTemplate(
        category='partnership',
        keywords=['partner', 'collaboration', 'work together', 'cooperate'],
        template="""Thank you for reaching out to Resilient Equity Green Tech Foundation! 🤝

We're always encouraged by individuals and organizations who believe in collective impact and tech-driven development.

We'd love to explore how we can work together. Could you share:
• A brief overview of your organization
• Your goals for this partnership
• Any preferred timelines

Once received, we'll arrange a suitable time for an exploratory call with our team.

We're excited about the possibility of creating lasting change together! 🌱

Contact: info@regtech.agency | https://resgreentech.tech/"""
    ),
    
    MessageTemplate(
        category='volunteer',
        keywords=['volunteer', 'intern', 'join', 'help', 'contribute'],
        template="""Thank you for expressing interest in volunteering with Resilient Equity Green Tech Foundation! 🙌

We love connecting with passionate people who want to support meaningful work in sustainability, technology, and community development.

To help us place you better, could you share:
• A short bio or CV
• Areas of interest (software development, community mobilization, research, etc.)
• Your availability (dates/times)

Once we receive this, we'll follow up with current opportunities or upcoming engagements.

We look forward to welcoming you to our growing network of changemakers! ✨

Contact: info@regtech.agency"""
    ),
    
    MessageTemplate(
        category='csr_donor',
        keywords=['csr', 'donation', 'funding', 'sponsor', 'support'],
        template="""We appreciate your outreach and willingness to support youth-led development and digital transparency! 💚

Our foundation has worked closely with mining companies, councils, and NGOs to implement CSR management platforms, reporting dashboards, and social engagement tools that align with SDG goals.

We'd be happy to provide:
• A brief project portfolio
• A proposal or capability overview
• Case studies from Zambia (e.g., KCM, local councils)

Let us know your preferred format or availability for a virtual session.

Thank you for considering a partnership with long-term community value! 🌍

Contact: info@regtech.agency"""
    ),
    
    MessageTemplate(
        category='projects_info',
        keywords=['project', 'platform', 'claro', 'system', 'technology'],
        template="""Thank you for showing interest in our digital platforms and initiatives! 💻

Our flagship solution, Claro Non-Profit OS, is a full-service operational system for CSR and community-focused programs. It includes:
• Project dashboards and reporting
• Grant and funding request portals
• Automated report generation and SMS notifications
• API integrations and secure data storage

We also offer custom implementations for mining companies, councils, and NGOs. Would you like a demo or detailed walkthrough?

Contact: info@regtech.agency | https://resgreentech.tech/"""
    ),
    
    MessageTemplate(
        category='general',
        keywords=['hello', 'hi', 'info', 'about', 'what'],
        template="""Hello! Thank you for reaching out to Resilient Equity Green Tech Foundation! 👋

We're a Zambian youth-led non-profit that builds digital systems to support transparency, sustainable development, and community empowerment.

Our work spans:
🌱 Environmental conservation
💻 Tech training and digital literacy
🏛️ Digital tools for CSR, CDF, and local government
🎓 Youth empowerment programs

How can we help you today? Feel free to ask about:
• Partnership opportunities
• Our projects and platforms
• Volunteer/internship opportunities
• CSR and community development solutions

Contact: info@regtech.agency | https://resgreentech.tech/"""
    )
]

class WhatsAppAIAgent:
    def __init__(self):
        self.app = Flask(__name__)
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.openai_client = openai
        else:
            self.openai_client = None
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/webhook', methods=['GET', 'POST'])
        def webhook():
            if request.method == 'GET':
                return self.verify_webhook()
            elif request.method == 'POST':
                return self.handle_message()
                
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            
        @self.app.route('/', methods=['GET'])
        def home():
            return self.render_dashboard()
    
    def verify_webhook(self):
        """Verify webhook for WhatsApp Business API"""
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == Config.VERIFY_TOKEN:
            logger.info('Webhook verified successfully')
            return challenge
        else:
            logger.warning('Webhook verification failed')
            return 'Verification failed', 403
    
    def handle_message(self):
        """Handle incoming WhatsApp messages"""
        try:
            data = request.get_json()
            logger.info(f'Received webhook data: {json.dumps(data, indent=2)}')
            
            if 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('field') == 'messages':
                                self.process_message(change['value'])
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f'Error handling message: {str(e)}')
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    def process_message(self, message_data):
        """Process individual message"""
        try:
            if 'messages' in message_data:
                for message in message_data['messages']:
                    sender = message['from']
                    message_text = message.get('text', {}).get('body', '')
                    message_id = message['id']
                    
                    logger.info(f'Processing message from {sender}: {message_text}')
                    
                    # Generate response
                    response = self.generate_response(message_text, sender)
                    
                    # Send response
                    if response:
                        self.send_message(sender, response)
                        
        except Exception as e:
            logger.error(f'Error processing message: {str(e)}')
    
    def generate_response(self, message_text: str, sender: str) -> str:
        """Generate appropriate response based on message content"""
        message_lower = message_text.lower()
        
        # Find matching template
        for template in MESSAGE_TEMPLATES:
            if any(keyword in message_lower for keyword in template.keywords):
                logger.info(f'Matched template category: {template.category}')
                return template.template
        
        # If no template matches, use AI if available
        if self.openai_client:
            return self.generate_ai_response(message_text)
        
        # Fallback to general template
        return MESSAGE_TEMPLATES[-1].template  # General template
    
    def generate_ai_response(self, message_text: str) -> str:
        """Generate AI response using OpenAI"""
        try:
            system_prompt = f"""You are an AI assistant for Resilient Equity Green Tech Foundation, a Zambian youth-led non-profit organization.
            
            Organization Info:
            {KNOWLEDGE_BASE['mission']}
            
            Contact: {KNOWLEDGE_BASE['contact']['email']} | {KNOWLEDGE_BASE['contact']['website']}
            
            Respond helpfully and professionally to inquiries. Keep responses concise but informative. Always include contact information when appropriate.
            Use emojis sparingly but appropriately. Focus on our mission of technology for social good, environmental sustainability, and youth empowerment."""
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_text}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f'Error generating AI response: {str(e)}')
            return MESSAGE_TEMPLATES[-1].template  # Fallback to general template
    
    def send_message(self, recipient: str, message: str):
        """Send message via WhatsApp Business API"""
        try:
            url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
            
            headers = {
                'Authorization': f'Bearer {Config.WHATSAPP_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': recipient,
                'type': 'text',
                'text': {'body': message}
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f'Message sent successfully to {recipient}')
            else:
                logger.error(f'Failed to send message: {response.status_code} - {response.text}')
                
        except Exception as e:
            logger.error(f'Error sending message: {str(e)}')
    
    def render_dashboard(self):
        """Render simple web dashboard"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resilient Equity WhatsApp AI Agent</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 2em; color: #2d5a27; margin-bottom: 10px; }}
                .status {{ display: inline-block; padding: 5px 15px; background: #4CAF50; color: white; border-radius: 20px; font-size: 0.9em; }}
                .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .info-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #2d5a27; }}
                .info-card h3 {{ margin: 0 0 10px 0; color: #2d5a27; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🌱 Resilient Equity WhatsApp AI Agent</div>
                    <div class="status">● Active</div>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📱 WhatsApp Integration</h3>
                        <p>Automated responses for WhatsApp Business API</p>
                        <p><strong>Phone ID:</strong> {Config.WHATSAPP_PHONE_NUMBER_ID}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🤖 AI Features</h3>
                        <p>Intelligent message categorization and responses</p>
                        <p><strong>Templates:</strong> {len(MESSAGE_TEMPLATES)} categories</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>📊 Knowledge Base</h3>
                        <p>Comprehensive information about our foundation</p>
                        <p><strong>Projects:</strong> {len(KNOWLEDGE_BASE['projects'])} active</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🔗 Contact</h3>
                        <p>Email: {KNOWLEDGE_BASE['contact']['email']}</p>
                        <p>Website: {KNOWLEDGE_BASE['contact']['website']}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Resilient Equity Green Tech Foundation - Empowering communities through technology, sustainability, and innovation.</p>
                    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def run(self):
        """Start the application"""
        logger.info('Starting Resilient Equity WhatsApp AI Agent...')
        logger.info(f'Dashboard available at: http://localhost:{Config.PORT}')
        logger.info(f'Webhook endpoint: http://localhost:{Config.PORT}/webhook')
        
        self.app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.DEBUG
        )

if __name__ == '__main__':
    agent = WhatsAppAIAgent()
    agent.run()
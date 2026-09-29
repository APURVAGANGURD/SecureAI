#!/usr/bin/env python3

import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

# Disable Flask's automatic .env loading to avoid encoding issues
os.environ['FLASK_SKIP_DOTENV'] = '1'

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
from openai import OpenAI, RateLimitError, APIError

# Load environment variables from existing .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

#  OPENAI API CONFIGURATION

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_ENABLED = False
client = None
AI_ERROR_MESSAGE = None

if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Test the API with a small request
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        AI_ENABLED = True
        print("✅ OpenAI API configured successfully")
        print(f"🔑 API Key found (starting with): {OPENAI_API_KEY[:10]}...")
    except RateLimitError as e:
        AI_ERROR_MESSAGE = "OpenAI API quota exceeded. Using rule-based responses. Please check your billing."
        print(f"⚠️  {AI_ERROR_MESSAGE}")
    except APIError as e:
        AI_ERROR_MESSAGE = f"OpenAI API Error: {str(e)[:100]}"
        print(f"⚠️  {AI_ERROR_MESSAGE}")
    except Exception as e:
        AI_ERROR_MESSAGE = f"OpenAI API Error: {str(e)[:100]}"
        print(f"⚠️  {AI_ERROR_MESSAGE}")
else:
    AI_ERROR_MESSAGE = "OpenAI API key not found or invalid in .env file. Using rule-based responses."
    print(f"⚠️  {AI_ERROR_MESSAGE}")
    if OPENAI_API_KEY:
        print(f"❌ Invalid API key format. Should start with 'sk-'. Found: {OPENAI_API_KEY[:20]}...")

def get_real_ai_response(user_message):
    """Get response from OpenAI API with better error handling"""
    if not AI_ENABLED or not client:
        return get_rule_based_response(user_message, show_error=True)
    
    try:
        # Cybersecurity expert system prompt
        system_prompt = """You are SecureAI, an expert cybersecurity assistant. You provide:
1. Accurate, practical cybersecurity advice
2. Step-by-step guidance for security tasks
3. Specific tool recommendations
4. Clear explanations of security concepts

Topics: Password security, phishing protection, WiFi safety, 
malware protection, privacy, data backup, 2FA, social engineering,
encryption, network security.

Format responses with bullet points and emojis for readability.
Keep responses concise but informative (200-400 words).
Always provide actionable advice."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except RateLimitError:
        error_msg = "⚠️ **API Quota Exceeded**\n\nMy OpenAI API quota has been exceeded. I'm switching to my built-in cybersecurity knowledge base.\n\n"
        return error_msg + get_rule_based_response(user_message)
    except APIError as e:
        error_msg = f"⚠️ **API Error**\n\nThere was an issue with the AI service: {str(e)[:100]}\n\n"
        return error_msg + get_rule_based_response(user_message)
    except Exception as e:
        error_msg = f"⚠️ **Connection Error**\n\nCould not connect to AI service. Using built-in responses.\n\n"
        return error_msg + get_rule_based_response(user_message)

def get_rule_based_response(user_message, show_error=False):
    """Rule-based cybersecurity responses"""
    user_message_lower = user_message.lower()
    
    # Enhanced response dictionary with more topics
    responses = {
        "password": """**🔐 Strong Password Guidelines:**

• **Length matters**: Use at least 12 characters (16+ for important accounts)
• **Mix character types**: Uppercase, lowercase, numbers, and symbols (!@#$%^&*)
• **Avoid common patterns**: Don't use dictionary words, sequences (123), or personal info
• **Password managers**: Use Bitwarden (free), 1Password, or KeePassXC
• **Never reuse passwords**: Each account gets a unique password
• **Passphrases work**: "CorrectHorseBatteryStaple!" is memorable and strong
• **Regular updates**: Change passwords every 90 days for critical accounts
• **Two-factor authentication**: Always enable 2FA when available""",
        
        "phishing": """**🎣 Phishing Detection & Prevention:**

**Red Flags to Watch For:**
1. **Urgent language**: "Your account will be closed in 24 hours!"
2. **Suspicious senders**: Slight misspellings like "support@amaz0n.com"
3. **Generic greetings**: "Dear customer" instead of your name
4. **Grammar errors**: Professional companies proofread their emails
5. **Suspicious links**: Hover to preview - don't trust displayed text
6. **Attachments**: Don't open unexpected attachments (.exe, .zip, .docm)

**Protection Steps:**
• Enable spam filters in your email
• Use browser extensions like Netcraft or PhishFort
• Verify by calling the company directly
• Keep software updated
• Educate family and colleagues""",
        
        "wifi": """**📶 Public Wi-Fi Security Guide:**

**✅ Do This:**
• Use a VPN (NordVPN, ExpressVPN, or ProtonVPN free tier)
• Verify network name with staff
• Disable auto-connect to Wi-Fi networks
• Use mobile data for sensitive transactions
• Enable firewall on your device
• Forget networks after use
• Use HTTPS Everywhere browser extension

**❌ Avoid This:**
• Banking or shopping without VPN
• Logging into important accounts
• Sending sensitive information
• File sharing on public networks
• Staying connected when not in use

**For Home Wi-Fi:**
• Change default router password
• Use WPA3 encryption (or WPA2)
• Hide SSID if not needed publicly
• Create guest network for visitors
• Keep router firmware updated""",
        
        "virus": """**🦠 Malware & Virus Protection:**

**Essential Protection:**
• **Antivirus**: Windows Defender (built-in), Bitdefender Free, Malwarebytes
• **Firewall**: Enable Windows Firewall or use a third-party option
• **Browser Security**: uBlock Origin, NoScript, HTTPS Everywhere
• **Email Protection**: Don't open attachments from unknown senders
• **Software Updates**: Enable automatic updates for all software

**Best Practices:**
• Use standard user accounts (not administrator)
• Disable autorun for external drives
• Backup files regularly (3-2-1 rule)
• Scan downloads before opening
• Be cautious with free software downloads
• Use ad-blockers to prevent malvertising

**If Infected:**
1. Disconnect from internet
2. Run full antivirus scan
3. Boot in safe mode if needed
4. Restore from backup if necessary
5. Change all passwords after cleanup""",
        
        "privacy": """**👁️ Online Privacy Protection:**

**Browser Settings:**
• Use Firefox with Privacy Badger, uBlock Origin
• Clear cookies regularly
• Disable third-party cookies
• Use private/incognito mode when needed
• Consider Brave or Tor for sensitive browsing

**Account Security:**
• Enable 2FA everywhere possible
• Use unique email for important accounts
• Check haveibeenpwned.com regularly
• Limit social media sharing
• Review privacy settings monthly

**Tools & Services:**
• Search: DuckDuckGo or Startpage
• Email: ProtonMail or Tutanota
• Messaging: Signal or Telegram (secret chats)
• VPN: For public Wi-Fi and additional privacy
• Password manager: For unique passwords""",
        
        "backup": """**💾 Data Backup Strategy (3-2-1 Rule):**

**3 Copies** of your data
**2 Different** media types
**1 Copy** offsite

**Local Backups:**
• **Windows**: File History or third-party tools
• **Mac**: Time Machine
• **External Drives**: Encrypt sensitive data
• **NAS**: For network backups

**Cloud Backups:**
• **Free**: Google Drive (15GB), OneDrive (5GB), Dropbox (2GB)
• **Paid**: Backblaze, iDrive, pCloud
• **Encrypted**: Cryptomator or VeraCrypt for sensitive files

**Automation:**
• Schedule regular backups
• Test restoration quarterly
• Keep multiple versions
• Monitor backup success

**Critical Data:**
• Documents
• Photos
• Financial records
• Passwords (export from manager)
• Important projects""",
        
        "2fa": """**🔑 Two-Factor Authentication Guide:**

**Best Methods:**
1. **Authenticator Apps**: Google Authenticator, Authy, Microsoft Authenticator
2. **Hardware Keys**: YubiKey, Google Titan (most secure)
3. **SMS Codes**: Good but vulnerable to SIM swapping
4. **Email Codes**: Better than nothing

**Priority Accounts:**
• Email (Gmail, Outlook, ProtonMail)
• Banking and financial apps
• Password manager
• Social media (Facebook, Twitter, Instagram)
• Cloud storage (Google Drive, Dropbox)

**Setup Tips:**
• Save backup codes in password manager
• Set up multiple methods if possible
• Avoid SMS for high-value accounts
• Register multiple devices
• Test recovery process

**Note**: Some services call this 2SV (two-step verification)""",
        
        "social media": """**📱 Social Media Security:**

**Privacy Settings:**
• Set profiles to private/friends only
• Review tags before they appear
• Limit location sharing
• Disable face recognition where possible
• Review connected apps monthly

**Information to Protect:**
• Phone number
• Home address
• Birth date (especially year)
• Relationship status
• Vacation plans (post after returning)

**Best Practices:**
• Use different passwords for each platform
• Enable 2FA on all social accounts
• Be cautious of quizzes and surveys
• Don't overshare personal details
• Regularly review friend lists
• Use separate email for social media""",
        
        "help": """**🤖 How I Can Help You:**

**🔐 Password Security**
• Creating strong passwords
• Password manager recommendations
• Password recovery strategies

**🎣 Phishing Protection**
• Identifying scam emails
• Safe email practices
• Reporting phishing attempts

**📶 Network Safety**
• Public Wi-Fi security
• Home network setup
• VPN recommendations

**🦠 Malware Defense**
• Antivirus software
• Virus removal steps
• Prevention strategies

**👁️ Privacy Protection**
• Browser privacy settings
• Data protection laws
• Anonymous browsing

**💾 Data Backup**
• Backup strategies
• Cloud storage options
• Disaster recovery

**🔑 Authentication**
• 2FA setup guides
• Biometric security
• Passwordless login

**📱 App Security**
• Permission management
• App store safety
• Mobile device security

**Ask me anything about these topics!**""",
        
        "hello": """👋 **Hello! I'm SecureAI, your cybersecurity assistant!**

I'm here to help you stay safe online with practical, actionable advice.

**Quick Start Topics:**
• 🔐 **Passwords**: Creating and managing secure passwords
• 🎣 **Phishing**: Spotting and avoiding email scams
• 📶 **Wi-Fi**: Securing home and public networks
• 🦠 **Viruses**: Protecting against malware and ransomware
• 👁️ **Privacy**: Keeping your personal information safe

**What's your biggest cybersecurity concern today?** 🚀""",
        
        "hi": """👋 **Hi there!** I'm SecureAI, ready to help with all your cybersecurity questions.

**Try asking me about:**
• "How do I create a strong password?"
• "What should I do if I clicked a phishing link?"
• "Is this website safe to use?"
• "How do I backup my important files?"
• "What's the best antivirus software?"

**Or explore these topics:**
🔐 Password security
🎣 Phishing detection
📶 Wi-Fi safety
🦠 Virus protection
👁️ Privacy tips
💾 Data backup
🔑 2FA setup

**What's on your mind?** 💭"""
    }
    
    # Check for keywords and return appropriate response
    response = None
    
    # Comprehensive keyword matching
    keywords = {
        "password": ["password", "passcode", "login", "credential", "passphrase"],
        "phishing": ["phishing", "scam", "spam", "email fraud", "suspicious email"],
        "wifi": ["wifi", "wireless", "network", "router", "internet connection"],
        "virus": ["virus", "malware", "antivirus", "ransomware", "trojan", "spyware"],
        "privacy": ["privacy", "private", "tracking", "data collection", "personal information"],
        "backup": ["backup", "restore", "recovery", "data loss", "cloud storage"],
        "2fa": ["2fa", "two factor", "authentication", "verification", "security code"],
        "social media": ["social media", "facebook", "instagram", "twitter", "tiktok", "linkedin"],
        "help": ["help", "what can you do", "capabilities", "topics", "assist"],
        "hello": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]
    }
    
    for topic, words in keywords.items():
        if any(word in user_message_lower for word in words):
            response = responses.get(topic)
            break
    
    # If no specific topic matched, provide general response
    if not response:
        response = """🤖 **I'm your AI cybersecurity assistant!**

I understand you're asking about cybersecurity. Here are some topics I can help with:

🔒 **Password Security** - Creating and managing strong passwords
🎣 **Phishing Protection** - Identifying and avoiding scams
📡 **Network Safety** - Securing Wi-Fi and internet connections
🛡️ **Device Protection** - Antivirus and malware prevention
👁️ **Privacy Tips** - Protecting your personal information
💾 **Data Backup** - Secure backup strategies
🔑 **Two-Factor Auth** - Adding extra security to accounts
📱 **App Permissions** - Managing what apps can access

**Try asking me something like:**
• 'How do I create a strong password?'
• 'What is phishing and how do I avoid it?'
• 'Is public Wi-Fi safe to use?'
• 'How do I backup my important files?'
• 'What should I do if my computer has a virus?'"""
    
    # Add error message if needed
    if show_error and AI_ERROR_MESSAGE:
        error_prefix = f"⚠️ **Note**: {AI_ERROR_MESSAGE}\n\n"
        return error_prefix + response
    
    return response

def get_ai_response(user_message):
    """Get AI response for chatbot - tries OpenAI first, falls back to rule-based"""
    # Try OpenAI API if available
    if AI_ENABLED:
        try:
            return get_real_ai_response(user_message)
        except Exception as e:
            print(f"AI API failed, using rule-based: {e}")
            return get_rule_based_response(user_message, show_error=True)
    else:
        return get_rule_based_response(user_message, show_error=True)

# ============================================
# SECURITY ANALYSIS FUNCTIONS
# ============================================

def analyze_password_strength(password):
    """Analyze password strength"""
    if not password:
        return {"strength": "Empty", "score": 0, "feedback": ["Password is empty"]}
    
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 12:
        score += 30
        feedback.append("✓ Excellent length (12+ characters)")
    elif len(password) >= 8:
        score += 20
        feedback.append("✓ Good length (8+ characters)")
    else:
        feedback.append("✗ Too short - use at least 8 characters")
    
    # Character variety
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    if char_types >= 4:
        score += 40
        feedback.append("✓ Excellent character variety")
    elif char_types >= 3:
        score += 30
        feedback.append("✓ Good character variety")
    else:
        feedback.append("✗ Add more character types (uppercase, lowercase, numbers, symbols)")
    
    # Common passwords check
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome', 'password123']
    if password.lower() in common_passwords:
        score = 0
        feedback.append("✗ This is a very common password - choose something unique")
    
    # Strength rating
    if score >= 70:
        strength = "Strong"
        color = "#27ae60"
    elif score >= 50:
        strength = "Good"
        color = "#f39c12"
    elif score >= 30:
        strength = "Fair"
        color = "#e67e22"
    else:
        strength = "Weak"
        color = "#e74c3c"
    
    return {
        "strength": strength,
        "score": score,
        "color": color,
        "feedback": feedback,
        "length": len(password),
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_special": has_special
    }

def analyze_phishing_message(message, sender):
    """Analyze phishing message"""
    if not message:
        return {
            "risk_level": "Unknown",
            "score": 0,
            "indicators": ["No message provided"],
            "advice": ["Enter a message to analyze"]
        }
    
    analysis = {
        "risk_level": "Medium",
        "score": 50,
        "indicators": [],
        "advice": []
    }
    
    # Check common phishing indicators
    indicators = []
    advice = []
    
    # Check for urgency words
    urgency_words = ['urgent', 'immediately', 'important', 'verify', 'update', 'security', 'account']
    urgency_found = [word for word in urgency_words if word in message.lower()]
    if urgency_found:
        indicators.append(f"Urgency language detected: {', '.join(urgency_found)}")
        advice.append("Be cautious of messages creating artificial urgency")
    
    # Check for suspicious sender
    suspicious_domains = ['secure-update', 'account-verify', 'login-security', 'admin-notice']
    if any(domain in sender.lower() for domain in suspicious_domains):
        indicators.append("Suspicious sender domain")
        advice.append("Verify the sender's email address carefully")
    
    # Check for links
    if 'http://' in message or 'https://' in message:
        indicators.append("Contains links")
        advice.append("Don't click links without verifying the sender")
    
    # Check for personal info requests
    personal_info = ['password', 'credit card', 'social security', 'bank account', 'login']
    info_found = [word for word in personal_info if word in message.lower()]
    if info_found:
        indicators.append(f"Requests personal information: {', '.join(info_found)}")
        advice.append("Legitimate companies won't ask for sensitive info via email")
    
    # Calculate risk score
    risk_score = min(100, len(indicators) * 25)
    
    if risk_score >= 75:
        risk_level = "High Risk"
        color = "#e74c3c"
    elif risk_score >= 50:
        risk_level = "Medium Risk"
        color = "#f39c12"
    else:
        risk_level = "Low Risk"
        color = "#27ae60"
    
    return {
        "risk_level": risk_level,
        "score": risk_score,
        "color": color,
        "indicators": indicators if indicators else ["No obvious phishing indicators found"],
        "advice": advice if advice else ["Message appears safe, but always verify unexpected communications"]
    }

def analyze_website_url(url):
    """Analyze website safety"""
    if not url:
        return {
            "url": "",
            "risk_level": "Unknown",
            "has_https": None,
            "domain_analysis": [],
            "safety_tips": ["Enter a URL to analyze"]
        }
    
    # Store original URL for display
    original_url = url
    display_url = url if url.startswith(('http://', 'https://')) else f'https://{url}'
    
    # Initialize result structure matching your template
    result = {
        "url": original_url,
        "risk_level": "Medium",
        "has_https": None,
        "domain_analysis": [],
        "safety_tips": []
    }
    
    try:
        # Check for HTTPS
        has_https = display_url.startswith('https://')
        result["has_https"] = has_https
        
        if has_https:
            result["domain_analysis"].append("✅ URL uses HTTPS (secure connection)")
            result["safety_tips"].append("This site uses HTTPS, which encrypts data between your browser and the website")
        else:
            result["domain_analysis"].append("❌ URL does NOT use HTTPS")
            result["safety_tips"].append("Avoid entering sensitive information on non-HTTPS sites")
            result["risk_level"] = "High"
        
        # Analyze domain name
        parsed_url = urlparse(display_url)
        domain = parsed_url.netloc
        
        # Check for suspicious patterns
        suspicious_patterns = [
            ("login", "Contains 'login' - common in phishing sites"),
            ("secure", "Contains 'secure' - often used in fake sites"),
            ("account", "Contains 'account' - be cautious"),
            ("verify", "Contains 'verify' - common in scam sites"),
            ("bank", "Contains 'bank' - verify it's legitimate"),
            ("paypal", "Contains 'PayPal' - check carefully"),
            ("facebook", "Contains 'Facebook' - verify spelling"),
            ("amazon", "Contains 'Amazon' - check URL carefully")
        ]
        
        for pattern, message in suspicious_patterns:
            if pattern in domain.lower():
                result["domain_analysis"].append(f"⚠️ {message}")
                if result["risk_level"] != "High":
                    result["risk_level"] = "Medium"
        
        # Check for hyphens
        if '-' in domain and domain.count('-') > 2:
            result["domain_analysis"].append("⚠️ Multiple hyphens in domain (common in phishing)")
        
        # Check for numbers
        if any(char.isdigit() for char in domain.split('.')[0]):
            result["domain_analysis"].append("⚠️ Numbers in domain name (can be suspicious)")
        
        # Check domain length
        if len(domain) > 50:
            result["domain_analysis"].append("⚠️ Very long domain name")
        
        # Check for IP address
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        if re.search(ip_pattern, domain):
            result["domain_analysis"].append("⚠️ Uses IP address instead of domain name")
            result["risk_level"] = "High"
        
        # Check TLD
        common_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.in']
        has_common_tld = any(domain.endswith(tld) for tld in common_tlds)
        if has_common_tld:
            result["domain_analysis"].append("✅ Uses common top-level domain")
        else:
            result["domain_analysis"].append("⚠️ Uncommon top-level domain")
        
        # Add general safety tips
        result["safety_tips"].extend([
            "Always check for the padlock icon in your browser's address bar",
            "Verify the website's domain name spelling carefully",
            "Look for contact information and privacy policy",
            "Check website reviews and reputation online",
            "Use a password manager to avoid phishing sites",
            "Enable browser security features and keep software updated"
        ])
        
        # If no specific issues found, mark as low risk
        if len(result["domain_analysis"]) <= 2 and result["has_https"]:
            result["risk_level"] = "Low"
            result["domain_analysis"].append("✅ No major issues detected in URL structure")
        
    except Exception as e:
        result["domain_analysis"].append(f"⚠️ Analysis error: Could not fully analyze URL")
        result["safety_tips"].append("There was an error analyzing this URL. Proceed with caution.")
    
    return result

def analyze_app_permissions(permissions, app_name):
    """Analyze app permissions risk"""
    if not permissions:
        return {
            "risk_level": "Information Needed",
            "score": 0,
            "permissions_analysis": [],
            "recommendations": ["Select app permissions to analyze"]
        }
    
    high_risk_perms = [
        'sms', 'contacts', 'location', 'camera', 'microphone', 
        'storage', 'phone', 'calendar', 'call_log'
    ]
    medium_risk_perms = [
        'photos', 'media', 'files', 'notifications', 'network'
    ]
    
    high_risk_found = []
    medium_risk_found = []
    
    for perm in permissions:
        perm_lower = perm.lower()
        for high_perm in high_risk_perms:
            if high_perm in perm_lower:
                high_risk_found.append(perm)
                break
        for medium_perm in medium_risk_perms:
            if medium_perm in perm_lower and perm not in high_risk_found:
                medium_risk_found.append(perm)
                break
    
    # Calculate risk score
    risk_score = len(high_risk_found) * 30 + len(medium_risk_found) * 15
    risk_score = min(100, risk_score)
    
    # Generate analysis
    permissions_analysis = []
    if high_risk_found:
        permissions_analysis.append(f"High-risk permissions: {', '.join(high_risk_found)}")
    if medium_risk_found:
        permissions_analysis.append(f"Medium-risk permissions: {', '.join(medium_risk_found)}")
    
    # Determine risk level
    if risk_score >= 60:
        risk_level = "High Risk"
        color = "#e74c3c"
    elif risk_score >= 30:
        risk_level = "Medium Risk"
        color = "#f39c12"
    else:
        risk_level = "Low Risk"
        color = "#27ae60"
    
    # Generate recommendations
    recommendations = []
    if high_risk_found:
        recommendations.append("Consider if the app really needs these permissions")
        recommendations.append("Review the app's privacy policy")
    if medium_risk_found:
        recommendations.append("These permissions are typically acceptable for most apps")
    
    recommendations.append("Only download apps from official app stores")
    recommendations.append("Regularly review and remove unused apps")
    
    return {
        "risk_level": risk_level,
        "score": risk_score,
        "color": color,
        "permissions_analysis": permissions_analysis,
        "recommendations": recommendations,
        "app_name": app_name,
        "total_permissions": len(permissions)
    }

def calculate_risk_score(answers):
    """Calculate personal risk score from assessment answers"""
    if not answers:
        return {"score": 0, "recommendations": ["Complete the assessment to get your score"]}
    
    total_score = 0
    max_score = 100
    
    # Convert answers to scores (answers should be 1-5, where 1=best, 5=worst)
    for key, value in answers.items():
        try:
            answer_value = int(value)
            # Convert 1-5 to 0-10 points per question
            question_score = (5 - answer_value) * 2  # 5=0, 4=2, 3=4, 2=6, 1=8
            total_score += question_score
        except (ValueError, TypeError):
            continue
    
    # Ensure score is within bounds
    total_score = min(total_score, max_score)
    
    # Determine risk level
    if total_score >= 80:
        risk_level = "Excellent"
        color = "#27ae60"
    elif total_score >= 60:
        risk_level = "Good"
        color = "#f39c12"
    elif total_score >= 40:
        risk_level = "Needs Improvement"
        color = "#e67e22"
    else:
        risk_level = "High Risk"
        color = "#e74c3c"
    
    # Generate recommendations
    recommendations = generate_recommendations(answers, total_score)
    
    return {
        "score": total_score,
        "risk_level": risk_level,
        "color": color,
        "recommendations": recommendations
    }

def generate_recommendations(answers, score):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Password recommendations
    q1 = int(answers.get('q1', 3))
    if q1 >= 3:
        recommendations.append("Use a password manager to create and store unique passwords for each account")
    
    # 2FA recommendations
    q2 = int(answers.get('q2', 3))
    if q2 >= 3:
        recommendations.append("Enable Two-Factor Authentication on important accounts (email, banking, social media)")
    
    # Phishing recommendations
    q3 = int(answers.get('q3', 3))
    if q3 >= 3:
        recommendations.append("Learn to identify phishing emails by checking sender addresses and avoiding suspicious links")
    
    # Update recommendations
    q4 = int(answers.get('q4', 3))
    if q4 >= 3:
        recommendations.append("Enable automatic updates on all your devices and software")
    
    # Wi-Fi recommendations
    q5 = int(answers.get('q5', 3))
    if q5 >= 3:
        recommendations.append("Use a VPN when connecting to public Wi-Fi networks")
    
    # App permission recommendations
    q6 = int(answers.get('q6', 3))
    if q6 >= 3:
        recommendations.append("Review app permissions regularly and only grant necessary access")
    
    # Backup recommendations
    q7 = int(answers.get('q7', 3))
    if q7 >= 3:
        recommendations.append("Set up automatic backups using cloud storage and external drives")
    
    # Social media recommendations
    q8 = int(answers.get('q8', 3))
    if q8 >= 3:
        recommendations.append("Review and tighten your social media privacy settings")
    
    # General recommendations based on score
    if score < 60:
        recommendations.append("Consider taking a basic cybersecurity course to improve your knowledge")
        recommendations.append("Install reputable antivirus software and keep it updated")
    
    return recommendations

# ============================================
# ROUTE DEFINITIONS
# ============================================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/password-analyzer', methods=['GET', 'POST'])
def password_analyzer():
    """Password Security Module"""
    result = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        result = analyze_password_strength(password)
    
    return render_template('password.html', result=result)

@app.route('/phishing-analyzer', methods=['GET', 'POST'])
def phishing_analyzer():
    """Phishing & Scam Analyzer"""
    result = None
    if request.method == 'POST':
        message = request.form.get('message', '')
        sender = request.form.get('sender', '')
        result = analyze_phishing_message(message, sender)
    
    return render_template('phishing.html', result=result)

@app.route('/two-factor-auth')
def two_factor_auth():
    """2FA Awareness Tool"""
    return render_template('2fa.html')

@app.route('/app-permissions', methods=['GET', 'POST'])
def app_permissions():
    """App Permission Risk Analyzer"""
    result = None
    if request.method == 'POST':
        permissions = request.form.getlist('permissions')
        app_name = request.form.get('app_name', '')
        result = analyze_app_permissions(permissions, app_name)
    
    return render_template('app_permissions.html', result=result)

@app.route('/public-wifi')
def public_wifi():
    """Public Wi-Fi Risk Advisor"""
    return render_template('wifi.html')

@app.route('/data-backup')
def data_backup():
    """Secure Data Backup Planner"""
    return render_template('backup.html')

@app.route('/digital-footprint')
def digital_footprint():
    """Digital Footprint Awareness Tool"""
    return render_template('footprint.html')

@app.route('/fake-profile')
def fake_profile():
    """Fake Profile & Impersonation Awareness"""
    return render_template('fake_profile.html')

@app.route('/risk-score', methods=['GET', 'POST'])
def risk_score():
    """Personal Cyber Security Risk Score"""
    score = None
    recommendations = []
    
    if request.method == 'POST':
        answers = {}
        for i in range(1, 11):
            key = f'q{i}'
            answers[key] = request.form.get(key, '3')
        
        result = calculate_risk_score(answers)
        score = result['score']
        recommendations = result['recommendations']
        
        # Store in session
        session['risk_score'] = score
    
    return render_template('risk_score.html', score=score, recommendations=recommendations)

@app.route('/ai-assistant', methods=['GET', 'POST'])
def ai_assistant():
    """AI Cyber Security Assistant Chatbot - ENHANCED VERSION"""
    messages = session.get('chat_history', [])
    
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            # Add timestamp to user message
            user_msg = {
                'role': 'user', 
                'content': user_message,
                'timestamp': datetime.now().strftime('%H:%M')
            }
            messages.append(user_msg)
            
            # Get AI response (uses OpenAI API if available)
            ai_response = get_ai_response(user_message)
            ai_msg = {
                'role': 'assistant', 
                'content': ai_response,
                'timestamp': datetime.now().strftime('%H:%M')
            }
            messages.append(ai_msg)
            
            # Update session (keep last 20 messages to prevent session bloat)
            session['chat_history'] = messages[-20:]
    
    return render_template('ai_assistant.html', messages=messages, ai_enabled=AI_ENABLED, ai_error=AI_ERROR_MESSAGE)

@app.route('/dashboard')
def dashboard():
    """User Dashboard"""
    score = session.get('risk_score', 'Not calculated yet')
    return render_template('dashboard.html', risk_score=score)

@app.route('/website-safety', methods=['GET', 'POST'])
def website_safety():
    """Website Safety Explainer"""
    result = None
    if request.method == 'POST':
        url = request.form.get('url', '')
        result = analyze_website_url(url)
    
    return render_template('website.html', result=result)

# ============ API ENDPOINTS ============

@app.route('/api/analyze-password', methods=['POST'])
def api_analyze_password():
    """API endpoint for password analysis"""
    data = request.json
    password = data.get('password', '')
    result = analyze_password_strength(password)
    return jsonify(result)

@app.route('/api/analyze-phishing', methods=['POST'])
def api_analyze_phishing():
    """API endpoint for phishing analysis"""
    data = request.json
    message = data.get('message', '')
    sender = data.get('sender', '')
    result = analyze_phishing_message(message, sender)
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chatbot"""
    data = request.json
    user_message = data.get('message', '')
    response = get_ai_response(user_message)
    
    # Update session if available
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    session['chat_history'].append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    # Keep only last 20 messages
    session['chat_history'] = session['chat_history'][-20:]
    
    return jsonify({'response': response, 'ai_enabled': AI_ENABLED})

@app.route('/api/clear-chat', methods=['POST'])
def api_clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    return jsonify({'status': 'success'})

# ============ MAIN EXECUTION ============

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️  .env file not found.")
        print("💡 To enable AI features, create a .env file with:")
        print("   OPENAI_API_KEY=your_key_here")
        print("   # Or use free alternatives:")
        print("   # OPENROUTER_API_KEY=your_key_here")
        print("   # OLLAMA_API_KEY=ollama")
    
    # Run the app
    print("=" * 60)
    print("🚀 Starting SecureAI on http://127.0.0.1:5000")
    print("=" * 60)
    print(f"📁 Templates directory: templates/")
    print(f"🔑 OpenAI API Status: {'✅ ENABLED' if AI_ENABLED else '⚠️ DISABLED'}")
    if AI_ENABLED:
        print(f"🤖 AI Assistant: Enhanced with GPT-3.5 Turbo")
    else:
        if AI_ERROR_MESSAGE:
            print(f"🤖 AI Assistant: {AI_ERROR_MESSAGE[:80]}...")
        else:
            print(f"🤖 AI Assistant: Using comprehensive rule-based responses")
    
    app.run(debug=True, port=5000, use_reloader=False)
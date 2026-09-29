"""
AI-based analysis functions for SecureAI
"""

import re
import random
from typing import Dict, List, Tuple
import nltk
from textblob import TextBlob
import urllib.parse

# Download NLTK data (first time only)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AIAnalyzer:
    """AI-based cybersecurity analyzer"""
    
    # Common weak passwords
    WEAK_PASSWORDS = [
        'password', '123456', 'qwerty', 'admin', 'welcome',
        'password123', '123456789', '12345678', '12345'
    ]
    
    # Phishing indicators
    PHISHING_KEYWORDS = [
        'urgent', 'immediately', 'verify', 'confirm', 'suspended',
        'locked', 'security alert', 'unauthorized', 'click here',
        'login now', 'update your information', 'prize', 'winner',
        'free', 'limited time', 'act now', 'account compromised'
    ]
    
    # Suspicious domains
    SUSPICIOUS_TLDS = ['.xyz', '.top', '.club', '.download', '.gq']
    
    # Dangerous app permissions
    DANGEROUS_PERMISSIONS = [
        'android.permission.READ_SMS',
        'android.permission.SEND_SMS',
        'android.permission.RECEIVE_SMS',
        'android.permission.READ_CONTACTS',
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.RECORD_AUDIO',
        'android.permission.CAMERA',
        'android.permission.READ_CALL_LOG'
    ]
    
    @staticmethod
    def analyze_password_strength(password: str) -> Dict:
        """Analyze password strength"""
        score = 0
        feedback = []
        suggestions = []
        
        # Check length
        if len(password) >= 12:
            score += 30
            feedback.append("✓ Password length is good (12+ characters)")
        elif len(password) >= 8:
            score += 15
            feedback.append("⚠ Password length is acceptable but could be longer")
            suggestions.append("Use at least 12 characters for better security")
        else:
            feedback.append("✗ Password is too short")
            suggestions.append("Use at least 8 characters, preferably 12+")
        
        # Check for common passwords
        if password.lower() in AIAnalyzer.WEAK_PASSWORDS:
            score = 0
            feedback.append("✗ This is a very common and weak password")
            suggestions.append("Avoid common passwords like 'password123' or '123456'")
        
        # Check character variety
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if has_upper and has_lower:
            score += 20
            feedback.append("✓ Contains both uppercase and lowercase letters")
        else:
            suggestions.append("Mix uppercase and lowercase letters")
        
        if has_digit:
            score += 20
            feedback.append("✓ Contains numbers")
        else:
            suggestions.append("Add numbers to your password")
        
        if has_special:
            score += 30
            feedback.append("✓ Contains special characters")
        else:
            suggestions.append("Add special characters (!@#$%^&*)")
        
        # Check for patterns
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            feedback.append("⚠ Avoid repeating characters (aaa, 111)")
            suggestions.append("Avoid repeating characters in sequence")
        
        # Determine strength level
        if score >= 80:
            strength = "Strong"
            color = "green"
        elif score >= 60:
            strength = "Medium"
            color = "orange"
        else:
            strength = "Weak"
            color = "red"
        
        # Generate secure password suggestion
        secure_password = AIAnalyzer.generate_secure_password()
        
        return {
            'score': min(100, max(0, score)),
            'strength': strength,
            'color': color,
            'feedback': feedback,
            'suggestions': suggestions,
            'secure_suggestion': secure_password
        }
    
    @staticmethod
    def generate_secure_password(length=16):
        """Generate a secure random password"""
        import string
        import secrets
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def analyze_phishing_message(message: str, sender: str = "") -> Dict:
        """Analyze message for phishing indicators"""
        score = 0
        indicators = []
        risk_level = "Low"
        recommendations = []
        
        # Convert to lowercase for analysis
        msg_lower = message.lower()
        
        # Check for urgency keywords
        urgency_count = 0
        for keyword in AIAnalyzer.PHISHING_KEYWORDS:
            if keyword in msg_lower:
                urgency_count += 1
                indicators.append(f"Contains urgency keyword: '{keyword}'")
        
        if urgency_count >= 3:
            score += 60
            risk_level = "High"
        elif urgency_count >= 1:
            score += 30
            risk_level = "Medium"
        
        # Check for suspicious links
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, message)
        
        if urls:
            indicators.append(f"Contains {len(urls)} link(s)")
            for url in urls[:3]:  # Check first 3 URLs
                parsed = urllib.parse.urlparse(url)
                if any(tld in parsed.netloc for tld in AIAnalyzer.SUSPICIOUS_TLDS):
                    score += 40
                    indicators.append(f"Suspicious domain: {parsed.netloc}")
                    recommendations.append(f"Avoid clicking links from suspicious domains like {parsed.netloc}")
        
        # Check sender (if provided)
        if sender:
            if '@' in sender:
                domain = sender.split('@')[-1]
                if any(tld in domain for tld in AIAnalyzer.SUSPICIOUS_TLDS):
                    score += 50
                    indicators.append(f"Suspicious sender domain: {domain}")
        
        # Check for grammar/spelling errors
        if len(message.split()) > 5:  # Only check if message is long enough
            blob = TextBlob(message)
            if len(message.split()) / max(1, len(blob.sentences)) > 20:
                score += 20
                indicators.append("Poor grammar or sentence structure detected")
        
        # Determine final risk level
        if score >= 70:
            risk_level = "High"
            color = "red"
        elif score >= 40:
            risk_level = "Medium"
            color = "orange"
        else:
            risk_level = "Low"
            color = "green"
        
        # Default recommendations
        if risk_level != "Low":
            recommendations.extend([
                "Do not click any links in this message",
                "Do not download attachments",
                "Verify the sender through official channels",
                "Never share personal information"
            ])
        
        return {
            'risk_score': min(100, score),
            'risk_level': risk_level,
            'color': color,
            'indicators': indicators,
            'recommendations': recommendations
        }
    
    @staticmethod
    def analyze_website_url(url: str) -> Dict:
        """Analyze website URL for safety indicators"""
        analysis = {
            'url': url,
            'has_https': False,
            'domain_analysis': [],
            'safety_tips': [],
            'risk_level': 'Unknown'
        }
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check HTTPS
            if parsed.scheme == 'https':
                analysis['has_https'] = True
                analysis['domain_analysis'].append("✓ Uses HTTPS (encrypted connection)")
            else:
                analysis['domain_analysis'].append("⚠ Does not use HTTPS - data may not be encrypted")
                analysis['safety_tips'].append("Avoid entering sensitive information on HTTP sites")
            
            # Check domain
            domain = parsed.netloc.lower()
            
            # Look for suspicious patterns
            if '--' in domain:
                analysis['domain_analysis'].append("⚠ Contains double hyphens (suspicious)")
            
            if any(tld in domain for tld in AIAnalyzer.SUSPICIOUS_TLDS):
                analysis['domain_analysis'].append("⚠ Uses less common TLD - be cautious")
            
            # Check for look-alike characters
            lookalikes = ['0', '1', 'l', 'I', '|', 'rn', 'm']
            for char in lookalikes:
                if char in domain:
                    analysis['domain_analysis'].append(f"⚠ Contains look-alike character '{char}'")
            
            # Subdomain analysis
            if domain.count('.') >= 3:
                analysis['domain_analysis'].append("⚠ Many subdomains - could be trying to mimic legitimate site")
            
            # Determine risk level
            warnings = len([msg for msg in analysis['domain_analysis'] if '⚠' in msg])
            if warnings >= 3:
                analysis['risk_level'] = 'High'
            elif warnings >= 1:
                analysis['risk_level'] = 'Medium'
            else:
                analysis['risk_level'] = 'Low'
            
            # Add general safety tips
            analysis['safety_tips'].extend([
                "Always check for HTTPS in the address bar",
                "Look for security indicators (padlock icon)",
                "Verify the domain name matches the legitimate site",
                "Be cautious of look-alike domains (amaz0n.com vs amazon.com)",
                "HTTPS does not guarantee a website is safe, only that data is encrypted"
            ])
            
        except Exception as e:
            analysis['error'] = f"Could not analyze URL: {str(e)}"
            analysis['risk_level'] = 'Unknown'
        
        return analysis
    
    @staticmethod
    def analyze_app_permissions(permissions: List[str], app_name: str = "") -> Dict:
        """Analyze app permissions for risks"""
        dangerous_found = []
        warning_found = []
        
        for perm in permissions:
            if perm in AIAnalyzer.DANGEROUS_PERMISSIONS:
                dangerous_found.append(perm)
            else:
                warning_found.append(perm)
        
        risk_score = len(dangerous_found) * 20 + len(warning_found) * 5
        
        if risk_score >= 60:
            risk_level = "High"
            color = "red"
        elif risk_score >= 30:
            risk_level = "Medium"
            color = "orange"
        else:
            risk_level = "Low"
            color = "green"
        
        recommendations = []
        if dangerous_found:
            recommendations.append(f"⚠ App requests {len(dangerous_found)} dangerous permissions")
            for perm in dangerous_found:
                simple_name = perm.split('.')[-1].replace('_', ' ').title()
                recommendations.append(f"  • {simple_name} - Consider if this app really needs this access")
        
        if app_name:
            recommendations.append(f"For '{app_name}', only grant permissions absolutely necessary for functionality")
        
        recommendations.extend([
            "Review permissions before installing any app",
            "Regularly audit app permissions in settings",
            "Uninstall apps that request unnecessary permissions",
            "Download apps only from official app stores"
        ])
        
        return {
            'risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'color': color,
            'dangerous_permissions': dangerous_found,
            'warning_permissions': warning_found,
            'recommendations': recommendations
        }
    
    @staticmethod
    def calculate_risk_score(answers: Dict) -> Dict:
        """Calculate personal cybersecurity risk score"""
        # Convert answers to scores (1-5 scale, where 5 is most risky)
        total_score = 0
        max_score = 50  # 10 questions * 5
        
        question_weights = {
            'q1': 1.2,  # Password habits
            'q2': 1.5,  # 2FA usage
            'q3': 1.0,  # Phishing awareness
            'q4': 1.0,  # Software updates
            'q5': 1.3,  # Public Wi-Fi
            'q6': 1.2,  # App permissions
            'q7': 1.1,  # Data backup
            'q8': 0.9,  # Social media sharing
            'q9': 1.4,  # Password manager
            'q10': 1.0  # Security software
        }
        
        for q, answer in answers.items():
            try:
                answer_value = int(answer)
                weight = question_weights.get(q, 1.0)
                total_score += answer_value * weight
            except ValueError:
                continue
        
        # Convert to 0-100 scale (higher = more risky)
        risk_percentage = int((total_score / max_score) * 100)
        security_score = 100 - risk_percentage  # Invert for security score
        
        # Determine risk level
        if security_score >= 80:
            risk_level = "Low Risk"
            color = "green"
        elif security_score >= 60:
            risk_level = "Medium Risk"
            color = "orange"
        else:
            risk_level = "High Risk"
            color = "red"
        
        # Generate recommendations based on answers
        recommendations = []
        
        # Password habits (q1)
        if answers.get('q1', '3') in ['4', '5']:
            recommendations.append("🔐 Consider using a password manager and creating stronger, unique passwords")
        
        # 2FA usage (q2)
        if answers.get('q2', '3') in ['4', '5']:
            recommendations.append("🔑 Enable Two-Factor Authentication on important accounts like email and banking")
        
        # Public Wi-Fi (q5)
        if answers.get('q5', '3') in ['4', '5']:
            recommendations.append("📶 Use a VPN when on public Wi-Fi and avoid sensitive activities")
        
        # App permissions (q6)
        if answers.get('q6', '3') in ['4', '5']:
            recommendations.append("📱 Review app permissions regularly and remove unnecessary access")
        
        # Data backup (q7)
        if answers.get('q7', '3') in ['4', '5']:
            recommendations.append("💾 Implement the 3-2-1 backup rule: 3 copies, 2 different media, 1 offsite")
        
        # General recommendations
        recommendations.extend([
            "🎓 Take time to learn about common cyber threats",
            "🔄 Regularly update your software and devices",
            "👀 Be skeptical of unsolicited messages and requests",
            "🔍 Periodically review your digital footprint"
        ])
        
        return {
            'score': security_score,
            'risk_level': risk_level,
            'color': color,
            'risk_percentage': risk_percentage,
            'recommendations': recommendations
        }
    
    @staticmethod
    def get_ai_response(user_input: str) -> str:
        """Get AI response for cybersecurity questions"""
        # Simple rule-based response system
        # In a production environment, you would integrate with OpenAI API
        
        user_lower = user_input.lower()
        
        responses = {
            'password': "For strong passwords: Use at least 12 characters, mix uppercase/lowercase letters, numbers, and symbols. Avoid dictionary words and personal information. Consider using a password manager.",
            
            'phishing': "Phishing attacks try to trick you into revealing sensitive information. Always verify sender addresses, don't click suspicious links, and never share passwords via email or messages.",
            
            '2fa': "Two-Factor Authentication adds an extra security layer. Even if someone gets your password, they need your phone or security key. Use authenticator apps like Google Authenticator instead of SMS when possible.",
            
            'wifi': "Public Wi-Fi is risky because others on the network might intercept your data. Use a VPN, avoid banking or shopping, and turn off auto-connect features.",
            
            'backup': "Follow the 3-2-1 backup rule: Keep 3 copies of important data, on 2 different types of media, with 1 copy stored offsite (like cloud storage).",
            
            'malware': "To avoid malware: Keep software updated, don't download from untrusted sources, use antivirus software, and be cautious of email attachments.",
            
            'social media': "Limit personal information on social media. Use privacy settings, disable location sharing, and be careful what you share publicly.",
            
            'vpn': "A VPN encrypts your internet connection, hiding your activity from your ISP and others on public networks. Choose a reputable, paid VPN service for best security."
        }
        
        # Find the most relevant topic
        for topic, response in responses.items():
            if topic in user_lower:
                return response
        
        # Default response
        default_responses = [
            "I'm here to help with cybersecurity questions! Could you be more specific about what you'd like to know?",
            "That's an important security consideration. Could you provide more details so I can give you the best advice?",
            "For detailed cybersecurity guidance, could you clarify which aspect you're concerned about? (passwords, phishing, 2FA, etc.)"
        ]
        
        return random.choice(default_responses)

# Module functions
def analyze_password_strength(password: str) -> Dict:
    return AIAnalyzer.analyze_password_strength(password)

def analyze_phishing_message(message: str, sender: str = "") -> Dict:
    return AIAnalyzer.analyze_phishing_message(message, sender)

def analyze_website_url(url: str) -> Dict:
    return AIAnalyzer.analyze_website_url(url)

def analyze_app_permissions(permissions: List[str], app_name: str = "") -> Dict:
    return AIAnalyzer.analyze_app_permissions(permissions, app_name)

def calculate_risk_score(answers: Dict) -> Dict:
    return AIAnalyzer.calculate_risk_score(answers)

def get_ai_response(user_input: str) -> str:
    return AIAnalyzer.get_ai_response(user_input)
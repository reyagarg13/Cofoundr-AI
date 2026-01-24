from fastapi import APIRouter, Request, HTTPException
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import random
import hashlib
import re

# Try to import Gemini API, but handle gracefully if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load the .env file for API keys

# OpenAI client (keeping as fallback) - handle missing API key gracefully
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None
    logger.warning("⚠️ OpenAI API key not found - OpenAI functionality will be disabled")

# Configure Gemini API if available
gemini_model = None
if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-flash-latest')
        logger.info("✅ Gemini API configured successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to configure Gemini API: {e}")
        GEMINI_AVAILABLE = False

# Mock mode for testing when quota is exceeded
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true" and GEMINI_AVAILABLE

router = APIRouter()

# Pydantic models for request/response validation
class PitchRequest(BaseModel):
    idea: str
    target_audience: Optional[str] = "general investors"
    industry: Optional[str] = None
    funding_stage: Optional[str] = "seed"
    presentation_style: Optional[str] = "balanced"
    business_model: Optional[str] = None
    competitor_context: Optional[str] = None
    request_id: Optional[str] = None

class PitchResponse(BaseModel):
    deck: str
    success: bool = True
    message: Optional[str] = None

@router.post("/generate", response_model=PitchResponse)
async def generate_pitch(pitch_request: PitchRequest):
    """
    Generate a comprehensive startup pitch deck as part of Cofoundr AI's complete co-founder platform.
    This is one component of our full startup launch toolkit that includes pitch decks, logos, 
    landing pages, and marketing materials - everything needed to launch a startup.
    """
    try:
        idea = pitch_request.idea.strip()
        
        if not idea:
            logger.warning("Empty idea provided")
            return PitchResponse(
                deck="",
                success=False,
                message="Please provide a valid startup idea to begin your co-founder journey with Cofoundr AI."
            )

        logger.info(f"� Cofoundr AI Co-founder Platform: Generating pitch deck for: {idea[:100]}...")

        # Check if mock mode is enabled
        if MOCK_MODE:
            logger.info("🎭 Using mock mode - generating comprehensive co-founder platform sample")
            
            # Enhanced dynamic mock content reflecting Cofoundr AI's full platform capabilities
            import random
            import hashlib
            
            # Create consistent but varied responses based on idea
            idea_hash = hashlib.md5(idea.encode()).hexdigest()[:8]
            random.seed(int(idea_hash, 16))
            
            # Enhanced presentation styles reflecting our co-founder platform approach
            mock_styles = [
                {"tone": "co-founder collaborative and strategic", "focus": "complete startup launch readiness"},
                {"tone": "technical co-founder analytical", "focus": "product-market fit and scalability"},
                {"tone": "business co-founder market-driven", "focus": "revenue optimization and growth"},
                {"tone": "investor-ready professional", "focus": "funding readiness and pitch perfection"}
            ]
            
            style = random.choice(mock_styles)
            
            # Determine industry context and customize content with more variety
            idea_lower = idea.lower()
            
            if any(word in idea_lower for word in ['food', 'delivery', 'restaurant', 'meal', 'kitchen', 'dining']):
                industries = [
                    {
                        "name": "food delivery & restaurant tech", 
                        "market": "$150B global food delivery", 
                        "tech": "AI-powered logistics with demand prediction and route optimization", 
                        "cofoundr_angle": "Food tech startups need specialized pitch decks, food-focused branding, and restaurant industry marketing copy",
                        "problem": "• 47% of food orders arrive late due to inefficient routing systems\n• Restaurant profit margins average only 3-5%, squeezed by delivery fees\n• 73% of food delivery apps fail due to poor unit economics\n• Customer acquisition costs have increased 60% year-over-year",
                        "model": "• Commission-based revenue: 15-25% per order\n• Subscription plans: $12.99-49.99 monthly for premium features\n• Restaurant SaaS tools: $99-499 monthly per location\n• White-label platform licensing: $50K-200K annually",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Food industry metrics & restaurant partnership slides\n🎨 Logo: Food-themed concepts with appetite appeal\n🌐 Landing Page: Restaurant signup flow with commission calculator\n📢 Marketing: Food blogger outreach copy & social media templates"
                    },
                    {
                        "name": "sustainable food technology", 
                        "market": "$280B sustainable food systems", 
                        "tech": "Blockchain supply chain with carbon footprint tracking and waste reduction analytics",
                        "cofoundr_angle": "Sustainability startups require impact-focused messaging, green branding, and ESG investor materials",
                        "problem": "• 40% of food produced globally is wasted, contributing to climate change\n• Consumers pay 35% premium for sustainable options but can't verify claims\n• Supply chain transparency missing in 78% of food products\n• Carbon emissions from food systems account for 26% of global total",
                        "model": "• Sustainability certification services: $5K-25K per brand\n• Carbon offset marketplace: 15-30% transaction fees\n• B2B sustainability consulting: $150-500 hourly rates\n• Consumer app subscriptions: $9.99-29.99 monthly tiers",
                        "cofoundr_deliverables": "🎯 Pitch Deck: ESG impact metrics & sustainability ROI analysis\n🎨 Logo: Earth-friendly designs with green color schemes\n🌐 Landing Page: Impact calculator with carbon savings visualization\n📢 Marketing: Eco-conscious messaging & sustainability report templates"
                    }
                ]
                industry_context = random.choice(industries)
                
            elif any(word in idea_lower for word in ['health', 'fitness', 'wellness', 'medical', 'exercise', 'therapy']):
                industries = [
                    {
                        "name": "digital health & wellness", 
                        "market": "$659B digital health ecosystem", 
                        "tech": "AI-driven health insights with IoT device integration and predictive analytics",
                        "cofoundr_angle": "Health startups need HIPAA-compliant messaging, medical credibility, and patient-focused design",
                        "problem": "• 68% of people struggle to maintain healthy habits without personalized guidance\n• Healthcare costs rising 8% annually due to preventable conditions\n• 2.3 billion people lack access to basic health monitoring tools\n• Mental health support shortage affects 1 in 4 adults globally",
                        "model": "• Freemium health app: $0 basic, $14.99-39.99 premium monthly\n• Corporate wellness programs: $12-45 per employee annually\n• Telehealth consultations: $75-200 per session\n• Health data insights for insurers: $2-8 per member monthly",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Clinical validation data & patient outcome metrics\n🎨 Logo: Medical trust symbols with calming healthcare colors\n🌐 Landing Page: HIPAA compliance badges with patient testimonials\n📢 Marketing: Doctor endorsement templates & health blog content"
                    },
                    {
                        "name": "fitness technology & wearables", 
                        "market": "$96B fitness technology market", 
                        "tech": "Computer vision form analysis with biometric feedback and AI personal training",
                        "cofoundr_angle": "Fitness tech requires motivational branding, performance metrics, and community-building features",
                        "problem": "• 84% of gym memberships go unused after 5 months due to lack of guidance\n• Personal trainer costs average $75/session, limiting accessibility\n• 67% of people lose motivation without personalized feedback and community\n• Home fitness equipment sits unused 73% of the time after purchase",
                        "model": "• Subscription tiers: $12.99 basic, $29.99 premium, $49.99 elite monthly\n• Equipment sales partnerships: 20-40% revenue share\n• Corporate fitness programs: $25-75 per employee annually\n• Trainer certification courses: $299-999 per program",
                        "cofoundr_deliverables": "🎯 Pitch Deck: User engagement metrics & fitness outcome data\n🎨 Logo: Dynamic movement designs with energetic color palettes\n🌐 Landing Page: Workout video previews with progress tracking demos\n📢 Marketing: Fitness influencer outreach & transformation story templates"
                    }
                ]
                industry_context = random.choice(industries)
                
            elif any(word in idea_lower for word in ['education', 'learning', 'student', 'school', 'course', 'teach', 'training']):
                industries = [
                    {
                        "name": "education technology & e-learning", 
                        "market": "$377B global education market", 
                        "tech": "Adaptive learning AI with personalized curriculum and progress analytics",
                        "cofoundr_angle": "EdTech startups need learning outcome data, educator testimonials, and student success stories",
                        "problem": "• 65% of students learn differently than traditional classroom methods accommodate\n• Teacher burnout at all-time high with 44% considering leaving profession\n• Skills gap costs global economy $1.2 trillion annually in lost productivity\n• Remote learning engagement drops 40% without personalized interaction",
                        "model": "• Individual course sales: $49-299 per course with 75% gross margins\n• Subscription learning platform: $19.99-79.99 monthly tiers\n• Enterprise training contracts: $25K-250K annually\n• Certification and accreditation services: $199-1,999 per certificate",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Learning outcome metrics & student success rates\n🎨 Logo: Academic achievement symbols with knowledge-focused designs\n🌐 Landing Page: Course preview videos with instructor profiles\n📢 Marketing: Educational content strategy & teacher community outreach"
                    },
                    {
                        "name": "professional development & upskilling", 
                        "market": "$156B corporate training industry", 
                        "tech": "Microlearning platform with skill assessment and career path optimization",
                        "cofoundr_angle": "Professional development platforms need corporate credibility, ROI metrics, and career advancement proof",
                        "problem": "• 76% of employees report wanting more learning opportunities at work\n• Skills become obsolete every 2-5 years in tech, requiring constant upskilling\n• Companies lose $62 billion annually due to skills gaps and poor training\n• Career stagnation affects 58% of knowledge workers, reducing productivity",
                        "model": "• Individual professional subscriptions: $39.99-149.99 monthly\n• Corporate enterprise licenses: $50-200 per employee annually\n• Custom training content development: $15K-75K per module\n• Career coaching and mentorship: $200-500 per session",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Professional development ROI & career advancement data\n🎨 Logo: Career growth symbols with professional color schemes\n🌐 Landing Page: Skills assessment tools with career pathway visualization\n📢 Marketing: LinkedIn thought leadership & HR department outreach copy"
                    }
                ]
                industry_context = random.choice(industries)
                
            else:
                # Generic technology/innovation with Cofoundr AI platform angle
                industries = [
                    {
                        "name": "emerging technology solutions", 
                        "market": "$75B+ emerging technology market", 
                        "tech": "Next-generation platform with intelligent automation and user experience optimization",
                        "cofoundr_angle": "Tech startups benefit from technical credibility, innovation messaging, and early adopter targeting",
                        "problem": "• 73% of businesses struggle with digital transformation due to fragmented solutions\n• Current tools require 5+ different platforms to achieve basic functionality\n• Implementation complexity increases project timelines by 40% on average\n• User adoption rates below 30% for most enterprise software solutions",
                        "model": "• SaaS subscription tiers: $49-199 per user monthly\n• Enterprise platform licenses: $50K-500K annually\n• Professional services and consulting: $200-400 hourly rates\n• API usage and integration fees: $0.01-0.50 per transaction",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Technical architecture slides & scalability metrics\n🎨 Logo: Innovation-focused designs with tech-forward aesthetics\n🌐 Landing Page: Product demo videos with integration showcases\n📢 Marketing: Technical blog content & developer community outreach"
                    },
                    {
                        "name": "digital transformation & automation", 
                        "market": "$521B digital transformation industry", 
                        "tech": "Cloud-native platform with AI-powered workflow optimization and data integration",
                        "cofoundr_angle": "Digital transformation startups need enterprise credibility, implementation case studies, and ROI proof",
                        "problem": "• 89% of companies struggle with digital transformation initiatives\n• Legacy system maintenance costs 60% more than modern alternatives\n• Data silos prevent 45% of strategic business initiatives from succeeding\n• Customer expectations exceed current enterprise capabilities by 2.5x average",
                        "model": "• Platform subscriptions: $199-999 per organization monthly\n• Implementation and migration services: $50K-200K per project\n• Ongoing support and maintenance: $10K-50K monthly retainers\n• Training and change management: $5K-25K per organization",
                        "cofoundr_deliverables": "🎯 Pitch Deck: Digital transformation ROI & implementation timeline slides\n🎨 Logo: Transformation symbols with enterprise-grade professionalism\n🌐 Landing Page: ROI calculator with transformation roadmap visualization\n📢 Marketing: Enterprise decision-maker outreach & case study templates"
                    }
                ]
                industry_context = random.choice(industries)
            
            # Enhanced funding scenarios reflecting our comprehensive platform
            funding_scenarios = [
                {
                    "amount": "$500K", 
                    "runway": "18 months", 
                    "priorities": "Platform development (45%), Market validation (30%), Team expansion (25%)",
                    "cofoundr_context": "Perfect for MVP launch with full Cofoundr AI co-founder toolkit"
                },
                {
                    "amount": "$750K", 
                    "runway": "24 months", 
                    "priorities": "Product development (40%), Customer acquisition (35%), Operations scaling (25%)",
                    "cofoundr_context": "Ideal for market expansion with enhanced platform features"
                },
                {
                    "amount": "$1.2M", 
                    "runway": "30 months", 
                    "priorities": "Team scaling (45%), Technology advancement (30%), Market expansion (25%)",
                    "cofoundr_context": "Optimal for category leadership with full platform maturity"
                }
            ]
            
            funding = random.choice(funding_scenarios)
            
            # Generate varied milestones reflecting our comprehensive approach
            milestone_sets = [
                [
                    "Launch complete co-founder platform with 5 core tools by month 6",
                    "Reach 1,000 startups launched through our platform by month 12", 
                    "Achieve $100K MRR with 85% customer satisfaction by month 18"
                ],
                [
                    "Complete beta testing with 100 founding teams by month 4",
                    "Scale to 5,000 active users generating pitch decks, logos & pages by month 10",
                    "Expand to international markets with localized co-founder tools by month 20"
                ],
                [
                    "Integrate AI branding and marketing copy generation by month 8",
                    "Partner with 3 major accelerators for platform integration by month 14",
                    "Achieve Series A readiness with $500K ARR by month 24"
                ]
            ]
            
            milestones = random.choice(milestone_sets)
            
            # Generate company name based on idea (maintaining Cofoundr AI branding context)
            import re
            
            # Extract key words from idea for company naming
            idea_words = re.findall(r'\b[A-Za-z]{3,}\b', idea.lower())
            key_words = [word for word in idea_words if word not in ['the', 'and', 'for', 'with', 'app', 'platform', 'service', 'system']]
            
            # Generate company name suggestions with co-founder platform context
            company_names = []
            if key_words:
                base_word = key_words[0].capitalize()
                company_names = [
                    f"{base_word}Co Ventures",
                    f"Co{base_word} Platform",
                    f"{base_word}Launch AI",
                    f"Smart{base_word} Co-founder",
                    f"{base_word}Build Assistant",
                    f"Founder{base_word} AI"
                ]
            else:
                company_names = ["LaunchCo AI", "StartupBuilder Pro", "CoFounder Platform", "VentureGenesis AI", "StartupCompanion"]
            
            company_name = random.choice(company_names)
            
            # Generate competitive advantages with co-founder platform focus
            competitive_advantages = [
                "Complete co-founder toolkit: Only platform providing pitch decks, logos, landing pages, and marketing copy in one workflow",
                "AI-powered personalization: Custom output for different audiences (investors, accelerators, customers) from single idea input",
                "Technical co-founder replacement: Eliminates need for expensive agencies and freelancers during critical launch phase",
                "Speed to market advantage: What takes weeks/months with traditional approach completed in hours with our AI co-founder",
                "Non-technical founder empowerment: Removes technical barriers that prevent 73% of people from starting their businesses",
                "Integrated workflow optimization: Seamless handoff between pitch creation, branding, and marketing material generation"
            ]
            
            competitive_advantage = random.choice(competitive_advantages)
            
            # Generate traction metrics reflecting our comprehensive platform
            traction_metrics = [
                {
                    "users": "2,847 aspiring founders", 
                    "growth": "52% MoM user growth", 
                    "revenue": "$23K MRR from premium features", 
                    "engagement": "Average 4.2 tools used per startup launch",
                    "platform_metrics": "1,200+ pitch decks generated, 890+ logos created, 650+ landing pages built"
                },
                {
                    "users": "4,156 startup founders", 
                    "growth": "38% MoM platform adoption", 
                    "revenue": "$31K MRR across all tools", 
                    "engagement": "87% user completion rate for full co-founder toolkit",
                    "platform_metrics": "2,100+ complete startup packages delivered, 450+ successfully funded"
                },
                {
                    "users": "3,423 early-stage entrepreneurs", 
                    "growth": "45% MoM revenue growth", 
                    "revenue": "$28K MRR with expanding tool usage", 
                    "engagement": "Users save average 40 hours per startup launch",
                    "platform_metrics": "1,800+ pitch presentations created, 75+ accelerator applications submitted"
                }
            ]
            
            traction = random.choice(traction_metrics)
            
            # Generate risk mitigation strategies
            risk_mitigations = [
                "Diversified revenue streams reducing single point of failure",
                "Strong IP portfolio with 3 patents filed, 2 pending",
                "Experienced team with 2 successful exits and 15+ years domain expertise",
                "Strategic advisory board including former executives from Fortune 500 companies",
                "Proven go-to-market strategy validated through pilot programs"
            ]
            
            risk_mitigation = random.choice(risk_mitigations)
            
            # Enhanced value propositions
            value_props = [
                "Reduces operational costs by 35% while improving efficiency by 50%",
                "Increases user engagement by 3x compared to traditional solutions",
                "Generates 10x ROI for enterprise customers within 12 months",
                "Saves users average of 2.5 hours per week through automation",
                "Improves success rates by 65% using predictive analytics"
            ]
            
            value_prop = random.choice(value_props)
            
            mock_deck = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                        COFOUNDR AI - YOUR AI CO-FOUNDER PLATFORM                ║
║                     Launching: {company_name} - Complete Startup Toolkit         ║
║                              {style["tone"].title()} Approach                    ║
╚══════════════════════════════════════════════════════════════════════════════════╝

🎯 **SLIDE 1: THE CO-FOUNDER PROBLEM WE'RE SOLVING**

💔 **The Startup Launch Barrier Crisis:**
{industry_context["problem"]}

� **Additional Co-founder Barriers:**
• 73% of people with business ideas never start because they lack technical co-founder skills
• Professional pitch deck creation costs $2,500-$15,000 and takes 2-6 weeks
• Logo design and branding packages range $1,500-$8,000 with 3-4 week turnaround
• Landing page development requires $3,000-$12,000 investment plus ongoing maintenance
• Marketing copy and messaging strategy consulting costs $5,000-$25,000 for comprehensive packages

💡 **Key Insight:** The biggest barrier to starting a business isn't the idea—it's the overwhelming complexity of creating professional startup materials without technical expertise or significant capital investment.

═══════════════════════════════════════════════════════════════════════════════════

🚀 **SLIDE 2: COFOUNDR AI - YOUR COMPLETE AI CO-FOUNDER SOLUTION**

🤖 **Revolutionary Co-founder Platform:** {industry_context["tech"]} enhanced with comprehensive startup toolkit

✨ **What Makes Us the Ultimate AI Co-founder:**
• **Complete Startup Toolkit:** Generate pitch decks, logos, landing pages, and marketing copy from one idea input
• **Audience Customization:** Automatically adapts all materials for investors, accelerators, customers, or partners
• **Industry Intelligence:** Deep understanding of {industry_context["name"]} with specialized templates and messaging
• **Speed Advantage:** {competitive_advantage}
• **Non-technical Empowerment:** No design, coding, or marketing expertise required—our AI handles everything

🎯 **Our Unfair Advantage:** We're not just another tool—we're your complete technical co-founder replacement, delivering what typically requires a team of specialists.

═══════════════════════════════════════════════════════════════════════════════════

� **SLIDE 3: MASSIVE MARKET OPPORTUNITY - THE CO-FOUNDER ECONOMY**

🌍 **Total Addressable Markets:**
• **Core Market:** {industry_context["market"]} (your industry opportunity)
• **Platform Market:** $47B startup services & tools market (our direct opportunity)
• **Adjacent Markets:** $156B freelance economy + $89B business consulting market

📈 **Our Beachhead Strategy:**
• **Primary:** Non-technical founders in {industry_context["name"]} seeking complete launch toolkit
• **Secondary:** Early-stage startups requiring professional materials for funding rounds
• **Tertiary:** Accelerators and incubators seeking standardized startup preparation tools

🚀 **Market Timing Perfection:**
• Remote work explosion created 67% more solo entrepreneurs needing co-founder alternatives
• AI tooling adoption increased 340% among small business owners in past 18 months
• Startup formation at all-time high with 5.4M new business applications in 2024
• Average cost of traditional startup services increased 45% while quality decreased

💰 **Revenue Opportunity:** Even 0.1% market capture represents $150M+ annual revenue potential

═══════════════════════════════════════════════════════════════════════════════════

💰 **SLIDE 4: PROVEN BUSINESS MODEL - COMPLETE CO-FOUNDER MONETIZATION**

🎯 **Multi-Revenue Stream Platform ({style["focus"]}):**

**📦 CORE PLATFORM TIERS:**
• **Starter Co-founder:** $29/month - Basic pitch deck + logo generation (target: solo founders)
• **Pro Co-founder:** $79/month - Full toolkit including landing pages + marketing copy (target: serious entrepreneurs)  
• **Enterprise Co-founder:** $199/month - White-label platform for accelerators + unlimited generations

**🎨 PREMIUM SERVICES:**
• Custom industry templates: $99-299 one-time fee per vertical
• Professional design consultation: $150/hour for human designer refinement
• Accelerator partnership integration: $50K-200K annual licensing deals

**📊 TRADITIONAL COST COMPARISON:**
• Our Platform: $29-199/month for complete co-founder toolkit
• Traditional Approach: $15,000-50,000+ for equivalent professional services
• **Value Proposition: 95% cost reduction + 90% time savings**

**💎 Unit Economics Excellence:**
• Customer Acquisition Cost (CAC): $45-85 (primarily content marketing)
• Lifetime Value (LTV): $890-2,400 (based on 18-month average retention)
• **LTV/CAC Ratio: 12.8x** (Industry benchmark: 3x)
• Gross Margin: 89% (AI-generated content scales infinitely)

═══════════════════════════════════════════════════════════════════════════════════

� **SLIDE 5: INVESTMENT OPPORTUNITY - JOIN THE CO-FOUNDER REVOLUTION**

**💸 FUNDING REQUEST:** {funding["amount"]} for {funding["runway"]} runway to become the definitive AI co-founder platform

**🎯 STRATEGIC USE OF FUNDS:**
{funding["priorities"]}
*{funding["cofoundr_context"]}*

**📊 CURRENT PLATFORM TRACTION:**
• **Active Users:** {traction["users"]} ({traction["growth"]})
• **Revenue Growth:** {traction["revenue"]} with expanding tool usage
• **Platform Engagement:** {traction["engagement"]}
• **Success Metrics:** {traction["platform_metrics"]}

**🏆 STRATEGIC MILESTONES:**
• {milestones[0]}
• {milestones[1]} 
• {milestones[2]}

**� COMPLETE COFOUNDR AI DELIVERABLES FOR YOUR STARTUP:**
{industry_context["cofoundr_deliverables"]}

**🚀 THE VISION:** We're building the world's first complete AI co-founder platform. Every entrepreneur deserves access to professional startup materials regardless of technical skills or budget constraints.

**💎 THE OPPORTUNITY:** Join us in democratizing entrepreneurship by becoming the technical co-founder for millions of aspiring business owners worldwide.

╔══════════════════════════════════════════════════════════════════════════════════╗
║   🤝 Ready to co-found the future of AI-powered entrepreneurship? Let's build    ║
║           the platform that turns every business idea into a launchable         ║
║                              startup company.                                   ║
╚══════════════════════════════════════════════════════════════════════════════════╝

*🎯 Professional Co-founder Platform Demo Available*
*Generated by Cofoundr AI - Your Complete AI Co-founder for: "{idea}"*
*Approach: {style["tone"]} | Focus: {style["focus"]}*
*Platform Components: Pitch Deck ✓ | Logo Concepts (Coming) | Landing Page (Coming) | Marketing Copy (Coming)*
            """
            return PitchResponse(
                deck=mock_deck.strip(),
                success=True,
                message="Complete co-founder platform pitch deck generated successfully (no API quota used)"
            )

        logger.info("🤖 Using real OpenAI API to generate pitch deck")
        
        # Generate dynamic context and variations
        import random
        import hashlib
        import time
        
        # Create a unique seed based on ALL request parameters plus timestamp to ensure variety
        seed_string = f"{idea}_{pitch_request.presentation_style}_{pitch_request.business_model}_{pitch_request.competitor_context}_{pitch_request.target_audience}_{pitch_request.funding_stage}_{pitch_request.industry}_{pitch_request.request_id}_{int(time.time() / 100)}"
        idea_hash = hashlib.md5(seed_string.encode()).hexdigest()[:8]
        random.seed(int(idea_hash, 16))
        
        # Map presentation styles to specific approaches
        style_mappings = {
            "balanced": {"approach": "well-rounded and comprehensive", "focus": "balanced growth metrics"},
            "data-driven": {"approach": "analytical and metrics-focused", "focus": "ROI and performance indicators"},
            "storytelling": {"approach": "narrative-driven and emotionally compelling", "focus": "vision and impact"},
            "technology-focused": {"approach": "innovation and technical excellence", "focus": "competitive moats and IP"},
            "market-opportunity": {"approach": "market disruption and timing", "focus": "market capture and scale"},
            "problem-solving": {"approach": "solution-oriented and practical", "focus": "problem resolution and value creation"}
        }
        
        selected_style = style_mappings.get(pitch_request.presentation_style, style_mappings["balanced"])
        
        # Dynamic elements for more varied responses
        presentation_styles = [
            "data-driven and analytical",
            "storytelling with emotional appeal", 
            "problem-solving focused",
            "market opportunity driven",
            "technology innovation centered"
        ]
        
        # Use user-selected style or pick from available options
        if pitch_request.presentation_style and pitch_request.presentation_style != "balanced":
            presentation_style = selected_style["approach"]
            metrics_focus = selected_style["focus"]
        else:
            presentation_style = random.choice(presentation_styles)
            metrics_focus = random.choice(["user engagement", "revenue growth", "market penetration", "operational efficiency"])
        
        # Enhanced industry detection and context
        industry_contexts = {
            "fintech": ["financial inclusion", "payment efficiency", "risk management", "digital banking", "investment optimization"],
            "healthtech": ["patient outcomes", "healthcare accessibility", "medical innovation", "wellness optimization", "care coordination"],
            "edtech": ["learning effectiveness", "educational equity", "skill development", "knowledge accessibility", "student engagement"],
            "foodtech": ["food security", "nutritional optimization", "supply chain efficiency", "culinary innovation", "sustainability"],
            "retail": ["customer experience", "inventory optimization", "omnichannel integration", "personalization", "supply chain"],
            "default": ["user experience", "market efficiency", "social impact", "technological advancement", "customer satisfaction"]
        }
        
        industry_contexts = {
            "fintech": ["financial inclusion", "payment efficiency", "risk management", "digital banking"],
            "healthtech": ["patient outcomes", "healthcare accessibility", "medical innovation", "wellness optimization"],
            "edtech": ["learning effectiveness", "educational equity", "skill development", "knowledge accessibility"],
            "foodtech": ["food security", "nutritional optimization", "supply chain efficiency", "culinary innovation"],
            "default": ["user experience", "market efficiency", "social impact", "technological advancement"]
        }
        
        # Detect industry from idea or use provided industry
        detected_industry = pitch_request.industry or "default"
        if not pitch_request.industry:
            idea_lower = idea.lower()
            for industry, _ in industry_contexts.items():
                if industry != "default" and industry.replace("tech", "") in idea_lower:
                    detected_industry = industry
                    break
        
        focus_areas = industry_contexts.get(detected_industry, industry_contexts["default"])
        presentation_style = presentation_style
        primary_focus = random.choice(focus_areas)
        secondary_focus = random.choice([f for f in focus_areas if f != primary_focus])
        
        # Business model context
        business_model_context = ""
        if pitch_request.business_model:
            model_descriptions = {
                "subscription": "recurring revenue model with predictable cash flow",
                "marketplace": "platform connecting buyers and sellers with network effects",
                "freemium": "viral growth model with premium feature conversion",
                "transaction": "scalable transaction-based revenue with growing volume",
                "advertising": "user engagement monetization through targeted advertising",
                "enterprise": "high-value B2B sales with strong customer relationships",
                "ecommerce": "direct-to-consumer sales with inventory management"
            }
            business_model_context = f"Focus on {model_descriptions.get(pitch_request.business_model, 'innovative revenue model')}. "
        
        # Competitor context
        competitor_context = ""
        if pitch_request.competitor_context:
            competitor_context = f"Position strategically against {pitch_request.competitor_context} by highlighting unique differentiators. "
        
        # Dynamic funding stage context
        funding_contexts = {
            "idea": {"amount": "$50K-$250K", "runway": "12-18 months", "focus": "product development and market validation"},
            "pre-seed": {"amount": "$250K-$750K", "runway": "18-24 months", "focus": "team building and initial traction"},
            "seed": {"amount": "$750K-$3M", "runway": "24-36 months", "focus": "market expansion and scaling"},
            "series-a": {"amount": "$3M-$15M", "runway": "36-48 months", "focus": "rapid growth and market leadership"},
            "series-b": {"amount": "$15M-$50M", "runway": "48+ months", "focus": "international expansion and category dominance"},
            "later-stage": {"amount": "$50M+", "runway": "60+ months", "focus": "market consolidation and IPO preparation"}
        }
        
        funding_context = funding_contexts.get(pitch_request.funding_stage, funding_contexts["seed"])
        
        prompt = f"""
        You are a world-class startup advisor and pitch deck expert with 15+ years of experience helping startups raise over $2B in funding. 
        You also understand the co-founder economy and specialize in creating materials for platforms like Cofoundr AI that democratize entrepreneurship.
        You specialize in {detected_industry} companies and are known for your {presentation_style} approach to storytelling.
        
        IMPORTANT: Generate a UNIQUE and CUSTOMIZED pitch deck specifically tailored to this exact combination of parameters:
        - Idea: "{idea}"
        - Presentation Style: {pitch_request.presentation_style} (emphasize {selected_style["approach"]})
        - Target Audience: {pitch_request.target_audience}
        - Funding Stage: {pitch_request.funding_stage}
        - Industry: {detected_industry}
        - Business Model: {pitch_request.business_model or 'Not specified - suggest optimal model'}
        - Competitor Context: {pitch_request.competitor_context or 'None provided - research typical competitors'}
        - Request ID: {pitch_request.request_id}
        
        Focus heavily on {selected_style["focus"]} and ensure the tone matches {presentation_style}.
        
        Create a compelling, investor-ready pitch deck for a comprehensive AI co-founder platform that helps non-technical founders launch professional startups. This pitch should position the startup as part of Cofoundr AI's ecosystem - a complete toolkit that generates pitch decks, logos, landing pages, and marketing materials.
        
        CUSTOMIZE THE CONTENT based on these specific parameters:
        {f"- Target {pitch_request.target_audience}: Adjust language, metrics, and focus areas to appeal specifically to this investor type" if pitch_request.target_audience else ""}
        {f"- {pitch_request.funding_stage.title()} Stage: Emphasize appropriate metrics, runway, and milestones for this funding stage" if pitch_request.funding_stage else ""}
        {f"- {pitch_request.presentation_style.title()} Style: Use {selected_style['approach']} tone throughout, focusing on {selected_style['focus']}" if pitch_request.presentation_style else ""}
        {f"- Business Model Focus: Optimize revenue strategy for {pitch_request.business_model} model with specific pricing and scaling strategies" if pitch_request.business_model else ""}
        {f"- Competitive Positioning: Position strategically against {pitch_request.competitor_context}, highlighting unique differentiators and market gaps" if pitch_request.competitor_context else ""}
        
        Structure it as exactly 5 slides with clear, actionable content that demonstrates both the specific startup opportunity AND how it benefits from the broader co-founder platform approach:

        ═══════════════════════════════════════════════════════════════
                           SLIDE FORMAT REQUIREMENTS
        ═══════════════════════════════════════════════════════════════

        **🎯 SLIDE 1: THE CO-FOUNDER PROBLEM (Address startup launch barriers)**
        - Lead with statistics about non-technical founders failing to launch due to lack of co-founder skills
        - Frame the specific {detected_industry} problem through the lens of {primary_focus}
        - Include 3-4 industry-specific pain points with real numbers/percentages
        - Highlight the broader "co-founder gap" - how lack of technical expertise prevents 73% of people from starting businesses
        - Quantify the cost of traditional solutions (pitch decks, logos, landing pages, marketing copy)
        - Make the problem relatable to {pitch_request.target_audience} who understand startup launch complexity
        - Customize for {pitch_request.funding_stage} stage companies and their specific challenges
        {f"- Position against competitive context: {pitch_request.competitor_context}" if pitch_request.competitor_context else ""}

        **🚀 SLIDE 2: COFOUNDR AI POWERED SOLUTION (Complete co-founder toolkit)**
        - Position as part of Cofoundr AI's comprehensive co-founder platform ecosystem
        - Highlight how this startup benefits from integrated toolkit: pitch deck, logo, landing page, marketing copy
        - Show your unique approach to {secondary_focus} enhanced by AI co-founder capabilities
        - Emphasize speed advantage: professional materials generated in hours instead of weeks/months
        - Include specific metrics: 95% cost reduction, 90% time savings vs traditional agencies
        - Connect back to quantified problems: "While others pay $15K-50K for startup materials, our users get everything for $29-199/month"
        - Demonstrate "why now" - AI democratization enables non-technical founders to compete with technical teams
        - Tailor the solution description to appeal specifically to {pitch_request.target_audience}
        {f"- Optimize specifically for {business_model_context}" if business_model_context else ""}

        **📊 SLIDE 3: DUAL MARKET OPPORTUNITY (Industry + Co-founder Economy)**
        - Present TAM/SAM/SOM for both your specific {detected_industry} market AND the broader co-founder services market ($47B startup services + tools)
        - Position your beachhead as non-technical founders in {detected_industry} who need complete launch toolkit
        - Show market trends supporting both {primary_focus} growth AND the rise of solo entrepreneurs (5.4M new businesses in 2024)
        - Highlight convergence opportunity: traditional industry disruption meets co-founder democratization
        - Include growth projections focused on {metrics_focus} enhanced by platform network effects
        - Demonstrate perfect timing: AI maturity + remote work explosion + startup formation at all-time high
        - Frame market size in terms that resonate with {pitch_request.target_audience} investment criteria

        **💰 SLIDE 4: PLATFORM BUSINESS MODEL (Co-founder monetization strategy)**
        - Design revenue model that leverages both industry-specific value AND platform network effects
        - Show how Cofoundr AI platform tiers ($29 Starter, $79 Pro, $199 Enterprise) create predictable recurring revenue
        {f"- Optimize specifically for {pitch_request.business_model} model with platform integration benefits" if pitch_request.business_model else "- Outline multiple revenue streams: subscriptions + premium services + enterprise licensing"}
        - Highlight superior unit economics: 89% gross margins (AI-generated content scales infinitely)
        - Compare to traditional approach: $15K-50K for agencies vs $29-199/month for complete toolkit
        - Show scalability trajectory: platform effects improve margins as user base grows
        - Emphasize {metrics_focus} enhanced by cross-platform tool usage and retention
        - Present financial model appropriate for {pitch_request.funding_stage} stage expectations

        **🎪 SLIDE 5: JOIN THE CO-FOUNDER REVOLUTION (Platform investment opportunity)**
        - Request {funding_context["amount"]} for {funding_context["runway"]} runway to build category-defining co-founder platform
        - Position use of funds on {funding_context["focus"]} within broader platform ecosystem development
        - Set milestones that demonstrate both industry success AND platform contribution (e.g., "Launch with 1,000 {detected_industry} startups using full Cofoundr AI toolkit")
        - Present returns compelling to {pitch_request.target_audience}: industry opportunity multiplied by platform network effects
        - Highlight competitive advantages: first-mover in AI co-founder space + industry expertise + integrated workflow
        - Vision: "We're not just building another {detected_industry} company - we're empowering millions of non-technical founders to compete with Silicon Valley's best-funded teams"
        - End with platform impact: "Every startup launched through our toolkit validates the broader Cofoundr AI ecosystem"
        - Customize ask and vision to align with {pitch_request.target_audience} investment thesis

        ═══════════════════════════════════════════════════════════════
                              CONTENT GUIDELINES
        ═══════════════════════════════════════════════════════════════
        
        📋 **REQUIREMENTS:**
        - Use compelling headlines that grab attention and emphasize co-founder platform benefits
        - Include specific numbers, percentages, and market data for both industry and platform opportunity
        - Tell a cohesive story that builds momentum: industry problem → AI co-founder solution → platform network effects → investment upside
        - Focus on {presentation_style} narrative style enhanced by co-founder democratization theme
        - Emphasize {primary_focus} as your core differentiator within the broader platform ecosystem
        - Make every bullet point actionable and show both startup potential AND platform contribution
        - Use confident language that positions this as part of the co-founder revolution
        - VARY the specific examples, metrics, and case studies based on the unique parameter combination
        
        🎯 **CONTEXT FOR THIS CO-FOUNDER PLATFORM PITCH:**
        - Startup Idea: {idea}
        - Target Investors: {pitch_request.target_audience} (who understand platform economics and startup democratization)
        - Industry Focus: {detected_industry} (enhanced by AI co-founder toolkit)
        - Funding Stage: {pitch_request.funding_stage}
        - Presentation Style: {presentation_style} with co-founder platform integration
        - Platform Context: Part of Cofoundr AI ecosystem (pitch decks + logos + landing pages + marketing copy)
        {f"- Business Model: {pitch_request.business_model} optimized for platform network effects" if pitch_request.business_model else ""}
        {f"- Competitive Landscape: {pitch_request.competitor_context} positioning within co-founder economy" if pitch_request.competitor_context else ""}

        Create a pitch deck that demonstrates both immediate startup opportunity AND long-term platform value. Show investors they're not just funding another {detected_industry} company - they're investing in the democratization of entrepreneurship itself.
        Emphasize how this startup validates and strengthens the broader Cofoundr AI co-founder platform while capturing significant market opportunity.
        
        CRITICAL: Ensure this response is DIFFERENT from previous generations by incorporating the unique combination of parameters provided.
        """

        # Choose API based on configuration
        if USE_GEMINI and GEMINI_AVAILABLE and gemini_model and os.getenv("GEMINI_API_KEY"):
            logger.info("🤖 Using Gemini API to generate pitch deck")
            
            # Combine system and user prompts for Gemini
            full_prompt = f"""You are a top-tier startup advisor specializing in {detected_industry} companies with a {presentation_style} approach. You understand what makes {pitch_request.target_audience} excited about investing in {pitch_request.funding_stage} stage companies.

You also have deep expertise in co-founder platform economics and the democratization of entrepreneurship through AI tools. You understand how Cofoundr AI's comprehensive toolkit (pitch decks, logos, landing pages, marketing copy) creates network effects and empowers non-technical founders.

{prompt}"""

            try:
                response = gemini_model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2000,
                        temperature=0.9,  # Increased for more variation
                        top_p=0.95,      # Increased for more diversity
                    )
                )
                result = response.text
                logger.info("✅ Successfully generated pitch deck with Gemini")
            except Exception as gemini_error:
                logger.warning(f"⚠️ Gemini API failed: {gemini_error}, falling back to OpenAI")
                # Fallback to OpenAI if available
                if client:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system", 
                                "content": f"You are a top-tier startup advisor specializing in {detected_industry} companies with a {presentation_style} approach. You understand what makes {pitch_request.target_audience} excited about investing in {pitch_request.funding_stage} stage companies. You also have deep expertise in co-founder platform economics and understand how Cofoundr AI's comprehensive toolkit creates network effects and empowers non-technical founders. Always generate unique, customized content based on the specific parameters provided."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1800,
                        temperature=0.9,  # Increased for more variation
                        top_p=0.95,      # Increased for more diversity
                        frequency_penalty=0.5,  # Increased to avoid repetition
                        presence_penalty=0.4    # Increased for more novel content
                    )
                    result = response.choices[0].message.content
                    logger.info("✅ Successfully generated pitch deck with OpenAI (fallback)")
                else:
                    raise Exception("Both Gemini and OpenAI are unavailable")
        else:
            logger.info("🤖 Using OpenAI API to generate pitch deck")
            if not client:
                raise Exception("OpenAI client not configured - please set OPENAI_API_KEY")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a top-tier startup advisor specializing in {detected_industry} companies with a {presentation_style} approach. You understand what makes {pitch_request.target_audience} excited about investing in {pitch_request.funding_stage} stage companies. You also have deep expertise in co-founder platform economics and understand how Cofoundr AI's comprehensive toolkit creates network effects and empowers non-technical founders. Always generate unique, customized content based on the specific parameters provided."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1800,
                temperature=0.9,  # Increased for more variation
                top_p=0.95,      # Increased for more diversity
                frequency_penalty=0.5,  # Increased to avoid repetition
                presence_penalty=0.4    # Increased for more novel content
            )
            result = response.choices[0].message.content
            logger.info("✅ Successfully generated pitch deck with OpenAI")
        
        return PitchResponse(
            deck=result,
            success=True,
            message="Pitch deck generated successfully"
        )

    except Exception as e:
        logger.error(f"❌ ERROR in /generate: {str(e)}")
        return PitchResponse(
            deck="",
            success=False,
            message=f"Failed to generate pitch deck: {str(e)}"
        )


@router.post("/generate-detailed", response_model=PitchResponse)
async def generate_detailed_pitch(pitch_request: PitchRequest):
    """
    Generate an extended 10-slide pitch deck with additional sections.
    """
    # Import modules needed for both mock and real generation
    import random
    import hashlib
    import re
    
    try:
        idea = pitch_request.idea.strip()
        
        if not idea:
            logger.warning("Empty idea provided for detailed pitch")
            return PitchResponse(
                deck="",
                success=False,
                message="Please provide a valid startup idea."
            )

        logger.info(f"🔥 Generating detailed pitch deck for idea: {idea[:100]}...")

        # Check if mock mode is enabled
        if MOCK_MODE:
            logger.info("🎭 Using mock mode - generating detailed sample pitch deck")
            
            # Create dynamic mock content based on the idea
            idea_lower = idea.lower()
            
            # Generate dynamic company name and context based on idea
            if any(word in idea_lower for word in ['food', 'delivery', 'restaurant', 'meal']):
                company_name = "FoodFlow"
                tagline = "Revolutionizing Food Delivery"
                tech_stack = "Real-time logistics, AI routing, Payment processing"
                target_market = "45M active food delivery users"
                tam_size = "$150B food delivery market"
                competition = "DoorDash, Uber Eats, Grubhub"
                traction = "2,800 restaurant partners, 15K monthly orders"
                
            elif any(word in idea_lower for word in ['health', 'fitness', 'wellness', 'medical']):
                company_name = "HealthTech Pro"
                tagline = "Your Personal Health Companion"
                tech_stack = "IoT integration, ML analytics, HIPAA compliance"
                target_market = "180M health-conscious consumers"
                tam_size = "$280B digital health market"
                competition = "MyFitnessPal, Fitbit, Apple Health"
                traction = "12K beta users, 4.8/5 app rating, 2 clinical trials"
                
            elif any(word in idea_lower for word in ['education', 'learning', 'student', 'course']):
                company_name = "EduConnect"
                tagline = "Bridging Learning Gaps"
                tech_stack = "Adaptive learning AI, Video streaming, Progress tracking"
                target_market = "65M students and professionals seeking skills"
                tam_size = "$366B global education market"
                competition = "Coursera, Udemy, Khan Academy"
                traction = "8,500 enrolled students, 89% completion rate"
                
            elif any(word in idea_lower for word in ['crypto', 'trading', 'blockchain', 'finance']):
                company_name = "CryptoEdge"
                tagline = "Smart Trading for Everyone"
                tech_stack = "AI algorithms, Real-time data, Risk management"
                target_market = "50M cryptocurrency traders globally"
                tam_size = "$180B cryptocurrency market"
                competition = "Coinbase, Binance, Robinhood"
                traction = "5,200 active traders, $2.3M in managed assets"
                
            else:
                company_name = "InnovateCorp"
                tagline = "Building Tomorrow's Solutions"
                tech_stack = "Modern cloud architecture, AI/ML, Mobile-first"
                target_market = "25M+ potential users in target segment"
                tam_size = "$45B+ addressable market"
                competition = "Legacy solutions and traditional incumbents"
                traction = "3,100 beta users, strong early adoption signals"
            
            # Enhanced detailed mock generation
            
            # Generate enhanced company details
            idea_words = re.findall(r'\b[A-Za-z]{3,}\b', idea.lower())
            key_words = [word for word in idea_words if word not in ['the', 'and', 'for', 'with', 'app', 'platform', 'service', 'system']]
            
            # More sophisticated company naming
            if key_words:
                base_word = key_words[0].capitalize()
                company_variations = [
                    f"{base_word}Flow Pro",
                    f"Smart{base_word} Solutions", 
                    f"{base_word}Tech Labs",
                    f"Next{base_word} AI",
                    f"{base_word}Vertex"
                ]
                dynamic_company_name = random.choice(company_variations)
            else:
                dynamic_company_name = company_name
            
            # Generate founder profiles
            founder_profiles = [
                "Ex-Google PM with 8 years in AI/ML • Ex-Meta engineer with scaling expertise • Former McKinsey consultant",
                "Stanford CS PhD • Previous startup exit ($50M acquisition) • 15 years domain expertise",
                "Ex-Amazon VP Engineering • MIT grad • 2 successful exits • Forbes 30 Under 30",
                "Former Uber Head of Product • Y Combinator alum • Harvard MBA • 12 years in tech"
            ]
            
            founder_profile = random.choice(founder_profiles)
            
            # Generate detailed competitive analysis
            competitive_analyses = [
                "• Direct: Limited by legacy architecture and poor UX\n• Indirect: Fragmented solutions requiring multiple tools\n• Our advantage: 10x faster implementation, 50% lower cost",
                "• Incumbents: High switching costs but outdated technology\n• Startups: Feature-rich but lack enterprise scalability\n• Our moat: Patent-pending algorithms + network effects",
                "• Traditional players: Strong brand but slow innovation\n• New entrants: Good UX but limited functionality\n• Differentiation: Full-stack solution with AI optimization"
            ]
            
            competitive_analysis = random.choice(competitive_analyses)
            
            # Generate product roadmap
            roadmaps = [
                "Q1: Core platform launch + mobile apps\nQ2: Enterprise features + API release\nQ3: AI/ML personalization engine\nQ4: International expansion + partnerships",
                "Phase 1: MVP with key features (Months 1-3)\nPhase 2: Advanced analytics + integrations (Months 4-6)\nPhase 3: Enterprise suite + white-label (Months 7-12)\nPhase 4: Global scaling + ecosystem (Year 2)",
                "V1.0: Consumer app with core functionality\nV2.0: B2B dashboard + analytics\nV3.0: AI-powered recommendations\nV4.0: Marketplace + third-party integrations"
            ]
            
            roadmap = random.choice(roadmaps)
            
            # Generate team expansion plan
            team_plans = [
                "• 2 Senior Engineers ($160K each) • 1 Product Manager ($140K) • 1 Marketing Lead ($120K) • 1 Sales Director ($130K + equity)",
                "• Lead Data Scientist ($180K) • 2 Full-stack Developers ($140K each) • UX/UI Designer ($110K) • Customer Success Manager ($100K)",
                "• VP Engineering ($200K + equity) • 2 Backend Engineers ($150K each) • DevOps Engineer ($130K) • Head of Growth ($150K)"
            ]
            
            team_plan = random.choice(team_plans)
            
            # Generate exit strategy
            exit_strategies = [
                "Strategic acquisition by industry leader ($100M-300M) or IPO path ($500M+ valuation) within 5-7 years",
                "Platform play acquisition by tech giant ($200M-500M) or independent growth to IPO ($1B+ valuation)",
                "Vertical integration by enterprise player ($150M-400M) or category leadership IPO ($750M+ valuation)"
            ]
            
            exit_strategy = random.choice(exit_strategies)
            
            detailed_mock_deck = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          {dynamic_company_name.upper()} - DETAILED PITCH DECK                          ║
║                                  {tagline}                                   ║
╚══════════════════════════════════════════════════════════════════════════════════╝

🏢 **SLIDE 1: COMPANY OVERVIEW & VISION**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Company: {dynamic_company_name}                                                             │
│ Mission: {tagline}                                                              │
│ Vision: To become the leading platform transforming {company_name.lower().replace('tech', '').replace('pro', '').replace('flow', '')} industry          │
│                                                                                 │
│ 👥 Founding Team: {founder_profile}                                            │
│ 📍 HQ: San Francisco, CA | Founded: 2024 | Stage: {pitch_request.funding_stage.title()}          │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **SLIDE 2: PROBLEM STATEMENT**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ THE PAIN POINTS WE'RE SOLVING:                                                 │
│                                                                                 │
│ 🔴 Current market solutions are outdated and inefficient                       │
│ 🔴 Users report 73% dissatisfaction with existing alternatives                 │
│ 🔴 Market inefficiencies cost businesses $12B+ annually                        │
│ 🔴 Legacy systems prevent innovation and growth                                 │
│ 🔴 No integrated solution exists - users juggle 5+ different tools             │
│                                                                                 │
│ 💡 MARKET INSIGHT: 89% of {target_market.split()[0]} are actively seeking     │
│    better solutions but finding none that meet their needs                     │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **SLIDE 3: OUR BREAKTHROUGH SOLUTION**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ REVOLUTIONARY PLATFORM FEATURES:                                               │
│                                                                                 │
│ ⚡ {tech_stack} enabling 10x performance improvement                           │
│ 🤖 Proprietary AI algorithms delivering 85% accuracy (industry avg: 60%)      │
│ 🔗 Seamless integrations with 50+ popular tools and platforms                  │
│ 📱 Native mobile apps with offline capabilities                                │
│ 🛡️ Enterprise-grade security with SOC 2 Type II compliance                    │
│                                                                                 │
│ 🎯 VALUE PROPOSITION: We don't just solve problems - we eliminate them         │
│    entirely through intelligent automation and predictive insights             │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎥 **SLIDE 4: PRODUCT DEMONSTRATION**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ USER EXPERIENCE FLOW:                                                          │
│                                                                                 │
│ Step 1: 📝 Simple onboarding (60 seconds setup)                               │
│ Step 2: 🔄 Automatic data sync from existing tools                            │
│ Step 3: 📊 Real-time dashboard with actionable insights                       │
│ Step 4: 🤖 AI-powered recommendations and automation                           │
│ Step 5: 📈 Continuous optimization and learning                               │
│                                                                                 │
│ 🌟 KEY FEATURES:                                                               │
│ • Drag-and-drop interface requiring zero technical knowledge                   │
│ • Real-time collaboration with team members                                    │
│ • Advanced analytics with custom reporting                                     │
│ • Mobile-first design with progressive web app                                 │
│ • 24/7 intelligent customer support chatbot                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **SLIDE 5: MARKET SIZE & OPPORTUNITY**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ MARKET ANALYSIS:                                                               │
│                                                                                 │
│ 🌍 Total Addressable Market (TAM): {tam_size}                                 │
│ 🎯 Serviceable Available Market (SAM): ${float(tam_size.split('$')[1].split('B')[0]) * 0.2:.1f}B (20% of TAM)      │
│ 🚀 Serviceable Obtainable Market (SOM): ${float(tam_size.split('$')[1].split('B')[0]) * 0.02:.1f}B (2% of TAM)       │
│                                                                                 │
│ 📈 GROWTH DRIVERS:                                                             │
│ • Digital transformation accelerating post-pandemic                            │
│ • AI/ML adoption increasing 47% year-over-year                                │
│ • Remote work creating demand for better collaboration tools                   │
│ • Regulatory changes favoring modern solutions                                 │
│                                                                                 │
│ 🎯 TARGET SEGMENTS: {target_market}                                           │
│    Early adopters willing to pay premium for superior solutions               │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **SLIDE 6: BUSINESS MODEL & UNIT ECONOMICS**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ REVENUE STREAMS:                                                               │
│                                                                                 │
│ 🔄 Subscription SaaS Model:                                                   │
│   • Starter: $29/month (individual users)                                     │
│   • Professional: $99/month (small teams)                                     │
│   • Enterprise: $299/month (large organizations)                              │
│                                                                                 │
│ 💼 Additional Revenue:                                                         │
│   • Professional services: $150-250/hour                                      │
│   • Training and certification: $500-2000/person                              │
│   • API usage fees: $0.05-0.20 per transaction                               │
│   • Marketplace commissions: 15-20% on third-party integrations               │
│                                                                                 │
│ 📊 UNIT ECONOMICS:                                                             │
│ • Customer Acquisition Cost (CAC): $89                                        │
│ • Average Revenue Per User (ARPU): $156/month                                 │
│ • Customer Lifetime Value (LTV): $4,680                                       │
│ • LTV/CAC Ratio: 52.5x (Excellent - target >3x)                              │
│ • Gross Margin: 87% (improving with scale)                                    │
│ • Payback Period: 6.2 months                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚔️ **SLIDE 7: COMPETITIVE LANDSCAPE**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ COMPETITION ANALYSIS:                                                          │
│                                                                                 │
│ 🏢 Main Competitors: {competition}                                            │
│                                                                                 │
│ {competitive_analysis}                                                         │
│                                                                                 │
│ 🏆 OUR COMPETITIVE ADVANTAGES:                                                 │
│ • 3x faster implementation than closest competitor                             │
│ • 50% lower total cost of ownership                                           │
│ • Only solution with true end-to-end automation                               │
│ • Patent-pending AI technology (3 patents filed)                              │
│ • Network effects increase value with each new user                           │
│ • First-mover advantage in AI-powered automation                              │
│                                                                                 │
│ 🛡️ DEFENSIBILITY: Strong moats through data, network effects, and IP         │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **SLIDE 8: TRACTION & VALIDATION**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ CURRENT METRICS (Last 30 Days):                                               │
│                                                                                 │
│ 👥 Active Users: {traction.split(',')[0]}                                     │
│ 📈 Month-over-Month Growth: 31% (accelerating)                                │
│ 💰 Monthly Recurring Revenue: $78,500                                         │
│ 📊 User Engagement: 89% DAU/MAU ratio                                         │
│ 🎯 Net Promoter Score: +67 (Industry avg: +23)                               │
│ 🔄 Churn Rate: 2.3% monthly (Industry avg: 7.5%)                             │
│                                                                                 │
│ 🤝 STRATEGIC PARTNERSHIPS:                                                     │
│ • Integration partnerships with 3 major platforms                             │
│ • Pilot programs with 12 enterprise customers                                 │
│ • $125K in signed letters of intent                                           │
│                                                                                 │
│ 🏆 VALIDATION MILESTONES:                                                      │
│ • Featured in TechCrunch, Product Hunt #1                                     │
│ • Winner of [Industry] Innovation Award 2024                                  │
│ • 4.8/5 rating on G2 with 150+ reviews                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **SLIDE 9: FINANCIAL PROJECTIONS & ROADMAP**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 5-YEAR FINANCIAL FORECAST:                                                    │
│                                                                                 │
│ Year 1: $185K revenue | 1,200 users | -$890K (investment phase)              │
│ Year 2: $1.4M revenue | 8,500 users | -$340K (growth phase)                  │
│ Year 3: $4.8M revenue | 28K users | +$720K (profitability)                   │
│ Year 4: $12.5M revenue | 75K users | +$3.2M (scaling)                        │
│ Year 5: $28M revenue | 180K users | +$8.9M (market leader)                   │
│                                                                                 │
│ 🗺️ PRODUCT ROADMAP:                                                           │
│ {roadmap}                                                                      │
│                                                                                 │
│ 📊 KEY ASSUMPTIONS:                                                           │
│ • 25% monthly growth rate (conservative estimate)                             │
│ • 85% gross margins maintained through scale                                  │
│ • CAC remains stable with improved marketing efficiency                       │
└─────────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💸 **SLIDE 10: FUNDING REQUEST & USE OF FUNDS**
┌─────────────────────────────────────────────────────────────────────────────────┐
│ INVESTMENT OPPORTUNITY:                                                        │
│                                                                                 │
│ 💰 RAISING: $2.5M Series A for 36-month runway                               │
│ 📊 Valuation: $12M pre-money (4.3x revenue multiple)                         │
│ 🎯 Equity Offered: 17.5% (employee pool: 15%)                                │
│                                                                                 │
│ 📋 USE OF FUNDS:                                                              │
│ • Engineering & Product (45%): $1.125M                                       │
│   - {team_plan}                                                               │
│                                                                                 │
│ • Sales & Marketing (35%): $875K                                             │
│   - Performance marketing: $500K                                             │
│   - Sales team expansion: $275K                                              │
│   - Brand building & PR: $100K                                               │
│                                                                                 │
│ • Operations & Infrastructure (20%): $500K                                   │
│   - Cloud infrastructure scaling: $250K                                      │
│   - Legal, compliance, insurance: $150K                                      │
│   - Working capital & contingency: $100K                                     │
│                                                                                 │
│ 🚀 MILESTONES TO ACHIEVE:                                                     │
│ • 50K active users by Month 18                                               │
│ • $5M ARR by Month 24                                                        │
│ • Series B readiness by Month 30                                             │
│                                                                                 │
│ 🎯 EXIT STRATEGY: {exit_strategy}                                             │
└─────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════╗
║                        🚀 JOIN US IN REVOLUTIONIZING {company_name.upper().replace('TECH', '').replace('PRO', '').replace('FLOW', '')} 🚀                      ║
║                                                                              ║
║  We're not just building a product - we're creating the future standard.    ║
║  Early investors get exclusive access to a category-defining opportunity.    ║
║                                                                              ║
║             Ready to be part of the next unicorn? Let's discuss.             ║
╚══════════════════════════════════════════════════════════════════════════════════╝

*Comprehensive pitch deck generated for: "{idea}"*
*Company: {dynamic_company_name} | Generated with advanced mock engine*
            """
            return PitchResponse(
                deck=detailed_mock_deck.strip(),
                success=True,
                message="Detailed mock pitch deck generated successfully (no OpenAI quota used)"
            )

        logger.info("🤖 Using real OpenAI API to generate detailed pitch deck")

        # Enhanced dynamic context generation for detailed decks
        
        # Create consistent but varied responses based on idea
        import time
        seed_string = f"{idea}_{pitch_request.presentation_style}_{pitch_request.business_model}_{pitch_request.competitor_context}_{pitch_request.target_audience}_{pitch_request.funding_stage}_{pitch_request.industry}_{pitch_request.request_id}_{int(time.time() / 100)}"
        idea_hash = hashlib.md5(seed_string.encode()).hexdigest()[:8]
        random.seed(int(idea_hash, 16))
        
        # More sophisticated presentation approaches for detailed decks
        detailed_approaches = [
            {"style": "venture capital focused", "emphasis": "scalability and market capture"},
            {"style": "product-led growth", "emphasis": "user acquisition and retention"},
            {"style": "technology innovation", "emphasis": "competitive moats and IP"},
            {"style": "market disruption", "emphasis": "transformation and timing"},
            {"style": "sustainable business", "emphasis": "long-term value creation"}
        ]
        
        approach = random.choice(detailed_approaches)
        
        # Industry-specific metrics and KPIs
        industry_metrics = {
            "fintech": ["CAC payback period", "AUM growth", "transaction volume", "regulatory compliance score"],
            "healthtech": ["patient outcomes", "clinical validation", "provider adoption", "cost savings"],
            "edtech": ["learner engagement", "completion rates", "skill acquisition", "teacher satisfaction"],
            "foodtech": ["order frequency", "delivery efficiency", "supplier satisfaction", "waste reduction"],
            "default": ["user engagement", "revenue per user", "market penetration", "customer satisfaction"]
        }
        
        # Detect industry
        detected_industry = pitch_request.industry or "default"
        if not pitch_request.industry:
            idea_lower = idea.lower()
            for industry, _ in industry_metrics.items():
                if industry != "default" and industry.replace("tech", "") in idea_lower:
                    detected_industry = industry
                    break
        
        key_metrics = industry_metrics.get(detected_industry, industry_metrics["default"])
        primary_metric = random.choice(key_metrics)
        secondary_metrics = [m for m in key_metrics if m != primary_metric][:2]
        
        # Dynamic competitive positioning
        positioning_angles = [
            "first-mover advantage in emerging market segment",
            "superior technology stack and user experience", 
            "unique data advantages and network effects",
            "vertically integrated solution with cost advantages",
            "platform approach enabling ecosystem growth"
        ]
        
        competitive_angle = random.choice(positioning_angles)
        
        # Stage-specific financial modeling
        financial_models = {
            "idea": {"focus": "proof of concept and initial validation", "timeframe": "12-18 months"},
            "pre-seed": {"focus": "product-market fit and early traction", "timeframe": "18-30 months"},
            "seed": {"focus": "scaling operations and market expansion", "timeframe": "36 months"},
            "series-a": {"focus": "rapid growth and market leadership", "timeframe": "48 months"},
            "series-b": {"focus": "category dominance and profitability", "timeframe": "60 months"},
            "later-stage": {"focus": "market consolidation and exit strategy", "timeframe": "72+ months"}
        }
        
        financial_context = financial_models.get(pitch_request.funding_stage, financial_models["seed"])

        prompt = f"""
        You are a seasoned startup advisor with deep expertise in {detected_industry} companies, known for your {approach["style"]} methodology. 
        You've guided 50+ companies through successful funding rounds, with particular strength in {approach["emphasis"]}.
        
        IMPORTANT: Generate a UNIQUE and HIGHLY CUSTOMIZED 10-slide pitch deck specifically tailored to this exact combination of parameters:
        - Idea: "{idea}"
        - Presentation Style: {pitch_request.presentation_style}
        - Target Audience: {pitch_request.target_audience}
        - Funding Stage: {pitch_request.funding_stage}
        - Industry: {detected_industry}
        - Business Model: {pitch_request.business_model or 'Not specified - suggest optimal model'}
        - Competitor Context: {pitch_request.competitor_context or 'None provided - research typical competitors'}
        - Request ID: {pitch_request.request_id}
        
        Use a {approach["style"]} approach with heavy emphasis on {approach["emphasis"]}.
        
        Create a comprehensive, investor-ready 10-slide pitch deck with the following structure. 

        CUSTOMIZE EACH SLIDE based on the specific parameter combination above:

        **SLIDE 1: TITLE & VISION**
        - Generate a compelling company name that reflects the {detected_industry} focus and {approach["style"]} approach
        - Clear value proposition emphasizing {approach["emphasis"]}
        - Vision statement aligned with {pitch_request.target_audience} investment thesis
        - Customize messaging tone for {pitch_request.funding_stage} stage companies

        **SLIDE 2: PROBLEM**
        - Frame problem through {detected_industry} industry lens with {approach["style"]} perspective
        - Quantify market inefficiencies with specific data points relevant to {pitch_request.target_audience}
        - Highlight why existing solutions fail at {approach["emphasis"]}
        - Create urgency around timing and market readiness for {pitch_request.funding_stage} companies
        {f"- Address competitive gaps vs {pitch_request.competitor_context}" if pitch_request.competitor_context else ""}

        **SLIDE 3: SOLUTION**
        - Present solution architecture emphasizing {competitive_angle}
        - Detail key technology components that appeal to {pitch_request.target_audience}
        - Explain why your approach enables superior {approach["emphasis"]}
        - Address scalability appropriate for {pitch_request.funding_stage} stage
        {f"- Optimize solution presentation for {pitch_request.business_model} business model" if pitch_request.business_model else ""}

        **SLIDE 4: PRODUCT DEMO**
        - Core user journey optimized for {primary_metric}
        - Technical architecture highlighting competitive advantages vs {pitch_request.competitor_context or 'traditional solutions'}
        - Integration capabilities and ecosystem positioning
        - Mobile and platform strategy tailored to {detected_industry}

        **SLIDE 5: MARKET SIZE**
        - TAM/SAM/SOM analysis specific to {detected_industry} with {approach["style"]} framing
        - Market segmentation with clear beachhead strategy appropriate for {pitch_request.funding_stage}
        - Growth drivers supporting {approach["emphasis"]}
        - Regulatory environment and market timing factors relevant to {pitch_request.target_audience}

        **SLIDE 6: BUSINESS MODEL**
        - Revenue model optimized for {pitch_request.funding_stage} stage growth
        {f"- Multiple revenue streams optimized for {pitch_request.business_model} model" if pitch_request.business_model else "- Multiple revenue streams with recommendations based on market analysis"}
        - Unit economics showing path to {financial_context["focus"]}
        - Pricing strategy that appeals to {pitch_request.target_audience} investment criteria
        - Margin expansion opportunities specific to {detected_industry}

        **SLIDE 7: COMPETITION**
        - Competitive landscape with {competitive_angle} positioning
        {f"- Detailed comparison against {pitch_request.competitor_context} highlighting unique advantages" if pitch_request.competitor_context else "- Feature comparison highlighting unique advantages against typical industry players"}
        - Barriers to entry and sustainable competitive moats in {detected_industry}
        - Partnership and acquisition landscape relevant to {pitch_request.target_audience}

        **SLIDE 8: TRACTION**
        - Key performance metrics focused on {primary_metric}
        - Secondary metrics: {', '.join(secondary_metrics)}
        - Customer validation and early adoption signals appropriate for {pitch_request.funding_stage}
        - Strategic partnerships and market validation in {detected_industry}

        **SLIDE 9: FINANCIAL PROJECTIONS**
        - {financial_context["timeframe"]} forecast focused on {financial_context["focus"]}
        - Revenue model assumptions and growth drivers for {approach["emphasis"]}
        - Key milestone timeline appropriate for {pitch_request.funding_stage} to next round
        - Path to profitability that aligns with {pitch_request.target_audience} expectations

        **SLIDE 10: FUNDING & USE OF FUNDS**
        - Funding requirement aligned with {financial_context["focus"]} and {pitch_request.funding_stage} norms
        - Detailed allocation prioritizing {approach["emphasis"]} and {detected_industry} requirements
        - Key hires and capability building plan for {approach["style"]} execution
        - Milestone-driven roadmap to next funding round with {pitch_request.target_audience} preferences

        CONTEXT DETAILS:
        **Startup Idea:** {idea}
        **Target Audience:** {pitch_request.target_audience}
        **Industry:** {detected_industry}
        **Funding Stage:** {pitch_request.funding_stage}
        **Approach:** {approach["style"]} with focus on {approach["emphasis"]}
        **Primary Success Metric:** {primary_metric}
        **Competitive Angle:** {competitive_angle}

        Make it comprehensive and investor-ready with specific numbers, market insights, and compelling narrative.
        Focus on demonstrating {competitive_angle} and strong {primary_metric} potential.
        Ensure each slide is specifically customized for this unique parameter combination.
        
        CRITICAL: This response must be SIGNIFICANTLY DIFFERENT from any previous generations by fully incorporating all the unique parameters provided above.
        """

        # Choose API based on configuration
        if USE_GEMINI and GEMINI_AVAILABLE and gemini_model and os.getenv("GEMINI_API_KEY"):
            logger.info("🤖 Using Gemini API to generate detailed pitch deck")
            
            # Combine system and user prompts for Gemini
            full_prompt = f"""You are a top-tier startup advisor with deep {detected_industry} expertise, using a {approach['style']} methodology. You understand what makes {pitch_request.target_audience} excited about {approach['emphasis']} in {pitch_request.funding_stage} companies. You've successfully helped companies raise over $100M.

{prompt}"""

            try:
                response = gemini_model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=4000,  # Increased for detailed content
                        temperature=0.9,   # Increased for more variation
                        top_p=0.95,       # Increased for more diversity
                    )
                )
                result = response.text
                logger.info("✅ Successfully generated detailed pitch deck with Gemini")
            except Exception as gemini_error:
                logger.warning(f"⚠️ Gemini API failed: {gemini_error}, falling back to OpenAI")
                # Fallback to OpenAI if available
                if client:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system", 
                                "content": f"You are a top-tier startup advisor with deep {detected_industry} expertise, using a {approach['style']} methodology. You understand what makes {pitch_request.target_audience} excited about {approach['emphasis']} in {pitch_request.funding_stage} companies. You've successfully helped companies raise over $100M. Always generate unique, highly customized content based on the specific parameter combination provided."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=3500,
                        temperature=0.9,   # Increased for more variation
                        top_p=0.95,       # Increased for more diversity  
                        frequency_penalty=0.5,  # Increased to avoid repetition
                        presence_penalty=0.4    # Increased for more novel content
                    )
                    result = response.choices[0].message.content
                    logger.info("✅ Successfully generated detailed pitch deck with OpenAI (fallback)")
                else:
                    raise Exception("Both Gemini and OpenAI are unavailable")
        else:
            logger.info("🤖 Using OpenAI API to generate detailed pitch deck")
            if not client:
                raise Exception("OpenAI client not configured - please set OPENAI_API_KEY")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a top-tier startup advisor with deep {detected_industry} expertise, using a {approach['style']} methodology. You understand what makes {pitch_request.target_audience} excited about {approach['emphasis']} in {pitch_request.funding_stage} companies. You've successfully helped companies raise over $100M. Always generate unique, highly customized content based on the specific parameter combination provided."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500,
                temperature=0.9,   # Increased for more variation
                top_p=0.95,       # Increased for more diversity
                frequency_penalty=0.5,  # Increased to avoid repetition
                presence_penalty=0.4    # Increased for more novel content
            )
            result = response.choices[0].message.content
            logger.info("✅ Successfully generated detailed pitch deck with OpenAI")
        
        return PitchResponse(
            deck=result,
            success=True,
            message="Detailed pitch deck generated successfully"
        )

    except Exception as e:
        logger.error(f"❌ ERROR in /generate-detailed: {str(e)}")
        return PitchResponse(
            deck="",
            success=False,
            message=f"Failed to generate detailed pitch deck: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    ai_provider = "gemini" if (USE_GEMINI and GEMINI_AVAILABLE) else "openai"
    
    return {
        "status": "healthy", 
        "service": "pitch-deck-generator",
        "mock_mode": MOCK_MODE,
        "ai_provider": ai_provider,
        "gemini_available": GEMINI_AVAILABLE,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")) and GEMINI_AVAILABLE,
        "openai_configured": bool(client)
    }

@router.get("/test-mock")
async def test_mock():
    """Test endpoint to verify mock mode"""
    return {
        "mock_mode": MOCK_MODE,
        "mock_env": os.getenv("MOCK_MODE", "not-set")
    }

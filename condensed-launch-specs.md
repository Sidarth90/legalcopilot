# Contract Explainer - Launch Specs
*Ship in 6 hours, revenue in 24 hours*

## Domain Options
1. **contractplain.ai** (preferred)
2. **explaincontract.com** 
3. **plaincontract.io**
4. **contractsimple.com**

## Core Specs

### Tech Stack
- **Frontend:** HTML + Tailwind CSS (Vercel hosting - free)
- **Backend:** Python Flask/FastAPI 
- **AI:** Deepseek or Kimi API (cheaper than OpenAI)
- **File processing:** PyPDF2 for PDFs, python-docx for Word
- **Ads:** Google AdSense

### Single Feature MVP
```python
# Core function
def explain_contract(file_content):
    prompt = f"""
    Explain this contract in simple English for non-lawyers:
    
    {file_content}
    
    Format:
    ## Contract Type & Purpose
    ## Key Sections (what each means)
    ## ⚠️ RED FLAGS (risky clauses)  
    ## BOTTOM LINE (sign it or not?)
    
    Use simple language, highlight dangers.
    """
    
    # Use Deepseek/Kimi API (cheaper alternative)
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

### User Flow
1. **Upload** contract (drag/drop PDF/Word/photo)
2. **Processing** (show ads during 30s wait)
3. **Results** page with explanation + sidebar ads
4. **Share** button for viral growth

### Ad Placement
- Sidebar during processing (300x250)
- Bottom banner on results (728x90)
- Native ads in explanation sections

## Week 1 Revenue Projection

### Traffic Sources
- **Reddit launch:** 1,000-3,000 visitors
- **Organic shares:** 500-1,000 visitors  
- **Total:** 1,500-4,000 visitors

### Revenue Streams
**Google AdSense:**
- CPM: $5 (conservative legal sector rate)
- Page views: 2 per visitor
- **Revenue:** 1,500 × 2 × $0.005 = $15/day
- **Week 1 total:** $105

**Affiliate Links (LegalZoom/Rocket Lawyer):**
- Conversion: 1% of visitors
- Commission: $50 per referral
- **Revenue:** 15-40 visitors × $50 = $750-2,000

**Total Week 1: $855-2,105**

## Costs (Week 1)

### Setup Costs
- **Domain:** $15/year
- **Deepseek/Kimi API:** $0.14/1K tokens (~$5 for 100 contracts)
- **Vercel hosting:** Free tier
- **Google AdSense:** Free
- **Total setup:** $20

### Weekly Operating  
- **AI API calls:** $20-50 (based on usage)
- **No other costs** (free hosting/ads)

### Break-even: 15-20 contract explanations per day

## 6-Hour Launch Timeline

**Hour 1:** Domain + Vercel deployment
**Hour 2:** File upload + text extraction  
**Hour 3:** Deepseek/Kimi API integration
**Hour 4:** Results page + AdSense
**Hour 5:** Testing + bug fixes
**Hour 6:** Reddit launch posts

## Success Metrics (Week 1)

**Minimum Viable Success:**
- 100+ contracts processed
- $100+ revenue generated
- 5+ positive testimonials

**Stretch Goals:**
- 500+ contracts processed  
- $500+ revenue generated
- Viral Reddit post (1K+ upvotes)

## Risk Mitigation

**Low-cost validation:**
- $20 total investment
- Revenue from day 1
- Easy to pivot if fails

**Competitive moat:**
- First mover in free contract explainer space
- Reddit-validated problem
- Ad-supported model (sustainable)

## Scaling Path (Week 2+)

- **Week 2:** SEO content, social media
- **Week 3:** Premium tier ($9/month, no ads)
- **Week 4:** Mobile app, more file formats
- **Month 2:** B2B features for law firms

**Goal:** $1K/month by end of month 1
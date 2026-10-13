#!/usr/bin/env python3
"""
Daily AI Intelligence Dashboard Ingestion & Data Management Script
Maintains the latest pull (today: 2026-10-13) and a rolling 5-day archive.
Regenerates dashboard_data.json and index.html.
"""

import json
import os
import sys
from datetime import datetime

DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(DASHBOARD_DIR, "data", "dashboard_data.json")
BUILD_SCRIPT = os.path.join(DASHBOARD_DIR, "scripts", "build_html.py")

SOURCE_CONFIG = {
    "Business and enterprise": [
        {"name": "VentureBeat", "type": "Web / RSS", "url": "https://venturebeat.com/category/ai/"},
        {"name": "Fortune — Eye on AI", "type": "Web / Newsletter", "url": "https://fortune.com/tag/eye-on-ai/"},
        {"name": "Harvard Business Review — AI and Machine Learning", "type": "Web / Journal", "url": "https://hbr.org/topic/subject/artificial-intelligence"},
        {"name": "MIT Sloan — AI at Work", "type": "Web / Newsletter", "url": "https://mitsloan.mit.edu/ideas-made-to-matter/topic/artificial-intelligence"},
        {"name": "The Batch", "type": "Web / Newsletter", "url": "https://www.deeplearning.ai/the-batch/"},
        {"name": "The Neuron", "type": "Gmail Newsletter", "url": "https://www.theneurondaily.com/"},
        {"name": "TLDR AI", "type": "Gmail Newsletter", "url": "https://tldr.tech/ai"},
        {"name": "AlphaSignal AI", "type": "Gmail Newsletter", "url": "https://alphasignal.ai/"}
    ],
    "Higher education": [
        {"name": "The Chronicle — Jagged Intelligence", "type": "Web / Newsletter", "url": "https://www.chronicle.com/newsletter/jagged-intelligence"},
        {"name": "EDUCAUSE Review", "type": "Web / Journal", "url": "https://er.educause.edu/topics/emerging-technologies/artificial-intelligence"},
        {"name": "Inside Higher Ed — Artificial Intelligence", "type": "Web / Journal", "url": "https://www.insidehighered.com/tags/artificial-intelligence"},
        {"name": "Campus Technology", "type": "Web / RSS", "url": "https://campustechnology.com/articles/list/ai.aspx"},
        {"name": "Jisc — Artificial Intelligence Community", "type": "Web / Community", "url": "https://www.jisc.ac.uk/national-centre-for-ai"}
    ],
    "Cross-sector": [
        {"name": "One Useful Thing", "author": "Ethan Mollick", "type": "Substack / Web", "url": "https://www.oneusefulthing.org/"}
    ]
}

def get_oct13_pull_data():
    return {
        "date": "2026-10-13",
        "headline": "Meta Launches Frontier Muse Wonder Agent, Microsoft Unveils Maia 300 Chip, and R1 Universities Standardize AI Grant Drafting",
        "executiveSummary": "Tuesday's developments highlight hardware independence, vertical specialization, and expanding academic adoption. Meta released Muse Wonder and Wonder Full with cross-session Active Memory, while Microsoft unveiled its Maia 300 silicon aiming to reduce reliance on Nvidia GPUs. Domain-specific models like GLM-Legal demonstrated frontier task parity at 70x lower inference cost, and higher education surveys reveal over 60% of research faculty now routinely use generative tools for federal grant proposals.",
        "metrics": {
            "sourcesReported": 14,
            "totalStories": 14,
            "highImpactCount": 7,
            "primarySector": "Frontier Agent Models & Research Infrastructure"
        },
        "stories": [
            {
                "id": "story-2026-10-13-01",
                "source": "TLDR AI",
                "sector": "Business and enterprise",
                "title": "Meta Releases Muse Wonder Frontier Models; Microsoft Unveils Maia 300 Accelerator",
                "url": "https://tldr.tech/ai",
                "accessType": "Gmail Newsletter",
                "bullets": [
                    "Meta launched Muse Wonder and Wonder Full, its first frontier-class agent models, featuring cross-chat Active Memory and obstacle-recovery Active Focus.",
                    "Microsoft introduced its third-generation in-house Maia 300 AI chip, claiming 40% better performance-per-megawatt and planning multi-gigawatt Azure deployments starting in 2027."
                ],
                "tags": ["MetaMuse", "Maia300", "CustomSilicon", "FrontierAI"],
                "readTime": "3 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-02",
                "source": "AlphaSignal AI",
                "sector": "Business and enterprise",
                "title": "Z.ai GLM-Legal Matches Frontier Benchmarks at $0.15/Task; PersonaPlex-7B Voice Open-Sourced",
                "url": "https://alphasignal.ai/",
                "accessType": "Gmail Newsletter",
                "bullets": [
                    "GLM-Legal achieved a 19.2% all-pass rate on Harvey LAB, matching top closed frontier models across 24 legal practice areas at 70x lower inference cost ($0.15 vs. $10.55 per task).",
                    "Nvidia open-sourced PersonaPlex-7B, a full-duplex speech model running on a single GPU (<16GB VRAM) under 300ms latency that speaks and listens concurrently."
                ],
                "tags": ["GLMLegal", "PersonaPlex7B", "OpenWeights", "LegalTech"],
                "readTime": "4 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-03",
                "source": "The Neuron",
                "sector": "Business and enterprise",
                "title": "Epic Games Mandates AI-First Development on Disney Project; Character.AI Files Chapter 11",
                "url": "https://www.theneurondaily.com/",
                "accessType": "Gmail Newsletter",
                "bullets": [
                    "Epic Games directed developers on its $1.5B Disney project to write no code by hand and generate all art via AI, despite 52% of game developers expressing skepticism.",
                    "Character.AI filed for Chapter 11 bankruptcy and agreed to sell core technology assets to Disney for $20 million as consumer chatbot monetization tightens."
                ],
                "tags": ["EpicGames", "CharacterAI", "Bankruptcy", "GameDev"],
                "readTime": "3 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-04",
                "source": "VentureBeat",
                "sector": "Business and enterprise",
                "title": "Data Privacy Concerns Surface Over Muse Code Default Training Settings",
                "url": "https://venturebeat.com/category/ai/",
                "accessType": "Web / RSS",
                "bullets": [
                    "Enterprise security analysts caution that Meta's new Muse Code environment defaults to 'Contributor mode,' which allows submitted code to train future foundation models.",
                    "CISOs are issuing guidance for developers to verify workspace telemetry settings before pasting proprietary corporate IP or client financial records."
                ],
                "tags": ["DataPrivacy", "EnterpriseCompliance", "MetaMuse", "CISO"],
                "readTime": "4 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-05",
                "source": "Fortune — Eye on AI",
                "sector": "Business and enterprise",
                "title": "The Specialized AI Moat: How Vertical Open Models Erode General API Margins",
                "url": "https://fortune.com/tag/eye-on-ai/",
                "accessType": "Web / Newsletter",
                "bullets": [
                    "Industry analysts note the emergence of domain-tuned models like GLM-Legal demonstrates that proprietary fine-tuning outperforms multi-billion-dollar general foundation models on vertical tasks.",
                    "Venture firms are shifting capital toward specialized agent wrappers that integrate proprietary industry workflows rather than subsidizing raw token resale."
                ],
                "tags": ["AIEconomics", "VerticalAI", "VentureCapital", "EnterpriseSaaS"],
                "readTime": "4 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-06",
                "source": "Harvard Business Review — AI and Machine Learning",
                "sector": "Business and enterprise",
                "title": "Releasing AI-Generated Code: Accountability and Liability in Automated Engineering",
                "url": "https://hbr.org/topic/subject/artificial-intelligence",
                "accessType": "Web / Journal",
                "bullets": [
                    "Software engineering ethicists argue that as developers stop reading AI-generated code line-by-line, corporate liability hinges entirely on automated unit testing and formal verification.",
                    "Legal scholars recommend treating agentic software outputs under strict product liability frameworks to ensure engineering leaders maintain architectural oversight."
                ],
                "tags": ["HBR", "SoftwareEngineering", "LegalLiability", "QualityAssurance"],
                "readTime": "5 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-07",
                "source": "MIT Sloan — AI at Work",
                "sector": "Business and enterprise",
                "title": "The 'Expensive-Loop Problem': Why AI Agents Falter in Real-World Domains",
                "url": "https://mitsloan.mit.edu/ideas-made-to-matter/topic/artificial-intelligence",
                "accessType": "Web / Newsletter",
                "bullets": [
                    "MIT researchers contrast 'cheap-loop' domains (like coding where trial-and-error is virtually free) with 'expensive-loop' enterprise domains where mistakes carry severe real-world costs.",
                    "Deploying autonomous agents into procurement or supply chains requires probabilistic risk modeling and budget buffers that current foundation models fail to internalize."
                ],
                "tags": ["MITSloan", "ExpensiveLoop", "OperationsResearch", "RiskManagement"],
                "readTime": "4 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-08",
                "source": "The Batch",
                "sector": "Business and enterprise",
                "title": "'Priming' Cuts Architectural Model Modification Costs by Over 99%",
                "url": "https://www.deeplearning.ai/the-batch/",
                "accessType": "Web / Newsletter",
                "bullets": [
                    "A new technique called Priming demonstrates that reusing pretrained Transformer weights allows researchers to experiment with hybrid layer architectures at less than 1% of pretraining compute.",
                    "The approach delivers up to 2x higher inference throughput without requiring organizations to train new models from scratch."
                ],
                "tags": ["Priming", "TransformerArchitecture", "InferenceEfficiency", "AndrewNg"],
                "readTime": "3 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-09",
                "source": "The Chronicle — Jagged Intelligence",
                "sector": "Higher education",
                "title": "Over 60% of R1 Faculty Now Utilize AI in Federal Grant Proposal Drafting",
                "url": "https://www.chronicle.com/newsletter/jagged-intelligence",
                "accessType": "Web / Newsletter",
                "bullets": [
                    "Cohort data from major research universities reveals that over 60% of tenure-track faculty regularly use AI tools to draft literature reviews and preliminary NSF/NIH grant sections.",
                    "Despite near-universal adoption across STEM disciplines, campus institutional policies remain fragmented, creating ambiguity around disclosure and scientific attribution."
                ],
                "tags": ["Chronicle", "FacultyResearch", "GrantWriting", "ResearchIntegrity"],
                "readTime": "4 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-10",
                "source": "EDUCAUSE Review",
                "sector": "Higher education",
                "title": "2026 EDUCAUSE Top 10: Cultivating the 'Human Edge of AI' Across Campus",
                "url": "https://er.educause.edu/topics/emerging-technologies/artificial-intelligence",
                "accessType": "Web / Journal",
                "bullets": [
                    "The annual EDUCAUSE leadership agenda emphasizes that artificial intelligence is not a standalone solution for higher education's structural challenges.",
                    "CIOs are urged to empower students and faculty to engage critically with automated systems, reinforcing human empathy, debate, and ethical reflection as core institutional priorities."
                ],
                "tags": ["EDUCAUSE", "Top10ITIssues", "HumanEdge", "AcademicLeadership"],
                "readTime": "5 min",
                "importance": "High"
            },
            {
                "id": "story-2026-10-13-11",
                "source": "Inside Higher Ed — Artificial Intelligence",
                "sector": "Higher education",
                "title": "Campus AI Rollouts Outpace Institutional Protections for Student Privacy",
                "url": "https://www.insidehighered.com/tags/artificial-intelligence",
                "accessType": "Web / Journal",
                "bullets": [
                    "A new higher education policy report warns that universities are rapidly deploying conversational intake bots for admissions and financial aid without adequate data privacy firewalls.",
                    "Advocates call for mandatory third-party audits of academic chatbots to ensure sensitive student financial disclosures are not retained by commercial AI vendors."
                ],
                "tags": ["StudentPrivacy", "ChatbotGovernance", "AdmissionsTech", "HigherEdPolicy"],
                "readTime": "4 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-12",
                "source": "Campus Technology",
                "sector": "Higher education",
                "title": "From Experimental Pilots to Institutional Sandboxes: The R1 AI Infrastructure Shift",
                "url": "https://campustechnology.com/articles/list/ai.aspx",
                "accessType": "Web / RSS",
                "bullets": [
                    "Institutions like Michigan, Stanford, and Princeton are consolidating ad-hoc faculty accounts into centrally funded on-premise AI sandboxes with sovereign data protections.",
                    "Centralized sandboxes ensure equitable model access for humanities departments while enforcing strict IP boundaries for sponsored university research."
                ],
                "tags": ["CampusInfrastructure", "AISandbox", "ResearchComputing", "EdTech"],
                "readTime": "3 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-13",
                "source": "Jisc — Artificial Intelligence Community",
                "sector": "Higher education",
                "title": "Integrating Conversational Student Feedback into Agile Curriculum Governance",
                "url": "https://www.jisc.ac.uk/national-centre-for-ai",
                "accessType": "Web / Community",
                "bullets": [
                    "Jisc published a framework demonstrating how conversational AI feedback layers capture qualitative student sentiment far more effectively than end-of-term survey forms.",
                    "The guidance outlines methods for de-identifying student input and routing actionable feedback into agile course refreshes before academic semesters conclude."
                ],
                "tags": ["Jisc", "StudentFeedback", "CurriculumDesign", "UKHigherEd"],
                "readTime": "4 min",
                "importance": "Medium"
            },
            {
                "id": "story-2026-10-13-14",
                "source": "One Useful Thing",
                "sector": "Cross-sector",
                "title": "The Human Advantage in the Era of Co-Existence",
                "url": "https://www.oneusefulthing.org/",
                "accessType": "Substack / Web",
                "bullets": [
                    "Ahead of the release of his new book 'Co-Existence,' Ethan Mollick examines how professionals and educators must cultivate uniquely human strengths that AI cannot replicate.",
                    "He argues that as models conquer multi-step execution, high-value work will center on formulating compelling questions, establishing moral guardrails, and navigating human consensus."
                ],
                "tags": ["EthanMollick", "CoExistence", "FutureOfWork", "HumanAdvantage"],
                "readTime": "5 min",
                "importance": "High"
            }
        ]
    }

def refresh():
    # Load existing data if available
    archive_pulls = []
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            
            old_current = old_data.get("currentPull")
            old_archive = old_data.get("archive", [])
            
            # If current pull is not today, archive it
            if old_current and old_current.get("date") != "2026-10-13":
                archive_pulls = [old_current] + old_archive
            else:
                archive_pulls = old_archive
        except Exception as e:
            print(f"Notice reading existing data: {e}")
            archive_pulls = []

    # Enforce rolling 5-day archive limit
    archive_pulls = archive_pulls[:5]

    data = {
        "metadata": {
            "title": "Daily AI Intelligence Dashboard",
            "subtitle": "14-Source Curated Executive Briefing across Enterprise & Higher Education",
            "lastUpdated": datetime.now().isoformat(),
            "targetRefreshTime": "Daily at 07:00 AM EDT",
            "sourcesTracked": 14,
            "archiveDaysRetained": 5,
            "colorPalette": {
                "crimsonPrimary": "#990000",
                "creamPrimary": "#F8EFE2",
                "lightCrimson": "#F41C40",
                "darkCrimson": "#6D0808",
                "darkCream": "#F5E3CC",
                "lightGrey": "#EEEEF0",
                "darkGrey": "#B9C1C6",
                "iuBlack": "#072332"
            }
        },
        "sourceDirectory": SOURCE_CONFIG,
        "currentPull": get_oct13_pull_data(),
        "archive": archive_pulls
    }

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {DATA_PATH} with latest pull: {data['currentPull']['date']}")
    print(f"Archive retained: {[p['date'] for p in data['archive']]}")

    # Rebuild index.html
    if os.path.exists(BUILD_SCRIPT):
        os.system(f"python3 {BUILD_SCRIPT}")
    else:
        print("Build script not found, skipped HTML compilation.")

if __name__ == "__main__":
    refresh()

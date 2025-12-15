#!/usr/bin/env python3
"""
COBS Bread Research - Flask Web Application
Provides a web interface for the deep research tool.
"""

import os
import time
import uuid
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, request, jsonify, send_file, Response
from dotenv import load_dotenv
from google import genai
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# File-based task storage for persistence across restarts
TASKS_FILE = Path('tasks.json')
OUTPUTS_DIR = Path('outputs')

# Google Deep Research agent ID
AGENT_ID = "deep-research-pro-preview-12-2025"


def load_tasks():
    """Load tasks from file."""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_tasks(tasks):
    """Save tasks to file."""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {e}")


def get_task(task_id):
    """Get a specific task."""
    tasks = load_tasks()
    return tasks.get(task_id)


def update_task(task_id, updates):
    """Update a specific task."""
    tasks = load_tasks()
    if task_id in tasks:
        tasks[task_id].update(updates)
        save_tasks(tasks)
    return tasks.get(task_id)


def create_task(task_id, task_data):
    """Create a new task."""
    tasks = load_tasks()
    tasks[task_id] = task_data
    save_tasks(tasks)
    return task_data


def build_research_prompt(bakery_location: str) -> str:
    """Build comprehensive research prompt for COBS Bread bakery analysis."""
    today = datetime.now().strftime('%B %d, %Y')
    return f"""
You are conducting an exhaustive deep research analysis of customer reviews for the COBS Bread bakery located at: {bakery_location}

**TODAY'S DATE: {today}**

Your task is to find and analyze ALL available reviews across EVERY social media platform and review site. Be extremely thorough and comprehensive. Search for the most recent reviews up to today's date.

## PLATFORMS TO SEARCH (search ALL of these):
- Google Reviews / Google Maps
- Yelp
- Facebook (page reviews and comments)
- Instagram (mentions, tagged posts, comments)
- Twitter/X (mentions, hashtags)
- TikTok (mentions, reviews, videos)
- Reddit (r/vancouver, r/calgary, r/toronto, local subreddits, food subreddits)
- TripAdvisor
- Zomato
- DoorDash reviews
- UberEats reviews
- Skip The Dishes reviews
- Local food blogs and review sites
- News articles mentioning this location
- YouTube reviews and mentions
- LinkedIn (any business mentions)
- NextDoor app mentions
- Local community forums
- Food critic reviews
- Franchise review sites

## ANALYSIS FRAMEWORK:

### SECTION 1: 5-STAR REVIEWS (Excellent - Detailed Analysis)
For every 5-star review found, extract and analyze:
1. **Beloved Products**: List EVERY product mentioned positively with specific details
   - Bread types (sourdough, rye, whole wheat, etc.)
   - Pastries (croissants, danishes, muffins, etc.)
   - Sandwiches and prepared foods
   - Seasonal/special items
   - Frequency of mention for each product

2. **Customer Experience Highlights**:
   - Staff interactions and service quality
   - Store atmosphere and cleanliness
   - Wait times and efficiency
   - Product freshness observations
   - Packaging quality
   - In-store experience

3. **Discovery Journey**:
   - How customers found this bakery (word of mouth, walking by, online search, etc.)
   - What made them first try it
   - How long they've been customers
   - Referral patterns

4. **Loyalty Indicators**:
   - Repeat customer patterns
   - What keeps them coming back
   - Comparisons to other bakeries
   - Brand affinity statements

5. **Value Perception**:
   - Price satisfaction
   - Quality-to-price ratio comments
   - Deals and promotions mentioned

### SECTION 2: 4-STAR REVIEWS (Good but with reservations - Balanced Analysis)
Analyze from DUAL PERSPECTIVES:

**A) Customer/Reviewer Perspective**:
1. **What They Loved**:
   - Specific products praised
   - Positive experiences
   - Strengths identified

2. **What Held Back 5 Stars**:
   - Specific criticisms
   - Products that disappointed
   - Service issues
   - Suggestions for improvement

3. **Conditional Recommendations**:
   - "Great for X but not for Y" statements
   - Situational preferences

**B) COBS Bread Franchisor Perspective**:
1. **Operational Insights**:
   - Consistency issues flagged
   - Training opportunities identified
   - Product quality variations
   - Peak time challenges

2. **Competitive Intelligence**:
   - Comparisons to competitors
   - Market positioning feedback
   - Pricing perception

3. **Growth Opportunities**:
   - Unmet customer needs
   - Product suggestions
   - Service improvements needed

### SECTION 3: 3-STAR AND BELOW (Critical Analysis)
For every review rated 3 stars or lower, deeply analyze:

1. **Problematic Products** (CRITICAL - Be Exhaustive):
   - List EVERY product mentioned negatively
   - Specific issues (staleness, taste, texture, appearance)
   - Frequency of complaints per product
   - Pattern analysis across reviews

2. **Service Failures**:
   - Staff behavior issues
   - Wait time complaints
   - Order accuracy problems
   - Customer service recovery (or lack thereof)

3. **Environmental Issues**:
   - Cleanliness concerns
   - Store layout problems
   - Parking/accessibility issues
   - Noise/crowding complaints

4. **Value Disappointments**:
   - Price complaints
   - Portion size issues
   - Quality-to-price mismatch

5. **Discovery Process Analysis**:
   - How these dissatisfied customers found the bakery
   - What expectations were set vs. reality
   - Impact on word-of-mouth

6. **Severity Assessment**:
   - One-time issues vs. recurring problems
   - Seasonal patterns in complaints
   - Response from bakery (if any)

### SECTION 4: COMPETITIVE LANDSCAPE
- How does this COBS location compare to:
  - Other COBS Bread locations nearby
  - Local independent bakeries
  - Chain competitors (Tim Hortons, Panera, etc.)
  - Grocery store bakeries

### SECTION 5: TREND ANALYSIS
- Review sentiment over time
- Seasonal patterns
- Post-COVID changes
- New product reception
- Staff/management change indicators

### SECTION 6: SOCIAL MEDIA SENTIMENT
- Hashtag analysis
- Viral moments (positive or negative)
- Influencer mentions
- User-generated content themes

### SECTION 7: ACTIONABLE INSIGHTS SUMMARY
Provide specific, actionable recommendations for:
1. Products to highlight/promote
2. Products to improve or consider removing
3. Service training priorities
4. Marketing opportunities
5. Competitive positioning strategies

## SECTION 8: REVIEW STATISTICS & DATA SOURCES (MANDATORY)
**THIS SECTION IS REQUIRED - You MUST include this exact breakdown:**

### 8.1 Total Reviews Analyzed
- **Total number of reviews analyzed**: [exact count]
- **Date range of reviews**: [earliest review date] to {today}

### 8.2 Reviews by Platform (provide exact counts)
Create a table with the following format:
| Platform | # of Reviews | Date Range | Average Rating |
|----------|--------------|------------|----------------|
| Google Reviews | XX | MM/YYYY - MM/YYYY | X.X |
| Yelp | XX | MM/YYYY - MM/YYYY | X.X |
| Facebook | XX | MM/YYYY - MM/YYYY | X.X |
| Instagram | XX mentions | MM/YYYY - MM/YYYY | N/A |
| TripAdvisor | XX | MM/YYYY - MM/YYYY | X.X |
| Reddit | XX mentions | MM/YYYY - MM/YYYY | N/A |
| Twitter/X | XX mentions | MM/YYYY - MM/YYYY | N/A |
| TikTok | XX mentions | MM/YYYY - MM/YYYY | N/A |
| DoorDash | XX | MM/YYYY - MM/YYYY | X.X |
| UberEats | XX | MM/YYYY - MM/YYYY | X.X |
| Skip The Dishes | XX | MM/YYYY - MM/YYYY | X.X |
| YouTube | XX | MM/YYYY - MM/YYYY | N/A |
| Local Blogs | XX | MM/YYYY - MM/YYYY | N/A |
| Other Sources | XX | MM/YYYY - MM/YYYY | N/A |
| **TOTAL** | **XXX** | | |

### 8.3 Rating Distribution (across all platforms)
- 5-star reviews: XX (XX%)
- 4-star reviews: XX (XX%)
- 3-star reviews: XX (XX%)
- 2-star reviews: XX (XX%)
- 1-star reviews: XX (XX%)

### 8.4 Data Limitations
- List any platforms where data was unavailable or limited
- Note any access restrictions encountered
- Mention if certain date ranges had no data

## OUTPUT FORMAT:
- Be extremely detailed and thorough
- Include specific quotes from reviews where possible
- Provide counts/statistics where available
- Organize clearly by section
- Include the source platform for each insight
- **ALWAYS include Section 8 with exact review counts and date ranges**
- Flag any data limitations or gaps in available information

Remember: This research will inform critical business decisions. Leave no stone unturned. The review statistics in Section 8 are MANDATORY and must be accurate.
"""


def generate_word_document(bakery_location: str, report_content: str, output_path: str) -> str:
    """Generate a formatted Word document from the research report."""
    doc = Document()

    # Set up styles
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Title
    title = doc.add_heading('COBS Bread Bakery', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_heading('Comprehensive Review Analysis Report', level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata section
    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.add_run('Location: ').bold = True
    meta.add_run(bakery_location)

    meta2 = doc.add_paragraph()
    meta2.add_run('Generated: ').bold = True
    meta2.add_run(datetime.now().strftime('%B %d, %Y at %I:%M %p'))

    meta3 = doc.add_paragraph()
    meta3.add_run('Research Engine: ').bold = True
    meta3.add_run('Google Deep Research API (Gemini)')

    doc.add_paragraph()
    doc.add_paragraph('_' * 70)
    doc.add_paragraph()

    # Process and add the report content
    add_formatted_content(doc, report_content)

    # Footer
    doc.add_paragraph()
    doc.add_paragraph('_' * 70)
    footer = doc.add_paragraph()
    footer.add_run('Disclaimer: ').bold = True
    footer.add_run(
        'This report is generated from publicly available reviews and social media content. '
        'All insights should be verified independently before making business decisions.'
    )

    # Save the document
    doc.save(output_path)
    return output_path


def add_formatted_content(doc: Document, content: str):
    """Add formatted content to the Word document, parsing markdown-like formatting."""
    import re
    lines = content.split('\n')

    for line in lines:
        stripped = line.strip()

        if not stripped:
            doc.add_paragraph()
            continue

        # Handle headers
        if stripped.startswith('######'):
            doc.add_heading(stripped[6:].strip(), level=6)
        elif stripped.startswith('#####'):
            doc.add_heading(stripped[5:].strip(), level=5)
        elif stripped.startswith('####'):
            doc.add_heading(stripped[4:].strip(), level=4)
        elif stripped.startswith('###'):
            doc.add_heading(stripped[3:].strip(), level=3)
        elif stripped.startswith('##'):
            doc.add_heading(stripped[2:].strip(), level=2)
        elif stripped.startswith('#'):
            doc.add_heading(stripped[1:].strip(), level=1)

        # Handle bullet points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            doc.add_paragraph(stripped[2:], style='List Bullet')

        # Handle numbered lists
        elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.):':
            doc.add_paragraph(stripped[2:].strip(), style='List Number')

        # Handle bold text markers
        elif stripped.startswith('**') and stripped.endswith('**'):
            para = doc.add_paragraph()
            para.add_run(stripped[2:-2]).bold = True

        # Regular paragraph
        else:
            para = doc.add_paragraph()
            # Handle inline bold
            pattern = r'\*\*([^*]+)\*\*'
            parts = re.split(pattern, stripped)

            for i, part in enumerate(parts):
                if i % 2 == 0:
                    para.add_run(part)
                else:
                    para.add_run(part).bold = True


def run_research(task_id: str, location: str):
    """Background task to run the research."""
    try:
        update_task(task_id, {'status': 'running'})

        # Initialize the Google client
        client = genai.Client()

        # Create the research interaction
        prompt = build_research_prompt(location)
        interaction = client.interactions.create(
            input=prompt,
            agent=AGENT_ID,
            background=True
        )

        update_task(task_id, {'interaction_id': interaction.id})

        # Poll for results
        max_poll_time = 3600  # 60 minutes
        poll_interval = 15
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_poll_time:
                update_task(task_id, {
                    'status': 'failed',
                    'error': 'Research exceeded maximum time limit'
                })
                return

            interaction = client.interactions.get(interaction.id)

            if interaction.status == "completed":
                if interaction.outputs:
                    report = interaction.outputs[-1].text

                    # Generate Word document
                    OUTPUTS_DIR.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    safe_location = "".join(c if c.isalnum() or c in ' -_' else '_' for c in location)[:50]
                    doc_path = OUTPUTS_DIR / f"COBS_Research_{safe_location}_{timestamp}.docx"

                    generate_word_document(location, report, str(doc_path))

                    update_task(task_id, {
                        'status': 'completed',
                        'report': report,
                        'report_length': len(report),
                        'document_path': str(doc_path)
                    })
                else:
                    update_task(task_id, {
                        'status': 'failed',
                        'error': 'Research completed but no output received'
                    })
                return

            elif interaction.status == "failed":
                update_task(task_id, {
                    'status': 'failed',
                    'error': getattr(interaction, 'error', 'Unknown error')
                })
                return

            time.sleep(poll_interval)

    except Exception as e:
        update_task(task_id, {
            'status': 'failed',
            'error': str(e)
        })


# Routes
@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    """Serve favicon - COBS brand color bread icon."""
    # SVG favicon with COBS brand color
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <circle cx="16" cy="16" r="15" fill="#862633"/>
        <ellipse cx="16" cy="16" rx="10" ry="7" fill="#D4A574"/>
        <ellipse cx="16" cy="14" rx="8" ry="5" fill="#E8CDB0"/>
        <path d="M10 16 Q16 12 22 16" stroke="#862633" stroke-width="1" fill="none"/>
        <path d="M12 15 Q16 11 20 15" stroke="#862633" stroke-width="0.5" fill="none"/>
    </svg>'''
    return Response(svg, mimetype='image/svg+xml')


@app.route('/api/research', methods=['POST'])
def start_research():
    """Start a new research task."""
    data = request.get_json()
    location = data.get('location', '').strip()

    if not location:
        return jsonify({'error': 'Location is required'}), 400

    # Check for API key
    if not os.environ.get('GOOGLE_API_KEY'):
        return jsonify({'error': 'Google API key not configured. Please add GOOGLE_API_KEY environment variable.'}), 500

    # Create task
    task_id = str(uuid.uuid4())
    task_data = {
        'id': task_id,
        'location': location,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'report': None,
        'document_path': None,
        'error': None
    }
    create_task(task_id, task_data)

    # Start background task
    thread = threading.Thread(target=run_research, args=(task_id, location))
    thread.daemon = True
    thread.start()

    return jsonify({
        'task_id': task_id,
        'status': 'pending',
        'message': 'Research started'
    })


@app.route('/api/research/<task_id>')
def get_research_status(task_id):
    """Get the status of a research task."""
    task = get_task(task_id)

    if not task:
        return jsonify({'error': 'Task not found. The task may have expired or the server was restarted.'}), 404

    response = {
        'task_id': task_id,
        'status': task['status'],
        'location': task['location']
    }

    if task['status'] == 'completed':
        response['report_length'] = task.get('report_length', 0)
        response['document_path'] = task.get('document_path')

    if task['status'] == 'failed':
        response['error'] = task.get('error', 'Unknown error')

    return jsonify(response)


@app.route('/api/download/<task_id>')
def download_document(task_id):
    """Download the generated Word document."""
    task = get_task(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if task['status'] != 'completed':
        return jsonify({'error': 'Research not completed'}), 400

    doc_path = task.get('document_path')
    if not doc_path or not Path(doc_path).exists():
        return jsonify({'error': 'Document not found'}), 404

    return send_file(
        doc_path,
        as_attachment=True,
        download_name=Path(doc_path).name,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    # Create outputs directory
    OUTPUTS_DIR.mkdir(exist_ok=True)

    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

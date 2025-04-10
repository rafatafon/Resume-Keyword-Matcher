# 🔍 AI Resume Keyword Matcher

A tool that scans a user's resume and compares it to a job description, highlighting how well it matches and which important keywords are missing.

## 💼 What It Does
- Analyzes resume and job description text
- Extracts relevant keywords from both
- Calculates a match score
- Identifies matched and missing keywords
- Provides suggestions for improvement

## 💡 Why It's Useful
- Helps job seekers optimize resumes for applicant tracking systems (ATS)
- Shows if they're using the right industry keywords
- Gives actionable feedback on what to add or change

## ⚙️ How It Works
1. User uploads:
   - Their resume (as `.txt` or `.pdf`)
   - A job description
2. AI compares the two and:
   - Highlights matched and missing keywords
   - Gives a match score (e.g., 72%)
   - Suggests improvements (e.g., "Add 'Docker', 'REST API', 'FastAPI'")

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-resume-keyword-matcher.git
cd ai-resume-keyword-matcher

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📦 Project Structure
```
resume-keyword-matcher/
├── app.py                    # Main Streamlit application
├── utils/
│   └── keyword_utils.py      # Keyword extraction & matching logic
├── data/
│   ├── sample_resume.txt     # Sample resume for testing
│   └── sample_job.txt        # Sample job description for testing
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## 📝 Output Example
**Match Score:** 68%  
**Matched Keywords:** Python, JavaScript, React, API, Testing  
**Missing Keywords:** Docker, NLP, CI/CD, AWS  
**Suggestions:** "Consider adding your experience with Docker and NLP tools to better align with the role."

## 🧰 Tech Stack
- **Python**
- **NLP Tools**: spaCy for natural language processing
- **Text Parsing**: Built-in Python text processing
- **Frontend**: Streamlit for interactive web interface

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

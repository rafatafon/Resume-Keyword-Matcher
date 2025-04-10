"""
Keyword extraction and matching utilities for the AI Resume Keyword Matcher.
"""
import re
import string
from collections import Counter
from typing import Dict, List, Tuple, Union

import spacy
from spacy.lang.en.stop_words import STOP_WORDS

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not installed, use a simpler approach
    nlp = spacy.blank("en")
    print("Warning: spaCy model not found. Using basic tokenization instead.")
    print("For better results, install the model with: python -m spacy download en_core_web_sm")

# Additional stop words specific to resumes and job descriptions
CUSTOM_STOP_WORDS = {
    "resume", "cv", "curriculum", "vitae", "job", "description", "position",
    "responsibilities", "requirements", "qualifications", "experience", "education",
    "skills", "company", "work", "email", "phone", "address", "summary", "profile",
    "contact", "information", "apply", "year", "years", "month", "months", "day", "days"
}

# Combine with spaCy's stop words
ALL_STOP_WORDS = STOP_WORDS.union(CUSTOM_STOP_WORDS)

def preprocess_text(text: str) -> str:
    """
    Preprocess text by converting to lowercase, removing punctuation and extra whitespace.
    
    Args:
        text: The input text to preprocess
        
    Returns:
        Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text: str, min_word_length: int = 3, top_n: int = 100) -> List[str]:
    """
    Extract important keywords from text using spaCy.
    
    Args:
        text: The input text to extract keywords from
        min_word_length: Minimum length of words to consider
        top_n: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    # Preprocess the text
    preprocessed_text = preprocess_text(text)
    
    # Process with spaCy
    doc = nlp(preprocessed_text)
    
    # Extract potential keywords (nouns, proper nouns, adjectives, verbs)
    potential_keywords = []
    
    for token in doc:
        # Check if token is a relevant part of speech and not a stop word
        if (token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"} and 
            token.text.lower() not in ALL_STOP_WORDS and
            len(token.text) >= min_word_length and
            token.is_alpha):  # Only alphabetic tokens
            potential_keywords.append(token.lemma_.lower())
    
    # Extract noun phrases (for multi-word terms)
    noun_phrases = []
    for chunk in doc.noun_chunks:
        # Clean the noun phrase
        clean_phrase = ' '.join([token.lemma_.lower() for token in chunk 
                               if token.lemma_.lower() not in ALL_STOP_WORDS
                               and len(token.lemma_) >= min_word_length
                               and token.is_alpha])
        if clean_phrase and ' ' in clean_phrase:  # Only multi-word phrases
            noun_phrases.append(clean_phrase)
    
    # Count frequencies
    keyword_freq = Counter(potential_keywords)
    phrase_freq = Counter(noun_phrases)
    
    # Combine single words and phrases, giving more weight to phrases
    for phrase, count in phrase_freq.items():
        keyword_freq[phrase] = count * 2  # Give phrases more weight
    
    # Get the most common keywords
    keywords = [kw for kw, _ in keyword_freq.most_common(top_n)]
    
    # Add technical terms that might be missed (acronyms, technologies, etc.)
    tech_keywords = extract_technical_terms(preprocessed_text)
    
    # Combine and remove duplicates while preserving order
    all_keywords = []
    seen = set()
    
    for kw in keywords + tech_keywords:
        if kw not in seen:
            all_keywords.append(kw)
            seen.add(kw)
    
    return all_keywords[:top_n]

def extract_technical_terms(text: str) -> List[str]:
    """
    Extract technical terms, acronyms, and programming languages that might be missed by NLP.
    
    Args:
        text: The preprocessed text
        
    Returns:
        List of technical terms
    """
    # Common programming languages, frameworks, tools, etc.
    tech_terms = {
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "swift",
        "kotlin", "go", "rust", "scala", "perl", "r", "matlab", "sql", "nosql", "html", "css",
        "react", "angular", "vue", "node", "express", "django", "flask", "spring", "rails",
        "laravel", "asp.net", "jquery", "bootstrap", "tailwind", "sass", "less",
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "travis", "circleci",
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "slack",
        "mongodb", "postgresql", "mysql", "oracle", "sqlite", "redis", "elasticsearch",
        "kafka", "rabbitmq", "graphql", "rest", "soap", "api", "json", "xml", "yaml",
        "agile", "scrum", "kanban", "waterfall", "tdd", "bdd", "ci/cd", "devops", "sre",
        "ai", "ml", "machine learning", "deep learning", "nlp", "computer vision", "data science",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
        "hadoop", "spark", "tableau", "power bi", "excel", "word", "powerpoint", "outlook",
        "linux", "unix", "windows", "macos", "ios", "android", "react native", "flutter",
        "oauth", "jwt", "saml", "ldap", "ssl", "tls", "https", "tcp/ip", "dns", "http",
        "ui", "ux", "frontend", "backend", "full-stack", "web", "mobile", "desktop", "cloud",
        "microservices", "serverless", "soa", "etl", "crud", "orm", "mvc", "mvvm", "spa"
    }
    
    # Find all tech terms in the text
    words = text.split()
    found_terms = []
    
    for word in words:
        if word.lower() in tech_terms:
            found_terms.append(word.lower())
    
    # Look for common acronyms (all caps words 2-5 letters)
    acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
    found_terms.extend([acr.lower() for acr in acronyms])
    
    return list(set(found_terms))  # Remove duplicates

def get_match_score(resume_keywords: List[str], job_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Calculate match score between resume keywords and job keywords.
    
    Args:
        resume_keywords: List of keywords extracted from the resume
        job_keywords: List of keywords extracted from the job description
        
    Returns:
        Tuple containing:
        - Match score as a percentage
        - List of matched keywords
        - List of missing keywords
    """
    # Convert to sets for easier operations
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    
    # Find matched and missing keywords
    matched_keywords = list(resume_set.intersection(job_set))
    missing_keywords = list(job_set.difference(resume_set))
    
    # Calculate match score
    if not job_set:
        return 100.0, matched_keywords, missing_keywords  # Avoid division by zero
    
    match_score = (len(matched_keywords) / len(job_set)) * 100
    
    return match_score, matched_keywords, missing_keywords

def generate_suggestions(matched_keywords: List[str], missing_keywords: List[str]) -> str:
    """
    Generate improvement suggestions based on matched and missing keywords.
    
    Args:
        matched_keywords: List of matched keywords
        missing_keywords: List of missing keywords
        
    Returns:
        Suggestion text
    """
    if not missing_keywords:
        return "Your resume already contains all the important keywords from the job description. Great job!"
    
    # Group missing keywords by category (if possible)
    tech_missing = []
    soft_skills_missing = []
    other_missing = []
    
    # Simple categorization based on common terms
    tech_terms = {"python", "javascript", "java", "aws", "azure", "docker", "kubernetes", 
                 "react", "angular", "vue", "node", "sql", "nosql", "git", "ci/cd", "api"}
    
    soft_skills = {"communication", "teamwork", "leadership", "problem-solving", 
                  "critical thinking", "time management", "adaptability", "creativity"}
    
    for kw in missing_keywords:
        if kw in tech_terms:
            tech_missing.append(kw)
        elif kw in soft_skills:
            soft_skills_missing.append(kw)
        else:
            other_missing.append(kw)
    
    suggestions = []
    
    if tech_missing:
        tech_str = ", ".join([f"'{k}'" for k in tech_missing[:3]])
        if len(tech_missing) > 3:
            tech_str += f", and {len(tech_missing) - 3} more technical skills"
        suggestions.append(f"Consider adding your experience with {tech_str} to better align with the technical requirements.")
    
    if soft_skills_missing:
        soft_str = ", ".join([f"'{k}'" for k in soft_skills_missing[:2]])
        if len(soft_skills_missing) > 2:
            soft_str += ", and other soft skills"
        suggestions.append(f"Highlight your {soft_str} skills, which are valued in this role.")
    
    if other_missing:
        other_str = ", ".join([f"'{k}'" for k in other_missing[:3]])
        if len(other_missing) > 3:
            other_str += ", and other relevant keywords"
        suggestions.append(f"Include experience related to {other_str} if you have it.")
    
    return " ".join(suggestions)

def analyze_resume_job_match(resume_text: str, job_text: str) -> Dict[str, Union[float, List[str], str]]:
    """
    Analyze the match between a resume and job description.
    
    Args:
        resume_text: The resume text content
        job_text: The job description text content
        
    Returns:
        Dictionary containing match score, matched keywords, missing keywords, and suggestions
    """
    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)
    
    # Get match score and keyword lists
    match_score, matched_keywords, missing_keywords = get_match_score(resume_keywords, job_keywords)
    
    # Generate suggestions
    suggestions = generate_suggestions(matched_keywords, missing_keywords)
    
    return {
        "match_score": round(match_score, 1),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions
    }

# Simple test function
def test_keyword_extraction():
    """Test the keyword extraction functionality with sample text."""
    sample_text = """
    Experienced software engineer with expertise in Python, JavaScript, and React.
    Developed scalable web applications and RESTful APIs.
    """
    keywords = extract_keywords(sample_text)
    print("Extracted Keywords:", keywords)
    
if __name__ == "__main__":
    test_keyword_extraction()

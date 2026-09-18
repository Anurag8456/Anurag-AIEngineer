import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
import json
from pydantic import BaseModel
from typing import List

# 1. Setup and Authentication
load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
CLIENT = Groq(api_key=my_api_key)

model = "llama-3.3-70b-versatile"

# 2. Extract Text Function
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

resume_text = extract_text_from_pdf(r"C:\Users\Anurag\Downloads\Anurag Singh Resume (2).pdf")

# 3. Pydantic Models
class ResumeData(BaseModel):
    skills: List[str]
    years_of_experience: int
    projects: List[str]

class HRRequirements(BaseModel):
    required_skills: List[str]
    minimum_experience: int
    required_project_keywords: List[str]

hr_criteria = HRRequirements(
    required_skills=["Python", "SQL", "Machine Learning", "AWS"],
    minimum_experience=2,
    required_project_keywords=["Dashboard", "Prediction", "API"]
)

# 4. LLM API Call
system_prompt = f"""
You are an expert HR assistant. Extract the candidate's skills, total years of experience, and project names/summaries from the provided resume text. 
Return the output strictly in JSON format matching this schema: {ResumeData.model_json_schema()}
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Resume Text:\n{resume_text}"}
]

response = CLIENT.chat.completions.create(
    model=model,
    messages=messages,
    response_format={"type": "json_object"}
)

raw_json = response.choices[0].message.content
data_file = json.loads(raw_json)

# Parse into Pydantic model
extracted_resume = ResumeData(**data_file)    

# 5. Evaluation Logic (Updated for Verdict & Reasoning)
def evaluate_candidate(resume: ResumeData, hr: HRRequirements) -> dict:
    score = 0
    total_criteria = 3 
    reasoning_points = []
    
    # Match Skills
    resume_skills_lower = {s.lower() for s in resume.skills}
    hr_skills_lower = {s.lower() for s in hr.required_skills}
    
    if hr_skills_lower:
        matched_skills = resume_skills_lower.intersection(hr_skills_lower)
        missing_skills = hr_skills_lower - resume_skills_lower
        skill_match_ratio = len(matched_skills) / len(hr_skills_lower)
        score += skill_match_ratio
        
        if skill_match_ratio == 1.0:
            reasoning_points.append("Has all required skills.")
        elif skill_match_ratio > 0:
            reasoning_points.append(f"Missing skills: {', '.join(missing_skills).title()}.")
        else:
            reasoning_points.append("Missing all required skills.")
            
    # Match Experience
    if resume.years_of_experience >= hr.minimum_experience:
        score += 1
        reasoning_points.append(f"Meets experience requirement ({resume.years_of_experience} yrs).")
    else:
        reasoning_points.append(f"Short on experience ({resume.years_of_experience} yrs vs {hr.minimum_experience} needed).")
        
    # Match Projects
    project_text = " ".join(resume.projects).lower()
    matched_kws = [kw for kw in hr.required_project_keywords if kw.lower() in project_text]
    missing_kws = [kw for kw in hr.required_project_keywords if kw.lower() not in project_text]
    
    if hr.required_project_keywords:
        project_match_ratio = len(matched_kws) / len(hr.required_project_keywords)
        score += project_match_ratio
        
        if project_match_ratio == 1.0:
            reasoning_points.append("All project keywords found.")
        elif project_match_ratio > 0:
            reasoning_points.append(f"Missing project keywords: {', '.join(missing_kws)}.")
        else:
            reasoning_points.append("No required project keywords found.")
            
    # Calculate Final Percentage
    final_percentage = round((score / total_criteria) * 100, 2)
    
    # Determine Verdict
    if final_percentage >= 80:
        verdict = "Strong Match (Pass)"
    elif final_percentage >= 50:
        verdict = "Potential Match (Review)"
    else:
        verdict = "Not a Match (Fail)"
        
    return {
        "verdict": verdict,
        "score": final_percentage,
        "reasoning": " | ".join(reasoning_points)
    }

# 6. Execute and Print Results
evaluation = evaluate_candidate(extracted_resume, hr_criteria)

print("\n--- RESUME EVALUATION RESULTS ---")
print(f"Verdict:   {evaluation['verdict']}")
print(f"Score:     {evaluation['score']}%")
print(f"Reasoning: {evaluation['reasoning']}")
print("---------------------------------\n")
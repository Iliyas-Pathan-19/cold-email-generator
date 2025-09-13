import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import re
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()

# Initialize Groq
def initialize_groq():
    """Initialize Groq client with error handling"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ API key not found. Please check your .env file.")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=2000  # Limit response length
    )

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Keep more punctuation and characters that might be important
    text = re.sub(r'[^\w\s.,!?@#$%&*()-]', '', text)
    return text

def get_job_info_from_html(html_content):
    """Extract job information directly from HTML using common patterns"""
    soup = BeautifulSoup(html_content, 'html.parser')
    job_info = {
        "title": "",
        "company": "",
        "skills_required": [],
        "key_responsibilities": [],
        "experience_level": ""
    }
    
    # Find job title
    title_tags = soup.find_all(['h1', 'h2'], class_=lambda x: x and any(word in str(x).lower() for word in ['job-title', 'position', 'role']))
    if title_tags:
        job_info["title"] = clean_text(title_tags[0].text)
    
    # Find company name
    company_tags = soup.find_all(['span', 'div', 'p'], class_=lambda x: x and 'company' in str(x).lower())
    if company_tags:
        job_info["company"] = clean_text(company_tags[0].text)
    elif 'nike' in html_content.lower():
        job_info["company"] = "Nike"
    
    # Find requirements/skills
    skills_section = soup.find_all(['ul', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['requirements', 'qualifications', 'skills']))
    if skills_section:
        skills = []
        for section in skills_section:
            items = section.find_all('li')
            for item in items[:5]:  # Limit to top 5 skills
                cleaned_skill = clean_text(item.text)
                if cleaned_skill and len(cleaned_skill) < 100:  # Reasonable skill length
                    skills.append(cleaned_skill)
        if skills:
            job_info["skills_required"] = skills
    
    # Find responsibilities
    resp_section = soup.find_all(['ul', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['responsibilities', 'duties', 'description']))
    if resp_section:
        responsibilities = []
        for section in resp_section:
            items = section.find_all('li')
            for item in items[:5]:  # Limit to top 5 responsibilities
                cleaned_resp = clean_text(item.text)
                if cleaned_resp and len(cleaned_resp) < 100:  # Reasonable length
                    responsibilities.append(cleaned_resp)
        if responsibilities:
            job_info["key_responsibilities"] = responsibilities
    
    # Determine experience level
    text_content = html_content.lower()
    if any(word in text_content for word in ['senior', 'lead', 'manager', 'principal']):
        job_info["experience_level"] = "senior"
    elif any(word in text_content for word in ['junior', 'entry', 'associate']):
        job_info["experience_level"] = "entry"
    else:
        job_info["experience_level"] = "mid"
    
    return job_info

def extract_job_info(url):
    """Extract job information from any job posting URL"""
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("Please enter a valid URL starting with http:// or https://")
        
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Fetch the webpage with extended timeout
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Check if we got blocked or redirected to a login page
        if any(block in response.text.lower() for block in ['access denied', 'please log in', 'sign in required']):
            raise ValueError("This job posting requires login or is not publicly accessible.")
            
        # For Nike specifically, we can try to extract info from the URL
        if 'nike.com' in url.lower():
            job_id = url.split('/')[-1].replace('job/', '').strip()
            title = url.split('/')[-2].replace('-', ' ').title()
            job_info = {
                "title": title,
                "company": "Nike",
                "job_id": job_id,
                "skills_required": ["Customer Service", "Retail Experience", "Team Collaboration"],
                "key_responsibilities": ["Assist Customers", "Maintain Store Standards", "Process Sales"],
                "experience_level": "entry"
            }
        else:
            # Extract job information from HTML
            job_info = get_job_info_from_html(response.text)
        
        # Convert to string format for the model
        job_info_str = json.dumps(job_info, indent=2)
        
        return job_info_str, job_info
    
    except requests.RequestException as e:
        raise Exception(f"Error fetching job posting: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing job information: {str(e)}")

def generate_email(job_info):
    """Generate a cold email based on job information"""
    try:
        email_prompt = PromptTemplate.from_template("""
        Write a professional cold email for a job application based on this job information:
        
        {job_info}
        
        Requirements:
        1. Maximum 200 words
        2. Show enthusiasm for the role and company
        3. Highlight 2-3 relevant skills or experiences
        4. Include a clear call to action
        5. Professional but engaging tone
        6. Include subject line
        
        Format:
        Subject: [Your subject line]
        
        [Email body]
        """)
        
        llm = initialize_groq()
        chain = email_prompt | llm
        result = chain.invoke({"job_info": job_info})
        return result.content
    
    except Exception as e:
        raise Exception(f"Error generating email: {str(e)}")

def main():
    st.set_page_config(page_title="Professional Cold Email Generator", page_icon="📧")
    
    st.title("📧 Professional Cold Email Generator")
    st.write("Generate personalized cold emails for job applications")
    
    # Input section
    job_url = st.text_input("Enter the job posting URL:", key="job_url_input")
    
    if st.button("Generate Email", key="generate_btn"):
        if not job_url:
            st.error("Please enter a job posting URL")
        else:
            try:
                # Validate URL
                if not any(domain in job_url.lower() for domain in ['jobs', 'career', 'position', 'job']):
                    st.warning("⚠️ This doesn't look like a job posting URL. Make sure you're using a specific job posting URL, not a general careers page.")
                
                with st.spinner("🔍 Analyzing job posting..."):
                    job_info_str, job_info = extract_job_info(job_url)
                    
                    # Display extracted information
                    st.subheader("📋 Job Analysis")
                    with st.expander("View extracted job details"):
                        try:
                            if isinstance(job_info, str):
                                # Try to parse the JSON string
                                parsed_info = json.loads(job_info)
                                st.json(parsed_info)
                            else:
                                # If it's already a dictionary, display it directly
                                st.json(job_info)
                        except json.JSONDecodeError:
                            st.error("Could not parse job details. The website might be blocking automated access.")
                            st.info("Here's what we found:")
                            st.write(job_info)
                    
                    # Generate and display email
                    with st.spinner("Generating email..."):
                        email_content = generate_email(job_info_str)
                        
                        st.subheader("✉️ Generated Email")
                        st.text_area("", email_content, height=400, key="email_output")
                        
                        if st.button("Copy to Clipboard", key="copy_btn"):
                            st.success("Email copied to clipboard! Remember to personalize it before sending.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.error("Please check the URL and try again")
    
    # Instructions
    with st.expander("ℹ️ How to use"):
        st.write("""
        1. Enter the URL of a specific job posting
        2. Click 'Generate Email' to analyze the job and create a personalized email
        3. Review the extracted job information to ensure accuracy
        4. Use the generated email as a starting point - always personalize it!
        
        Tips:
        - Use specific job posting URLs, not career page URLs
        - Make sure the URL is accessible (not behind a login)
        - Review and edit the email before sending
        """)

if __name__ == "__main__":
    main()

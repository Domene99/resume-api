from flask import Flask, request, Response, jsonify
import json
import openai
import os
import PyPDF2

app = Flask(__name__)

MAX_RETRIES = 10

def resumeParse(resume):
    RESUME_SCHEMA ="""
    "{
    "full_name": "",
    "email": "",
    "phone": "",
    "address": "",
    "linkedin": "",
    "website": "",
    "objective": "",
    "summary": "",
    "education": [
        {
            "institution": "",
            "degree": "",
            "field_of_study": "",
            "start_date": "",
            "end_date": "",
            "gpa": "",
            "honors_awards": [],
            "courses": []
        }
    ],
    "experience": [
        {
            "title": "",
            "company": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "description": "",
            "achievements": [],
            "technologies": [],
            "projects": []
        }
    ],
    "skills": {
        "technical": [],
        "soft": []
    },
    "languages": [],
    "certifications": [],
    "volunteer_experience": [],
    "publications": [],
    "patents": [],
    "hobbies_interests": []
}
" 
    """

    CONTENT = "Use this schema \" " + RESUME_SCHEMA  + " \" to parse this resume \"" + resume + "\". Include no added commentary, explanation, confirmation or preamble in your response. Include only the json response"
    if len(CONTENT) // 4 > 2500:
        return { "choices": [ { "finish_reason" : "length" } ] }

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": CONTENT},
        ]
    )
    
    return response
    # return {"hi": "you"}

@app.route('/resume', methods=["GET"])
def resume():
    resume = request.form.get("resume")
    
    key = os.getenv('OPENAI_KEY')
    openai.api_key = key

    response = None
    # retries = 0
    # while retries < MAX_RETRIES and response is None:
    while response is None:
        try:
            openai_response = resumeParse(resume)
            if openai_response["choices"][0]["finish_reason"] == "length":
                return "Exceeded maximum size of resume (~8,000 chars or ~1500 words)", 413
            response = json.loads(openai_response["choices"][0]["message"]["content"])            
        except ValueError:
            response = None
    if response is None:
        return "Malformed json response from neural network.", 500
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
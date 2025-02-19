import cohere
from key import API_KEY
import streamlit as st

COHERE_API_KEY = API_KEY
co = cohere.ClientV2(COHERE_API_KEY)

# Initialize session state for filters if not exists
if 'selected_filters' not in st.session_state:
    st.session_state.selected_filters = {
        'Location': [],
        'Type of School': [],
        'Cost': [],
        'Programs': [],
        'Campus Life': [],
        'Admissions': []
    }

# Initialize universities in session state if not exists
if 'universities' not in st.session_state:
    st.session_state.universities = {}

st.title("College Finder Chatbot")

st.subheader("Filters")

filter_cols = st.columns(6)
filter_options = {
    'Location': ['United States', 'Canada', 'United Kingdom', 'Australia'],
    'Type of School': ['Public', 'Private', 'Liberal Arts', 'Research'],
    'Cost': ['<$20K', '$20K-$30K', '$30K-$40K', '$40K-$50K', '$50K+'],
    'Programs': ['Computer Science', 'Engineering', 'Business', 'Arts'],
    'Campus Life': ['Urban', 'Rural', 'Suburban'],
    'Admissions': ['Competitive', 'Moderate', 'Less Selective']
}

# Create dropdown menus horizontally
for i, (filter_name, options) in enumerate(filter_options.items()):
    with filter_cols[i]:
        selected = st.selectbox(filter_name, ['Select'] + options, key=f"filter_{filter_name}")
        if selected != 'Select' and selected not in st.session_state.selected_filters[filter_name]:
            st.session_state.selected_filters[filter_name].append(selected)

user_input = st.text_area("Write about yourself (e.g., grades, interests, location preferences):", "")

def build_system_message():
    filter_text = "\n".join([
        f"{filter_name}: {', '.join(values)}" 
        for filter_name, values in st.session_state.selected_filters.items() 
        if values
    ])

    return f"""## Task and Context: 
    You are a chatbot designed to help a student find the best colleges suited for them. 
    Please provide at least 10 university recommendations.
    For each recommended college, format your response exactly as follows:

    UNIVERSITY: [University Name]
    INFO: [Include acceptance rate, tuition, average GPA, and other key statistics]
    FIT: [Explain why this university would be a good fit based on the student's input]
    NEXT_UNIVERSITY

    Provide recommendations based on these filters:
    {filter_text}
    """

def parse_ai_response(response_text):
    universities = {}
    
    university_sections = response_text.split('NEXT_UNIVERSITY')
    
    for section in university_sections:
        if not section.strip():
            continue
            
        try:
            uni_name = section.split('UNIVERSITY:')[1].split('INFO:')[0].strip()
            info = section.split('INFO:')[1].split('FIT:')[0].strip()
            fit = section.split('FIT:')[1].strip()

            universities[uni_name] = {
                "info": info.replace('$', '\\$'),
                "why_fit": fit
            }
        except IndexError:
            continue
    
    return universities


if st.button("Get College Recommendations", use_container_width=True):
    st.subheader("Suggested Universities")
    with st.spinner("Loading recommendations..."):
        system_message = build_system_message()
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        response = co.chat_stream(
            model="command-r-plus-08-2024", 
            messages=messages, 
            temperature=1,
            max_tokens=4096
        )

        full_response = ""
        for event in response:
            if event.type == "content-delta":
                full_response += event.delta.message.content.text

        # Parse the response and update universities
        try:
            parsed_universities = parse_ai_response(full_response)
            st.session_state.universities = parsed_universities
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing AI response: {str(e)}")

if st.session_state.universities:
    st.subheader("Suggested Universities")
    
    # Display universities as expandable sections
    for uni_name, details in st.session_state.universities.items():
        with st.expander(uni_name):
            st.write(details["info"])
            st.write("Why this is a good fit:")
            st.write(details["why_fit"])


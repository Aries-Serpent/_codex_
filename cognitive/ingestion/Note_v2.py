# Note_v2.py

import streamlit as st
from transformers import pipeline
from keybert import KeyBERT
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from textblob import TextBlob

# Function to prepare the classifier model
def prepare_classifier_model():
    # Sample data for demonstration purposes
    data = pd.DataFrame({
        'query': [
            "How to improve my Python code?",
            "What is machine learning?",
            "Best practices for NLP",
            "Understanding deep learning models",
            "Tips for data preprocessing",
            "How to use transformers for NER?",
            "Clustering algorithms in Scikit-learn",
            "Automating tasks with AutoML",
            "Sentiment analysis using TextBlob",
            "Implementing KMeans clustering"
        ],
        'category': [
            "Programming",
            "Machine Learning",
            "NLP",
            "Deep Learning",
            "Data Preprocessing",
            "NLP",
            "Machine Learning",
            "AutoML",
            "NLP",
            "Machine Learning"
        ]
    })

    # Split data
    X = data['query']
    y = data['category']
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define models to test
    models = {
        'Naive Bayes': MultinomialNB(),
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Linear SVC': LinearSVC(),
        'Random Forest': RandomForestClassifier()
    }

    # Vectorizer
    vectorizer = TfidfVectorizer()

    # Find the best model based on training accuracy
    best_score = 0
    best_model = None
    best_model_name = ""
    for model_name, model in models.items():
        pipeline_model = make_pipeline(vectorizer, model)
        pipeline_model.fit(X_train, y_train)
        score = pipeline_model.score(X_train, y_train)
        st.write(f"Model: {model_name}, Training Accuracy: {score:.2f}")
        if score > best_score:
            best_score = score
            best_model = pipeline_model
            best_model_name = model_name

    st.write(f"**Best Model:** {best_model_name} with Training Accuracy: {best_score:.2f}")
    return best_model

# Function to load all models with caching
@st.cache_resource
def load_models():
    summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
    kw_model = KeyBERT()
    ner_pipeline = pipeline(
        "ner",
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
        aggregation_strategy="simple"  # Updated to avoid deprecation warning
    )
    classifier_model = prepare_classifier_model()
    return summarizer, kw_model, ner_pipeline, classifier_model

# Load models
summarizer, kw_model, ner_pipeline, classifier_model = load_models()

# Initialize session storage
if 'sessions' not in st.session_state:
    st.session_state.sessions = []

# Streamlit App Layout
st.title("Token-Friendly Query Converter")

# Input Section
st.header("Enter Your Message")
input_text = st.text_area("Input Text", height=150)

# Summarization Options
st.header("Summarization Options")
summarization_method = st.radio("Choose Summarization Method", ("Standard Summarization", "Keyword Emphasis Summarization"))

# Additional Features
st.header("Additional Features")
enable_ner = st.checkbox("Named Entity Recognition")
enable_sentiment = st.checkbox("Sentiment Analysis")
enable_classification = st.checkbox("Classify Query")

# Length Sliders
st.header("Summarization Length")
col1, col2 = st.columns(2)
with col1:
    min_length = st.slider("Min Length", min_value=10, max_value=150, value=30)
with col2:
    max_length = st.slider("Max Length", min_value=30, max_value=300, value=150)

# Convert Button
if st.button("Convert"):
    # Input validation
    if not input_text.strip():
        st.warning("Please enter a message to convert.")
    elif len(input_text) < 10:
        st.warning("The input text is too short to summarize.")
    elif len(input_text) > 5000:
        st.warning("The input text is too long. Please enter a shorter message.")
    elif min_length > max_length:
        st.warning("Minimum length cannot be greater than maximum length.")
    else:
        # Processing
        with st.spinner("Processing..."):
            try:
                # Summarization
                if summarization_method == "Standard Summarization":
                    summary = summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
                else:
                    keywords = kw_model.extract_keywords(input_text, keyphrase_ngram_range=(1, 2), stop_words='english')
                    important_phrases = [kw[0] for kw in keywords[:5]]
                    summary = summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
                    for phrase in important_phrases:
                        if phrase.lower() not in summary.lower():
                            summary += f" {phrase}."

                # Analysis Results
                analysis_results = ""

                # NER
                if enable_ner:
                    entities = ner_pipeline(input_text)
                    if entities:
                        ner_results = "\n**Named Entities:**\n"
                        for ent in entities:
                            entity_group = ent.get("entity_group", "Unknown")
                            entity = ent.get("word", ent.get("entity"))
                            ner_results += f"- {entity}: {entity_group}\n"
                    else:
                        ner_results = "\n**Named Entities:**\n- None found.\n"
                    analysis_results += ner_results

                # Sentiment Analysis
                if enable_sentiment:
                    blob = TextBlob(input_text)
                    sentiment = blob.sentiment.polarity
                    if sentiment > 0:
                        sentiment_label = "Positive"
                    elif sentiment < 0:
                        sentiment_label = "Negative"
                    else:
                        sentiment_label = "Neutral"
                    sentiment_results = f"\n**Sentiment Analysis:**\n- Sentiment: {sentiment_label}\n"
                    analysis_results += sentiment_results

                # Query Classification
                if enable_classification:
                    prediction = classifier_model.predict([input_text])
                    category = prediction[0]
                    classification_results = f"\n**Query Classification:**\n- Category: {category}\n"
                    analysis_results += classification_results

                # Display Results
                st.header("Token-Friendly Query")
                st.write(summary)
                if analysis_results:
                    st.header("Analysis Results")
                    st.write(analysis_results)

                # Save Session
                session = {
                    'input': input_text,
                    'output': summary,
                    'analysis': analysis_results
                }
                st.session_state.sessions.append(session)
                st.success("Conversion completed and session saved.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Sessions Management
st.header("Processed Sessions")
if st.session_state.sessions:
    for idx, session in enumerate(reversed(st.session_state.sessions), 1):
        with st.expander(f"Session {len(st.session_state.sessions) - idx + 1}"):
            st.write("**Input:**")
            st.write(session['input'])
            st.write("**Output:**")
            st.write(session['output'])
            if session['analysis']:
                st.write("**Analysis:**")
                st.write(session['analysis'])
else:
    st.write("No sessions processed yet.")

# Save and Load Sessions
st.sidebar.header("Session Management")

# Save Sessions
save_button = st.sidebar.button("Save Sessions")
if save_button:
    if st.session_state.sessions:
        file_name = st.sidebar.text_input("Enter file name", value="sessions.json")
        if file_name:
            with open(file_name, "w") as f:
                json.dump(st.session_state.sessions, f, indent=4)
            st.sidebar.success(f"Sessions saved to `{file_name}`.")
        else:
            st.sidebar.warning("Please enter a valid file name.")
    else:
        st.sidebar.warning("No sessions to save.")

# Load Sessions
uploaded_file = st.sidebar.file_uploader("Load Sessions", type=["json"])
if uploaded_file is not None:
    try:
        loaded_sessions = json.load(uploaded_file)
        st.session_state.sessions.extend(loaded_sessions)
        st.sidebar.success("Sessions loaded successfully.")
    except Exception as e:
        st.sidebar.error(f"Error loading sessions: {e}")

# Clear Sessions
if st.sidebar.button("Clear Sessions"):
    st.session_state.sessions.clear()
    st.sidebar.success("All sessions have been cleared.")

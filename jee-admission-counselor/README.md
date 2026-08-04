---
title: JEE Admission Counselor AI
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
---

# 🎓 JEE Admission Counselor AI

An AI-powered admission counseling assistant built on 8 years (2018-2025) of 
JoSAA (Joint Seat Allocation Authority) cutoff data covering 432,524 admission 
records across 136 institutes (IITs, NITs, IIITs, GFTIs).

## Features

- **Rank-based College Finder**: Enter your JEE rank, category, and preferences 
  to get realistic college recommendations with safety verdicts
- **Trend Analysis**: Track how closing ranks for specific colleges/programs 
  changed over the years
- **Best College Rankings**: Find the most competitive colleges for any branch
- **Natural Language Interface**: Powered by Groq LLaMA-3.1 for intent understanding

## Tech Stack

- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Random Forest Regressor (R² = 0.87) for closing rank prediction
- **RAG**: FAISS vector store with 81,112 indexed documents, 
  HuggingFace sentence-transformers embeddings
- **LLM**: Groq (LLaMA-3.1-8b-instant) for query understanding
- **UI**: Streamlit

## Architecture

The system uses a hybrid approach:
1. LLM classifies user intent and extracts structured parameters
2. Deterministic pandas-based engines compute exact rankings/filters/trends
3. RAG handles open-ended comparison questions

This avoids LLM hallucination on numerical data while retaining natural 
language flexibility.

## Data Source

JoSAA Cutoff data 2018-2025 (Rounds 1-6), sourced from official JoSAA 
counselling records via Kaggle.

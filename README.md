# Health Functional Food Review Fact-Check System

A web service prototype that collects online reviews of health functional food products, uses AI to identify advertising reviews, and provides analysis results from a pharmacist's perspective.

## 📖 Project Introduction

This project analyzes review data for 5 Lutein products collected from iHerb to:
- **Ad Review Detection**: Automatic verification based on 13-step checklist
- **Trust Score Calculation**: Quantitative evaluation system
- **AI Pharmacist Analysis**: Professional insights using Claude AI
- **Visualization Dashboard**: Interactive UI based on Streamlit

## 🏗️ Project Structure

```
ica-github/
├── dev2-2Hour/
│   └── dev2-main/          # Main project folder
│       ├── docs/           # Project documents
│       ├── database/       # Database module
│       ├── logic_designer/ # Logic design and AI analysis
│       ├── ui_integration/ # Streamlit UI
│       ├── data_manager/   # Data collection and upload
│       └── dev_logs/       # Development logs
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Siyeolryu/ica-github.git
cd ica-github/dev2-2Hour/dev2-main
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
cd ui_integration
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file and add:

```env
# Supabase Settings
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# Anthropic Claude API (Optional)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Run Streamlit App

```bash
cd ui_integration
streamlit run app.py
```

## 📚 Main Features

### 1. Trust Score Verification Engine
- 13-step ad detection checklist
- Quantitative trust score calculation (0-100)
- Automatic ad review detection

### 2. AI Pharmacist Analysis
- Claude AI-based professional analysis
- Efficacy, side effects, advice provision
- Hallucination prevention logic

### 3. Visualization Dashboard
- Trust score gauge chart
- Radar chart (5 indicator comparison)
- Price comparison bar chart
- Review detail view

## 📖 Detailed Documentation

For detailed project documentation, refer to `dev2-2Hour/dev2-main/docs/` folder:

- [Project Overview](dev2-2Hour/dev2-main/docs/project-overview.md)
- [Team Collaboration Guide](dev2-2Hour/dev2-main/docs/team-collaboration-guide-week1.md)
- [User Scenario](dev2-2Hour/dev2-main/docs/user-scenario.md)

## 🛠️ Technology Stack

- **Database**: Supabase (PostgreSQL)
- **AI Analysis**: Anthropic Claude API
- **UI Framework**: Streamlit
- **Visualization**: Plotly
- **Language**: Python 3.8+

## 📝 Development Logs

Project development process can be found in `dev2-2Hour/dev2-main/dev_logs/` folder.

## 🤝 Contributing

This is a team project. To contribute, please create an issue or submit a Pull Request.

## 📄 License

This project is created for educational purposes.

## 🔗 Related Links

- [Supabase Dashboard](https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf)
- [Streamlit Cloud](https://streamlit.io/cloud)

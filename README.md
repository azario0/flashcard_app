# PDF Flashcard Generator & Quiz App

A Flask web application that transforms PDF documents into interactive flashcard quizzes using Google's Gemini AI. Upload any PDF, and the app will automatically generate questions and answers for an engaging learning experience.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)

## 🚀 Features

- **PDF Text Extraction**: Seamlessly extract text content from PDF files
- **AI-Powered Flashcard Generation**: Leverage Google's Gemini 1.5 Flash API to create intelligent Q&A pairs
- **Interactive Quiz Interface**: User-friendly quiz experience with immediate feedback
- **Detailed Scoring**: Comprehensive results with score tracking
- **Clean UI**: Simple, responsive design for optimal user experience
- **Session Management**: Secure handling of quiz data and user sessions

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://ai.google.dev/))
- Pip (Python package installer)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/azario0/flashcard_app.git
   cd flashcard_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install Flask python-dotenv google-generativeai PyMuPDF
   ```

3. **Set up environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   GEMINI_API_KEY="your_actual_gemini_api_key_here"
   FLASK_SECRET_KEY="your_strong_random_secret_key_here"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   
   Open your browser and navigate to `http://127.0.0.1:5000/`

## 🎯 Usage

1. **Upload PDF**: Click "Choose PDF file" and select your document
2. **Generate Flashcards**: Click "Generate Flashcards" to process the PDF
3. **Take Quiz**: Answer the generated questions one by one
4. **View Results**: See your score and detailed feedback
5. **Repeat**: Start a new quiz with another PDF

## 📁 Project Structure

```
flashcard_app/
├── app.py                     # Main Flask application
├── templates/
│   ├── layout.html            # Base HTML template
│   ├── index.html             # PDF upload page
│   ├── quiz.html              # Quiz interface
│   ├── results.html           # Results display
│   └── _flash_messages.html   # Flash message partial
├── static/
│   └── css/
│       └── style.css          # Application styling
├── .env                       # Environment variables (create this)
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |
| `FLASK_SECRET_KEY` | Random string for session security | Yes |

### API Limits

- Current token limit: 10,000 tokens per request
- Gemini 1.5 Flash supports much higher limits if needed
- Large PDFs may require processing time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **PDF Quality**: Flashcard quality depends on PDF content structure and readability
- **Processing Time**: Large PDFs may take longer to process
- **API Costs**: Ensure your Gemini API key has proper billing setup if required
- **Session Storage**: Quiz data is stored in browser sessions (cookies)
- **Security**: Use strong secret keys in production environments

## 🐛 Troubleshooting

### Common Issues

**"API Key Error"**
- Verify your `GEMINI_API_KEY` in the `.env` file
- Ensure the API key has necessary permissions

**"PDF Processing Failed"**
- Check if the PDF contains extractable text (not just images)
- Try with a smaller PDF file first

**"Session Errors"**
- Clear your browser cookies
- Restart the Flask application

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/azario0/flashcard_app/issues) page
2. Create a new issue with detailed information
3. Contact: [azario0](https://github.com/azario0)

## 🙏 Acknowledgments

- Google Gemini AI for powering the flashcard generation
- Flask community for the excellent web framework
- PyMuPDF for reliable PDF text extraction

---

**Made with ❤️ by [azario0](https://github.com/azario0)**
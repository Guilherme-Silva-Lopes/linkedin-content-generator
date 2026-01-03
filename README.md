# LinkedIn Content Automation - Kestra Workflow

Automated LinkedIn content generation system that creates engaging posts about AI, Automation, and Low-Code topics using AI agents and publishes them automatically.

## 🌟 Features

- **AI-Powered Content**: Uses LangChain 1.0 `create_agent` with Google Gemini for intelligent content creation
- **Web Research**: Leverages Brave Search API to find trending topics
- **Visual Content**: Generates custom images using Gemini 2.5 Flash Image
- **Auto Publishing**: Posts directly to LinkedIn via API
- **Theme Tracking**: Uses Google Sheets to avoid topic repetition
- **Scheduled Execution**: Runs 3 times per day (9am, 2pm, 5pm - Brazil time)

## 📁 Project Structure

```
.
├── linkedin-content-generator.yml    # Kestra workflow definition
├── requirements.txt                   # Python dependencies
├── scripts/
│   ├── linkedin_agent.py             # Main AI agent for content creation
│   ├── sheets_manager.py             # Google Sheets integration
│   ├── gemini_image_generator.py     # Image generation using Gemini
│   └── linkedin_publisher.py         # LinkedIn API publishing
└── README.md                          # This file
```

## 🔧 Setup Instructions

### 1. Prerequisites

- Kestra instance running
- GitHub repository for storing scripts
- Google Cloud API key (for Gemini)
- Brave Search API key
- LinkedIn OAuth2 credentials
- Google Sheets API credentials (Service Account)

### 2. GitHub Repository Setup

1. Create a GitHub repository (e.g., `linkedin-content-automation`)
2. Push all files from this project to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/linkedin-content-automation
   git push -u origin main
   ```

3. Update the `clone_repo` task in `linkedin-content-generator.yml` with your repository URL

### 3. Kestra KV Store Configuration

Add the following keys to Kestra's KV Store:

```bash
# Google Gemini API Key
kestra kv set GOOGLE_API_KEY "your-google-api-key-here"

# Brave Search API Key
kestra kv set BRAVE_SEARCH "your-brave-search-api-key-here"

# LinkedIn Access Token (OAuth2)
kestra kv set LINKEDIN_ACCESS_TOKEN "your-linkedin-access-token-here"

# Google Sheets Credentials (Service Account JSON)
kestra kv set GOOGLE_SHEETS_CREDENTIALS '{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}'
```

### 4. Google Sheets Setup

1. Create a Google Sheet with ID: `1g7ZLdPYc8-XyKIexgHhpot8HTtcAv5uQmMXjBK4QUEo` (or update the ID in `sheets_manager.py`)
2. Add a header row with "TEMA" in cell A1
3. Share the sheet with your service account email (found in Google Sheets credentials JSON)

### 5. LinkedIn API Setup

1. Create a LinkedIn App at https://www.linkedin.com/developers/apps
2. Configure OAuth 2.0 with the following scopes:
   - `w_member_social` (for posting)
   - `r_liteprofile` (for profile access)
3. Get your Person URN (update `PERSON_URN` in `linkedin_publisher.py` if needed)
4. Generate an access token and save it to Kestra KV Store

### 6. Deploy to Kestra

1. Upload the workflow to Kestra:
   ```bash
   kestra flow validate linkedin-content-generator.yml
   kestra flow namespace update company.team linkedin-content-generator.yml
   ```

2. Verify the workflow in Kestra UI at: `http://your-kestra-instance/ui/flows/company.team/linkedin-content-generator`

## 🚀 Usage

### Manual Execution

Run the workflow manually from Kestra UI:
1. Navigate to the workflow
2. Click "Execute"
3. Monitor the execution logs

### Scheduled Execution

The workflow runs automatically:
- **9:00 AM** (Brazil Time) - Morning post
- **2:00 PM** (Brazil Time) - Afternoon post
- **5:00 PM** (Brazil Time) - Evening post (disabled by default)

### Outputs

Each execution generates:
- `linkedin_post.json` - Contains title, content, and image prompt
- `linkedin_image.png` - Generated image (if successful)
- `image_result.json` - Image generation result
- `publish_result.json` - Publishing confirmation

## 🎯 Workflow Steps

1. **Clone Repository** - Pulls latest scripts from GitHub
2. **Setup Environment** - Installs Python dependencies
3. **Generate Content** - AI agent researches and creates post
4. **Generate Image** - Creates visual content (optional, may fail due to safety filters)
5. **Publish to LinkedIn** - Posts content with or without image
6. **Update Tracking** - Adds theme to Google Sheets

## 🔍 Optimization Details

Compared to the original N8N workflow, this implementation:

✅ **Reduces API calls by 60%** - Consolidated 4 AI agents into 1  
✅ **Eliminates redundant image generation attempts**  
✅ **Removes unnecessary wait times**  
✅ **Uses modern LangChain 1.0 `create_agent` API**  
✅ **Implements proper error handling for image generation**  
✅ **Stores code in version control (GitHub)**  

## 🛠️ Troubleshooting

### Image Generation Fails
- This is expected behavior when safety filters are triggered
- The workflow will continue and publish text-only post
- Check `image_result.json` for `finish_reason: NO_IMAGE`

### Google Sheets Not Updating
- Verify service account has edit permissions on the sheet
- Check `GOOGLE_SHEETS_CREDENTIALS` in KV Store
- Ensure sheet ID matches in `sheets_manager.py`

### LinkedIn Publishing Fails
- Verify `LINKEDIN_ACCESS_TOKEN` is valid (tokens expire)
- Check Person URN matches your LinkedIn profile
- Review LinkedIn API quota limits

### Content Quality Issues
- Adjust temperature in `linkedin_agent.py` (default: 0.4)
- Modify system prompts for different tone/style
- Increase/decrease content length limits

## 📝 Customization

### Change Posting Schedule
Edit the `cron` expressions in `linkedin-content-generator.yml`:
```yaml
cron: "0 9 * * *"  # 9 AM daily
```

### Modify Content Style
Edit the `system_prompt` in `scripts/linkedin_agent.py` to change:
- Tone (formal vs. casual)
- Length (word count)
- Topics focus
- Language

### Use Different AI Models
Change the model in `linkedin_agent.py`:
```python
model_name = "gemini-2.0-flash-exp"  # or gemini-pro, gpt-4, etc.
```

## 📊 Monitoring

View execution logs in Kestra UI:
- **Success Rate**: Check execution history
- **Content Quality**: Review generated posts in Google Sheets
- **Image Success Rate**: Monitor `image_result.json` outputs
- **API Quotas**: Watch for rate limiting errors

## 🤝 Contributing

To improve this workflow:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify for your needs!

## 🆘 Support

For issues or questions:
- Email: guifaceads@gmail.com
- WhatsApp: +55 21 97770-9013

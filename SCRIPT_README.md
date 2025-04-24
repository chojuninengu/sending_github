# Cameroon Developer Finder Script

This script helps you find Cameroonian developers on GitHub and gather their information. It uses the GitHub API to search for users with Cameroon-related information in their profiles.

## Prerequisites
 
- Python 3.7 or higher
- GitHub Personal Access Token with appropriate permissions

## Setup

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a GitHub Personal Access Token:

   - Go to https://github.com/settings/tokens
   - Click "Generate new token"
   - Select the following scopes:
     - `read:user`
     - `user:email`
   - Copy the generated token

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file and replace `your_github_token_here` with your actual GitHub token.

## Usage

Run the script:

```bash
python find_cameroon_devs.py
```

The script will:

1. Search for GitHub users with Cameroon-related information
2. Display their:
   - Username
   - Name
   - Location
   - Email (if available)
   - Profile URL

## Important Notes

- The script includes rate limiting to avoid GitHub API restrictions
- Some users may have private email addresses
- Respect GitHub's terms of service and user privacy
- Use the information gathered responsibly

## Limitations

- The GitHub API has rate limits
- Not all users make their email addresses public
- Location data may not be accurate for all users

## Contributing

Feel free to improve this script by:

- Adding more search criteria
- Implementing email notification functionality
- Adding data export capabilities
- Improving error handling

## License

This script is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

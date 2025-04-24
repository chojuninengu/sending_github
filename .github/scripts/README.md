# Cameroon Developer Network - GitHub Actions

This directory contains scripts for the GitHub Actions workflow that automatically invites Cameroonian developers to join the Cameroon Developer Network repository.

## How It Works

The workflow does the following:

1. Runs every 3 days (configurable in the workflow file)
2. Downloads the latest list of Cameroonian developers from the top-github-users repository
3. Extracts developer information from the markdown file
4. Sends invitations to developers who haven't been invited yet
5. Maintains a record of successful invitations to avoid duplicates

## Files

- `invite_cameroon_devs.py`: The main script that extracts developers and sends invitations
- `invite-cameroon-devs.yml`: The GitHub Actions workflow file

## Setup Instructions

1. Make sure your repository exists at `https://github.com/chojuninengu/cameroon-developer-network`

   - If your repository has a different name or is under a different username, update the `REPO_OWNER` and `REPO_NAME` variables in the script

2. Create the necessary directories:

   ```
   mkdir -p .github/workflows
   mkdir -p .github/scripts
   mkdir -p data
   ```

3. Copy the files to their respective locations:

   - Copy `invite_cameroon_devs.py` to `.github/scripts/`
   - Copy `invite-cameroon-devs.yml` to `.github/workflows/`

4. Push the changes to your repository:

   ```
   git add .github/
   git commit -m "Add GitHub Actions workflow for inviting Cameroonian developers"
   git push
   ```

5. The workflow will run automatically every 3 days, or you can trigger it manually from the Actions tab in your repository.

## Customization

You can customize the workflow by:

- Changing the schedule in the workflow file
- Adjusting the delay between invitations in the script
- Modifying the invitation message
- Adding more search criteria for finding developers

## Troubleshooting

If you encounter issues with the workflow:

1. Check the Actions tab in your repository for error messages
2. Make sure your repository has the necessary permissions
3. Verify that the GitHub token has the required scopes
4. Check if the cameroon.md file is being downloaded correctly

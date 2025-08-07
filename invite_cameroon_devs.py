import os
import time
import json
import re
from github import Github, GithubException

# Initialize GitHub client
github_token = os.getenv('GITHUB_TOKEN')
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable not set")
g = Github(github_token)

# Repository details
REPO_OWNER = "chojuninengu"
REPO_NAME = "sending_github"  # Corrected repository name

# Configuration
BATCH_SIZE = 30  # Number of invitations to send in one batch
DELAY_BETWEEN_INVITATIONS = 5  # Seconds to wait between invitations
DELAY_BETWEEN_BATCHES = 3600  # Seconds to wait between batches (1 hour)

def extract_developers_from_md():
    """
    Extract developer information from data/cameroon.md
    """
    filename = 'data/cameroon.md'  # Corrected file path
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return []
        
    developers = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all developer entries in the markdown table
        pattern = r'<tr>\s*<td>\d+</td>\s*<td>\s*<a href="https://github.com/([^"]+)">.*?</a><br/>\s*([^<]+)\s*</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>(\d+)</td>\s*</tr>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        print(f"Found {len(matches)} developers in the markdown file")
        
        for match in matches:
            username, name, company, twitter, location, contributions = match
            
            # Clean up the data
            name = name.strip()
            company = company.strip()
            twitter = twitter.strip()
            location = location.strip()
            
            # Skip entries with "No Twitter Username"
            if twitter == "No Twitter Username":
                twitter = None
                
            developer = {
                'username': username,
                'name': name,
                'company': company,
                'twitter': twitter,
                'location': location,
                'contributions': int(contributions),
                'invited': False,
                'invitation_date': None,
                'invitation_error': None
            }
            
            developers.append(developer)
            
    except Exception as e:
        print(f"Error extracting developers from {filename}: {str(e)}")
        raise
        
    return developers

def save_developers(developers):
    """
    Save developer information to a JSON file
    """
    filename = 'data/cameroon_developers.json'  # Save in data/ directory
    os.makedirs('data', exist_ok=True)  # Ensure data/ directory exists
    
    # Load existing data if file exists
    existing_data = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    
    # Merge new developers with existing ones
    for dev in developers:
        if not any(existing['username'] == dev['username'] for existing in existing_data):
            existing_data.append(dev)
    
    # Save updated data
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"Saved {len(existing_data)} developers to {filename}")

def send_invitations_in_batches():
    """
    Send invitations to join the repository to developers who haven't been invited yet,
    processing in batches to respect GitHub's rate limits
    """
    try:
        # Get the repository
        repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
        print(f"Successfully accessed repository: {REPO_OWNER}/{REPO_NAME}")
        
        # Load existing data
        filename = 'data/cameroon_developers.json'
        if not os.path.exists(filename):
            print("No developers found. Run the extraction first.")
            return
            
        with open(filename, 'r') as f:
            developers = json.load(f)
            
        # Filter developers who haven't been invited yet
        developers_to_invite = [dev for dev in developers if not dev.get('invited', False)]
        
        if not developers_to_invite:
            print("All developers have already been invited.")
            return
            
        print(f"Found {len(developers_to_invite)} developers to invite")
        
        # Process in batches
        total_invited = 0
        batch_count = 0
        
        for i in range(0, len(developers_to_invite), BATCH_SIZE):
            batch = developers_to_invite[i:i+BATCH_SIZE]
            batch_count += 1
            
            print(f"\nProcessing batch {batch_count} ({len(batch)} developers)...")
            
            # Process each developer in the batch
            for dev in batch:
                try:
                    # Skip if already invited
                    if dev.get('invited', False):
                        continue
                        
                    # Create a personalized message
                    message = f"""Hi {dev['name'] or dev['username']},

I noticed you're a developer from Cameroon and wanted to invite you to join the Cameroon Developer Network on GitHub.

This is a community-driven initiative to connect, support, and empower Cameroonian developers worldwide. Whether you're a beginner, intermediate, or professional developer, this is your space to grow, collaborate, and contribute to the tech ecosystem in Cameroon.

Repository: https://github.com/{REPO_OWNER}/{REPO_NAME}

Let's build something meaningful together!

Best regards,
The Cameroon Developer Network Team
"""
                    
                    # Send invitation
                    repo.add_to_collaborators(dev['username'], permission='push')
                    
                    # Update the developer's information
                    dev['invited'] = True
                    dev['invitation_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    dev['invitation_error'] = None
                    
                    print(f"Invitation sent to {dev['username']}")
                    total_invited += 1
                    
                    # Add a delay to avoid rate limiting
                    time.sleep(DELAY_BETWEEN_INVITATIONS)
                    
                except GithubException as e:
                    error_message = str(e)
                    print(f"Error sending invitation to {dev['username']}: {error_message}")
                    dev['invitation_error'] = error_message
                    
                    # If we hit a rate limit, pause for a while
                    if e.status == 403 and "rate limit" in error_message.lower():
                        print("Rate limit detected. Pausing for 5 minutes...")
                        time.sleep(300)  # Wait 5 minutes
                    elif e.status == 403:
                        print("Permission error. Check if ORG_ADMIN_TOKEN has admin:org scope.")
                        raise  # Fail the workflow to diagnose permission issues
                    elif e.status == 404:
                        print(f"User {dev['username']} not found or repository inaccessible.")
                        continue
                    
                    continue
                    
            # Save progress after each batch
            with open(filename, 'w') as f:
                json.dump(developers, f, indent=2)
                
            print(f"Batch {batch_count} completed. {total_invited} invitations sent so far.")
            
            # If there are more batches to process, wait before continuing
            if i + BATCH_SIZE < len(developers_to_invite):
                print(f"Waiting {DELAY_BETWEEN_BATCHES/60} minutes before processing the next batch...")
                time.sleep(DELAY_BETWEEN_BATCHES)
                
        print(f"\nInvitation process completed! Total invitations sent: {total_invited}")
        
    except GithubException as e:
        print(f"Error accessing repository or sending invitations: {str(e)}")
        raise

def main():
    """
    Main function to run the script
    """
    print("Extracting Cameroonian developers from data/cameroon.md...")
    developers = extract_developers_from_md()
    
    if developers:
        print(f"Found {len(developers)} Cameroonian developers")
        save_developers(developers)
        print("\nSending invitations in batches to respect GitHub's rate limits...")
        send_invitations_in_batches()
        print("\nInvitation process completed!")
    else:
        print("No developers found in the markdown file.")

if __name__ == "__main__":
    main()

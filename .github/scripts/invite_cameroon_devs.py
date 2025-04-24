#!/usr/bin/env python3
"""
GitHub Actions script to invite Cameroonian developers to join a GitHub organization.
This script is designed to run in a GitHub Actions workflow.
"""

import os
import time
import json
import re
from github import Github

# Organization details
ORG_NAME = "cameroon-developers"  # Your GitHub organization name
ROLE = "member"  # Role to assign: member, admin, or billing_manager

# Configuration
BATCH_SIZE = 30  # Number of invitations to send in one batch
DELAY_BETWEEN_INVITATIONS = 5  # Seconds to wait between invitations

def extract_developers_from_md():
    """
    Extract developer information from the cameroon.md file
    """
    filename = 'data/cameroon.md'
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
        
    return developers

def load_invitation_records():
    """
    Load existing invitation records
    """
    filename = 'data/invitation_records.json'
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_invitation_records(records):
    """
    Save invitation records
    """
    filename = 'data/invitation_records.json'
    with open(filename, 'w') as f:
        json.dump(records, f, indent=2)

def send_organization_invitations():
    """
    Send invitations to join the GitHub organization to developers who haven't been invited yet
    """
    try:
        # Initialize GitHub client
        github_token = os.environ.get('GITHUB_TOKEN')
        g = Github(github_token)
        
        # Get the organization
        org = g.get_organization(ORG_NAME)
        
        # Load existing invitation records
        invitation_records = load_invitation_records()
        
        # Extract developers from the markdown file
        developers = extract_developers_from_md()
        
        if not developers:
            print("No developers found in the markdown file.")
            return
            
        print(f"Found {len(developers)} Cameroonian developers")
        
        # Track how many invitations were sent
        total_invited = 0
        
        # Process each developer
        for dev in developers:
            username = dev['username']
            
            # Skip if already invited
            if username in invitation_records and invitation_records[username].get('invited', False):
                print(f"Skipping {username} - already invited")
                continue
                
            try:
                # Create a personalized message
                message = f"""Hi {dev['name'] or dev['username']},

I noticed you're a developer from Cameroon and wanted to invite you to join the Cameroon Developers organization on GitHub.

This is a community-driven initiative to connect, support, and empower Cameroonian developers worldwide. Whether you're a beginner, intermediate, or professional developer, this is your space to grow, collaborate, and contribute to the tech ecosystem in Cameroon.

Organization: https://github.com/{ORG_NAME}

Let's build something meaningful together!

Best regards,
The Cameroon Developers Team
"""
                
                # Send organization invitation
                org.invite_user(username, role=ROLE)
                
                # Update the invitation record
                invitation_records[username] = {
                    'name': dev['name'],
                    'location': dev['location'],
                    'invited': True,
                    'invitation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'invitation_error': None
                }
                
                print(f"Organization invitation sent to {username}")
                total_invited += 1
                
                # Add a delay to avoid rate limiting
                time.sleep(DELAY_BETWEEN_INVITATIONS)
                
            except Exception as e:
                error_message = str(e)
                print(f"Error sending invitation to {username}: {error_message}")
                
                # Update the invitation record with the error
                invitation_records[username] = {
                    'name': dev['name'],
                    'location': dev['location'],
                    'invited': False,
                    'invitation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'invitation_error': error_message
                }
                
                # If we hit a rate limit, stop processing
                if "rate_limit" in error_message.lower():
                    print("Rate limit detected. Stopping invitation process.")
                    break
                
                continue
                
        # Save updated invitation records
        save_invitation_records(invitation_records)
            
        print(f"\nInvitation process completed! Total invitations sent: {total_invited}")
        
    except Exception as e:
        print(f"Error sending invitations: {str(e)}")

if __name__ == "__main__":
    print("Starting organization invitation process for Cameroonian developers...")
    send_organization_invitations()
    print("Invitation process completed!") 
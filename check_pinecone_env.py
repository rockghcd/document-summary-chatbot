"""
Script to help find Pinecone environment
"""

import requests
import json

def check_pinecone_environment(api_key):
    """Check Pinecone environment using the API key"""
    
    # Remove the 'pcsk_' prefix if present
    if api_key.startswith('pcsk_'):
        api_key = api_key[5:]
    
    # Try to get environment info
    try:
        # Make a request to Pinecone API to get environment info
        headers = {
            'Api-Key': f'pcsk_{api_key}'
        }
        
        # Try different common environments
        environments = [
            'us-east-1-aws',
            'us-west-1-gcp', 
            'eu-west-1-aws',
            'ap-southeast-1-aws',
            'us-central1-gcp',
            'us-east1-gcp'
        ]
        
        print("🔍 Checking common Pinecone environments...")
        
        for env in environments:
            try:
                url = f"https://controller.{env}.pinecone.io/databases"
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ Found working environment: {env}")
                    return env
                elif response.status_code == 401:
                    print(f"❌ Unauthorized for {env} - wrong environment")
                else:
                    print(f"⚠️ Status {response.status_code} for {env}")
                    
            except Exception as e:
                print(f"❌ Error checking {env}: {str(e)}")
        
        print("\n❌ Could not determine environment automatically.")
        print("Please check your Pinecone dashboard manually.")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Your API key (replace with your actual key)
    api_key = "6ut6Xp_P4Gw7rdKkv69BHpd2SSVn5te8frcT5L6qxUpBRHX844KVUJS5MUtxL3gmTAsrSB"
    
    print("🔍 Checking Pinecone environment...")
    environment = check_pinecone_environment(api_key)
    
    if environment:
        print(f"\n✅ Your Pinecone environment is: {environment}")
        print(f"\n📝 Add this to your .env file:")
        print(f"PINECONE_ENVIRONMENT={environment}")
    else:
        print("\n❌ Could not determine environment automatically.")
        print("Please check your Pinecone dashboard at https://app.pinecone.io/")
        print("Look for the environment name in the top navigation bar.") 
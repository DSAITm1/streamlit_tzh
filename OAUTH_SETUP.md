# Google OAuth Setup for Olist Dashboard

This document explains how to configure Google OAuth authentication for the Olist Analytics Dashboard.

## Overview

The dashboard now supports two authentication methods:
1. **Google OAuth 2.0** - User authentication with personal Google accounts
2. **Service Account** - Application-level authentication (existing method)

OAuth authentication provides better security and user-specific access control.

## Setting up Google OAuth

### 1. Create OAuth 2.0 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client IDs**
5. Configure the OAuth consent screen if prompted
6. Set application type to **Web application**
7. Add authorized redirect URIs:
   - For local development: `http://localhost:8501`
   - For production: Your Streamlit app URL

### 2. Enable Required APIs

Make sure these APIs are enabled in your Google Cloud project:
- BigQuery API
- Cloud Resource Manager API
- Google+ API (for user profile info)

### 3. Configure Environment Variables

Set the following environment variables:

```bash
# OAuth Configuration
export GOOGLE_OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"

# Optional: BigQuery Project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### 4. Streamlit Secrets Configuration

Alternatively, configure OAuth in Streamlit secrets (`~/.streamlit/secrets.toml`):

```toml
[oauth]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"

[bigquery]
project_id = "your-project-id"
```

## Using OAuth Authentication

### 1. Start the Application

```bash
streamlit run main.py
```

### 2. Authenticate

1. In the sidebar, you'll see the Authentication section
2. Click **"Login with Google"**
3. You'll be redirected to Google's authentication page
4. Grant necessary permissions for BigQuery access
5. Copy the authorization code from the redirect URL
6. Paste it back in the application and click **"Complete Authentication"**

### 3. Access Control

Users need appropriate BigQuery permissions in your Google Cloud project:
- `BigQuery Data Viewer` - To read data
- `BigQuery Job User` - To run queries
- Project-level or dataset-level access as needed

## Fallback Authentication

If OAuth is not configured, the application automatically falls back to service account authentication using:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable
2. Streamlit secrets `gcp_service_account`
3. Local service account file `dsai-468212-f4762cc666a5.json`

## Troubleshooting

### Common Issues

1. **"OAuth not configured"**
   - Ensure `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set
   - Check Streamlit secrets configuration

2. **"Invalid authorization code"**
   - Make sure to copy the complete authorization code
   - Check that redirect URI matches the configured URI

3. **"Access denied to BigQuery"**
   - Verify the user has appropriate BigQuery permissions
   - Check that BigQuery API is enabled

4. **"Token expired"**
   - The application automatically refreshes tokens
   - If issues persist, logout and login again

### Security Considerations

- OAuth tokens are stored in Streamlit session state (memory only)
- Tokens are automatically refreshed when expired
- Use HTTPS in production environments
- Regularly review OAuth consent screen and permissions

## Development vs Production

### Development
- Use `http://localhost:8501` as redirect URI
- OAuth credentials can be in environment variables or secrets file

### Production (Streamlit Cloud)
- Set OAuth credentials in Streamlit Cloud secrets
- Use your production URL as redirect URI
- Enable HTTPS for secure token exchange

## Migration from Service Account

Existing installations continue to work with service account authentication. OAuth is an additional option that can be enabled without disrupting existing setups.

To migrate users to OAuth:
1. Set up OAuth credentials as described above
2. Users can choose to authenticate via OAuth for better security
3. Service account authentication remains available as fallback
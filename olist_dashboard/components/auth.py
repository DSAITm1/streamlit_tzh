"""
Authentication component for Google OAuth integration.
"""

import streamlit as st
from typing import Optional, Dict, Any
import webbrowser
from urllib.parse import urlparse, parse_qs

from ..config.settings import init_oauth_flow, get_oauth_credentials, OAUTH_CONFIG


def render_auth_section() -> Dict[str, Any]:
    """
    Render authentication section in sidebar.
    
    Returns:
        Dictionary containing authentication status and user info
    """
    st.subheader("🔐 Authentication")
    
    # Check if user is authenticated
    oauth_creds = get_oauth_credentials()
    is_authenticated = oauth_creds is not None
    
    if is_authenticated:
        return render_authenticated_user(oauth_creds)
    else:
        return render_login_options()


def render_authenticated_user(credentials) -> Dict[str, Any]:
    """
    Render UI for authenticated user.
    
    Args:
        credentials: OAuth credentials object
        
    Returns:
        Authentication status dictionary
    """
    # Get user info from session state if available
    user_info = st.session_state.get("user_info", {})
    user_email = user_info.get("email", "Unknown User")
    
    st.success(f"✅ Logged in as {user_email}")
    
    # Authentication method indicator
    st.info("🔑 Using OAuth authentication")
    
    # Logout button
    if st.button("🚪 Logout", help="Sign out and clear authentication"):
        logout_user()
        st.rerun()
    
    # Show token status
    with st.expander("Token Status"):
        if credentials.valid:
            st.success("✅ Token is valid")
        else:
            st.warning("⚠️ Token needs refresh")
        
        if hasattr(credentials, 'expiry') and credentials.expiry:
            st.info(f"Expires: {credentials.expiry}")
    
    return {
        "is_authenticated": True,
        "auth_method": "oauth",
        "user_email": user_email,
        "credentials": credentials
    }


def render_login_options() -> Dict[str, Any]:
    """
    Render login options for unauthenticated user.
    
    Returns:
        Authentication status dictionary
    """
    # Check if OAuth is configured
    flow = init_oauth_flow()
    oauth_configured = flow is not None
    
    if oauth_configured:
        st.info("🔑 OAuth authentication available")
        
        # Login button
        if st.button("🔐 Login with Google", help="Authenticate using your Google account"):
            start_oauth_flow()
        
        # Instructions
        with st.expander("How to authenticate"):
            st.markdown("""
            1. Click 'Login with Google' above
            2. You'll be redirected to Google's login page
            3. Grant permissions for BigQuery access
            4. Copy the authorization code back here
            """)
        
        # Check for authorization code in URL parameters
        check_oauth_callback()
        
    else:
        st.warning("⚠️ OAuth not configured")
        st.info("💡 Using service account authentication")
        
        with st.expander("OAuth Setup"):
            st.markdown("""
            To enable OAuth authentication, configure:
            
            **Environment Variables:**
            - `GOOGLE_OAUTH_CLIENT_ID`
            - `GOOGLE_OAUTH_CLIENT_SECRET`
            
            **Or Streamlit Secrets:**
            ```toml
            [oauth]
            client_id = "your-client-id"
            client_secret = "your-client-secret"
            ```
            """)
    
    return {
        "is_authenticated": False,
        "auth_method": "service_account",
        "oauth_configured": oauth_configured
    }


def start_oauth_flow():
    """Start the OAuth authentication flow."""
    try:
        flow = init_oauth_flow()
        if not flow:
            st.error("OAuth not configured properly")
            return
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        # Store flow state in session
        st.session_state["oauth_flow"] = flow
        
        # Display instructions
        st.info("🌐 Opening authentication page...")
        st.markdown(f"**[Click here to authenticate]({auth_url})**")
        
        # Show manual instructions
        st.markdown("""
        After authenticating:
        1. Copy the authorization code from the URL
        2. Paste it in the field below
        """)
        
        # Authorization code input
        auth_code = st.text_input(
            "Authorization Code:",
            help="Paste the authorization code from Google here"
        )
        
        if auth_code and st.button("Complete Authentication"):
            complete_oauth_flow(auth_code)
        
    except Exception as e:
        st.error(f"Failed to start OAuth flow: {str(e)}")


def complete_oauth_flow(auth_code: str):
    """
    Complete the OAuth flow with authorization code.
    
    Args:
        auth_code: Authorization code from Google
    """
    try:
        # Get flow from session state
        flow = st.session_state.get("oauth_flow")
        if not flow:
            st.error("OAuth flow not found. Please restart authentication.")
            return
        
        # Exchange authorization code for credentials
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Store credentials in session state
        st.session_state["oauth_credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        # Get user info if possible
        try:
            from google.oauth2.credentials import Credentials
            import requests
            
            # Call Google's userinfo API to get email
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {credentials.token}"}
            response = requests.get(userinfo_url, headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                st.session_state["user_info"] = user_info
            
        except Exception as e:
            st.warning(f"Could not retrieve user info: {str(e)}")
        
        # Clean up flow from session
        if "oauth_flow" in st.session_state:
            del st.session_state["oauth_flow"]
        
        st.success("✅ Authentication successful!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")


def check_oauth_callback():
    """Check for OAuth callback parameters in URL."""
    try:
        # This is a simplified version - in a real app you'd handle the full OAuth callback
        # For Streamlit apps, we use the manual authorization code flow
        pass
    except Exception:
        pass


def logout_user():
    """Logout current user and clear session state."""
    # Clear OAuth credentials
    if "oauth_credentials" in st.session_state:
        del st.session_state["oauth_credentials"]
    
    # Clear user info
    if "user_info" in st.session_state:
        del st.session_state["user_info"]
    
    # Clear OAuth flow
    if "oauth_flow" in st.session_state:
        del st.session_state["oauth_flow"]
    
    # Clear any cached data that might be user-specific
    st.cache_data.clear()
    
    st.success("✅ Logged out successfully")


def get_auth_status() -> Dict[str, Any]:
    """
    Get current authentication status.
    
    Returns:
        Dictionary with authentication information
    """
    oauth_creds = get_oauth_credentials()
    
    if oauth_creds and oauth_creds.valid:
        user_info = st.session_state.get("user_info", {})
        return {
            "is_authenticated": True,
            "auth_method": "oauth",
            "user_email": user_info.get("email", "Unknown"),
            "credentials": oauth_creds
        }
    else:
        # Check for service account credentials
        from ..config.settings import get_bigquery_credentials
        service_creds = get_bigquery_credentials()
        
        return {
            "is_authenticated": service_creds is not None,
            "auth_method": "service_account" if service_creds else "none",
            "user_email": None,
            "credentials": service_creds
        }
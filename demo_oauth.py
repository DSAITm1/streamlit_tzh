"""
Simple demo to show OAuth authentication UI without running the full app.
"""
import streamlit as st

# Mock the UI components to demonstrate the authentication interface
st.set_page_config(
    page_title="Olist Analytics Dashboard - OAuth Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("📊 Olist Analytics Dashboard")
st.markdown("### OAuth Authentication Demo")

with st.sidebar:
    st.title("📊 Olist Analytics")
    st.markdown("---")
    
    # Authentication Section
    st.subheader("🔐 Authentication")
    
    # Show OAuth not configured state
    st.warning("⚠️ OAuth not configured")
    st.info("💡 Using service account authentication")
    
    if st.button("🔐 Login with Google", disabled=True):
        st.info("OAuth would start here")
    
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
    
    st.markdown("---")
    
    # Show what authenticated state would look like
    st.subheader("🔐 When Authenticated:")
    st.success("✅ Logged in as user@example.com")
    st.info("🔑 Using OAuth authentication")
    
    if st.button("🚪 Logout", disabled=True):
        st.info("Would logout here")
    
    with st.expander("Token Status"):
        st.success("✅ Token is valid")
        st.info("Expires: 2024-12-31 23:59:59")
    
    st.markdown("---")
    
    # Data Status
    st.subheader("📡 Data Status")
    st.success("🔐 OAuth Authentication")
    st.caption("User: user@example.com")
    st.success("✅ Connected to BigQuery")
    st.info("🕐 Last updated: 14:30")

# Main content area
st.info("🔐 Authentication Required")
st.markdown("Please authenticate using the sidebar to access BigQuery data.")

st.markdown("---")
st.subheader("Demo Mode")
st.info("You can view the dashboard with sample data while authentication is set up.")

if st.button("🎭 View with Sample Data"):
    st.success("✅ Sample data mode enabled!")

# Show features
st.markdown("---")
st.subheader("🆕 New OAuth Authentication Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **✅ Added Features:**
    - Google OAuth 2.0 authentication
    - User-specific access control
    - Automatic token refresh
    - Secure session management
    - Fallback to service account auth
    """)

with col2:
    st.markdown("""
    **🔧 Configuration Options:**
    - Environment variables
    - Streamlit secrets
    - Multiple authentication methods
    - Easy setup documentation
    - Backward compatibility
    """)

st.markdown("---")
st.markdown("### 📚 Documentation")
st.markdown("""
- **[OAuth Setup Guide](OAUTH_SETUP.md)** - Complete OAuth configuration instructions
- **[README.md](README.md)** - Updated with authentication options
- **Authentication Types:** OAuth 2.0 (recommended) or Service Account (existing)
""")
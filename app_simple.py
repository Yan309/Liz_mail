"""Simplified Streamlit web application - no RabbitMQ required."""
import streamlit as st
import os
import tempfile
import pandas as pd
from pathlib import Path
import time
from config import Config
from cv_parser import CVParser
from email_sender import EmailSender, EmailTemplates
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Lizmail - Automated Email System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'extracted_emails' not in st.session_state:
        st.session_state.extracted_emails = []


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary directory."""
    try:
        upload_dir = Path(Config.UPLOAD_FOLDER)
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


def send_emails_sync(email_list, progress_bar, status_text):
    """Send emails synchronously with progress updates."""
    sender = EmailSender()
    total = len(email_list)
    sent = 0
    failed = 0
    
    for idx, email_data in enumerate(email_list, 1):
        try:
            status_text.text(f"Sending email {idx}/{total} to {email_data.get('to', 'unknown')}")
            success = sender.send_email(email_data)
            
            if success:
                sent += 1
            else:
                failed += 1
            
            progress_bar.progress(idx / total)
            time.sleep(Config.PROCESSING_DELAY)
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            failed += 1
    
    return sent, failed


def main():
    """Main application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📧 Lizmail - Automated Email System</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # SMTP Configuration
        with st.expander("📮 SMTP Settings", expanded=False):
            smtp_configured = bool(Config.SMTP_USER and Config.SMTP_PASSWORD)
            if smtp_configured:
                st.success("✅ SMTP Configured")
                st.info(f"Email: {Config.SMTP_USER}")
                
                if st.button("Test SMTP Connection"):
                    with st.spinner("Testing connection..."):
                        sender = EmailSender()
                        if sender.test_connection():
                            st.success("✅ Connection successful!")
                        else:
                            st.error("❌ Connection failed. Check .env file")
            else:
                st.error("❌ SMTP not configured")
                st.info("Configure SMTP in .env file")
        
        st.markdown("---")
        
        # Statistics
        st.header("📊 Statistics")
        if st.session_state.extracted_emails:
            st.metric("Emails Extracted", len(st.session_state.extracted_emails))
        else:
            st.metric("Emails Extracted", 0)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Upload & Extract",
        "✉️ Screening Email",
        "❌ Rejection Email",
        "📋 Custom Email"
    ])
    
    # Tab 1: Upload and Extract
    with tab1:
        st.header("📁 Upload CVs and Extract Emails")
        st.info("Upload PDF, Word documents, or ZIP files containing CVs. The system will automatically extract email addresses.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Upload CV files (PDF, DOC, DOCX, ZIP)",
                type=['pdf', 'doc', 'docx', 'zip'],
                accept_multiple_files=True,
                help="You can upload multiple files or a ZIP containing multiple CVs"
            )
        
        with col2:
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        if st.button("🔍 Extract Emails", type="primary", disabled=not uploaded_files):
            if uploaded_files:
                with st.spinner("Processing files and extracting emails..."):
                    all_emails = set()
                    results_data = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing: {uploaded_file.name}")
                        
                        file_path = save_uploaded_file(uploaded_file)
                        
                        if file_path:
                            emails = CVParser.process_file(file_path)
                            all_emails.update(emails)
                            
                            results_data.append({
                                'File': uploaded_file.name,
                                'Emails Found': len(emails),
                                'Emails': ', '.join(emails) if emails else 'None'
                            })
                            
                            try:
                                os.remove(file_path)
                            except:
                                pass
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.session_state.extracted_emails = list(all_emails)
                    
                    st.success(f"✅ Extraction complete! Found {len(all_emails)} unique email(s)")
                    
                    if results_data:
                        st.subheader("📊 Extraction Results")
                        df = pd.DataFrame(results_data)
                        st.dataframe(df, use_container_width=True)
                    
                    if st.session_state.extracted_emails:
                        st.subheader("📧 Extracted Email Addresses")
                        email_df = pd.DataFrame({
                            'Email': st.session_state.extracted_emails
                        })
                        st.dataframe(email_df, use_container_width=True)
                        
                        csv = email_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Email List (CSV)",
                            data=csv,
                            file_name="extracted_emails.csv",
                            mime="text/csv"
                        )
        
        # Manual Email Entry Section
        st.markdown("---")
        st.subheader("✍️ Manually Add Email Addresses")
        st.info("Add emails manually if extraction failed or you want to include additional recipients.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            manual_email_input = st.text_area(
                "Enter email addresses (one per line or comma-separated)",
                placeholder="john.doe@example.com\njane.smith@example.com\nor: email1@test.com, email2@test.com",
                height=100,
                key="manual_emails"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("➕ Add Emails", type="secondary"):
                if manual_email_input:
                    # Parse emails from input
                    import re
                    # Split by newlines and commas
                    raw_emails = re.split(r'[,\n]+', manual_email_input)
                    
                    # Clean and validate emails
                    valid_emails = []
                    invalid_emails = []
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    
                    for email in raw_emails:
                        email = email.strip()
                        if email:
                            if re.match(email_pattern, email):
                                valid_emails.append(email.lower())
                            else:
                                invalid_emails.append(email)
                    
                    # Add to session state (avoid duplicates)
                    if valid_emails:
                        initial_count = len(st.session_state.extracted_emails)
                        st.session_state.extracted_emails.extend(valid_emails)
                        st.session_state.extracted_emails = list(set(st.session_state.extracted_emails))
                        added_count = len(st.session_state.extracted_emails) - initial_count
                        
                        st.success(f"✅ Added {added_count} new email(s)! Total: {len(st.session_state.extracted_emails)}")
                    
                    if invalid_emails:
                        st.warning(f"⚠️ Invalid email(s) skipped: {', '.join(invalid_emails)}")
                else:
                    st.warning("⚠️ Please enter at least one email address")
        
        # Show current email list if exists
        if st.session_state.extracted_emails:
            with st.expander("📋 View All Email Addresses", expanded=False):
                email_list_df = pd.DataFrame({
                    'Email': st.session_state.extracted_emails
                })
                st.dataframe(email_list_df, use_container_width=True)
                
                # Option to remove individual emails
                st.write("**Remove Emails:**")
                emails_to_remove = st.multiselect(
                    "Select email(s) to remove",
                    st.session_state.extracted_emails,
                    key="remove_emails"
                )
                
                if st.button("🗑️ Remove Selected", key="remove_btn"):
                    if emails_to_remove:
                        for email in emails_to_remove:
                            st.session_state.extracted_emails.remove(email)
                        st.success(f"✅ Removed {len(emails_to_remove)} email(s)")
                        st.rerun()
    
    # Tab 2: Screening Email
    with tab2:
        st.header("✉️ Send Screening Email")
        st.info("Send initial screening emails to candidates with custom questions.")
        
        if not st.session_state.extracted_emails:
            st.warning("⚠️ No emails extracted yet. Please upload CVs in the 'Upload & Extract' tab first.")
        else:
            with st.form("screening_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    company_name = st.text_input("Company Name *", placeholder="e.g., Tech Corp")
                    position = st.text_input("Position *", placeholder="e.g., Senior Developer")
                    hr_name = st.text_input("HR Name *", placeholder="e.g., John Smith")
                
                with col2:
                    candidate_name = st.text_input("Candidate Name", placeholder="e.g., Candidate or leave blank")
                    from_name = st.text_input("From Name (Optional)", placeholder="e.g., HR Team")
                
                st.subheader("❓ Screening Questions")
                num_questions = st.number_input("Number of questions", min_value=0, max_value=10, value=3)
                
                questions = []
                for i in range(num_questions):
                    q = st.text_input(f"Question {i+1}", key=f"q_{i}", 
                                     placeholder=f"Enter question {i+1}")
                    if q:
                        questions.append(q)
                
                additional_info = st.text_area("Additional Information (Optional)", 
                                              placeholder="Any additional details...")
                
                st.subheader("📧 Select Recipients")
                selected_emails = st.multiselect(
                    "Choose email addresses",
                    st.session_state.extracted_emails,
                    default=st.session_state.extracted_emails
                )
                
                submit_screening = st.form_submit_button("📤 Send Screening Emails", type="primary")
                
                if submit_screening:
                    if not all([company_name, position, hr_name]):
                        st.error("❌ Please fill in all required fields")
                    elif not selected_emails:
                        st.error("❌ Please select at least one recipient")
                    else:
                        email_tasks = []
                        for email in selected_emails:
                            template = EmailTemplates.screening_email(
                                candidate_name=candidate_name or "Candidate",
                                position=position,
                                company_name=company_name,
                                hr_name=hr_name,
                                questions=questions,
                                additional_info=additional_info
                            )
                            
                            email_tasks.append({
                                'to': email,
                                'subject': template['subject'],
                                'body': template['body'],
                                'from_name': from_name
                            })
                        
                        # Send emails with progress tracking
                        with st.spinner("Sending emails..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            sent, failed = send_emails_sync(email_tasks, progress_bar, status_text)
                            
                            progress_bar.empty()
                            status_text.empty()
                        
                        # Show results
                        if failed == 0:
                            st.success(f"✅ Successfully sent {sent} email(s)!")
                        else:
                            st.warning(f"⚠️ Sent {sent} email(s), {failed} failed")
                            st.info("💡 Check your SMTP settings if emails are failing")
    
    # Tab 3: Rejection Email
    with tab3:
        st.header("❌ Send Rejection Email")
        st.info("Send rejection emails to candidates professionally.")
        
        if not st.session_state.extracted_emails:
            st.warning("⚠️ No emails extracted yet. Please upload CVs in the 'Upload & Extract' tab first.")
        else:
            with st.form("rejection_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    company_name_rej = st.text_input("Company Name *", placeholder="e.g., Tech Corp", key="rej_company")
                    position_rej = st.text_input("Position *", placeholder="e.g., Senior Developer", key="rej_position")
                
                with col2:
                    hr_name_rej = st.text_input("HR Name *", placeholder="e.g., John Smith", key="rej_hr")
                    candidate_name_rej = st.text_input("Candidate Name", placeholder="e.g., Candidate", key="rej_candidate")
                    from_name_rej = st.text_input("From Name (Optional)", placeholder="e.g., HR Team", key="rej_from")
                
                additional_message = st.text_area("Additional Message (Optional)", 
                                                 placeholder="Any encouraging words...",
                                                 key="rej_msg")
                
                st.subheader("📧 Select Recipients")
                selected_emails_rej = st.multiselect(
                    "Choose email addresses",
                    st.session_state.extracted_emails,
                    key="rej_emails"
                )
                
                submit_rejection = st.form_submit_button("📤 Send Rejection Emails", type="primary")
                
                if submit_rejection:
                    if not all([company_name_rej, position_rej, hr_name_rej]):
                        st.error("❌ Please fill in all required fields")
                    elif not selected_emails_rej:
                        st.error("❌ Please select at least one recipient")
                    else:
                        email_tasks = []
                        for email in selected_emails_rej:
                            template = EmailTemplates.rejection_email(
                                candidate_name=candidate_name_rej or "Candidate",
                                position=position_rej,
                                company_name=company_name_rej,
                                hr_name=hr_name_rej,
                                additional_message=additional_message
                            )
                            
                            email_tasks.append({
                                'to': email,
                                'subject': template['subject'],
                                'body': template['body'],
                                'from_name': from_name_rej
                            })
                        
                        # Send emails with progress tracking
                        with st.spinner("Sending emails..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            sent, failed = send_emails_sync(email_tasks, progress_bar, status_text)
                            
                            progress_bar.empty()
                            status_text.empty()
                        
                        # Show results
                        if failed == 0:
                            st.success(f"✅ Successfully sent {sent} email(s)!")
                        else:
                            st.warning(f"⚠️ Sent {sent} email(s), {failed} failed")
                            st.info("💡 Check your SMTP settings if emails are failing")
    
    # Tab 4: Custom Email
    with tab4:
        st.header("📋 Send Custom Email")
        st.info("Create custom emails with variables: {candidate_name}, {position}, {company_name}, {hr_name}")
        
        if not st.session_state.extracted_emails:
            st.warning("⚠️ No emails extracted yet.")
        else:
            with st.form("custom_form"):
                subject_custom = st.text_input("Email Subject *", placeholder="e.g., Opportunity at {company_name}")
                
                body_custom = st.text_area("Email Body *", height=300,
                    placeholder="""Dear {candidate_name},

We are reaching out regarding {position}...

Best regards,
{hr_name}
{company_name}""")
                
                col1, col2 = st.columns(2)
                with col1:
                    var_candidate = st.text_input("candidate_name", placeholder="John Doe", key="custom_candidate")
                    var_position = st.text_input("position", placeholder="Developer", key="custom_position")
                
                with col2:
                    var_company = st.text_input("company_name", placeholder="Tech Corp", key="custom_company")
                    var_hr = st.text_input("hr_name", placeholder="HR Manager", key="custom_hr")
                
                from_name_custom = st.text_input("From Name (Optional)", key="custom_from")
                
                st.subheader("📧 Select Recipients")
                selected_emails_custom = st.multiselect(
                    "Choose email addresses",
                    st.session_state.extracted_emails,
                    key="custom_emails"
                )
                
                submit_custom = st.form_submit_button("📤 Send Custom Emails", type="primary")
                
                if submit_custom:
                    if not all([subject_custom, body_custom]):
                        st.error("❌ Please fill in subject and body")
                    elif not selected_emails_custom:
                        st.error("❌ Please select at least one recipient")
                    else:
                        variables = {
                            'candidate_name': var_candidate,
                            'position': var_position,
                            'company_name': var_company,
                            'hr_name': var_hr
                        }
                        
                        email_tasks = []
                        for email in selected_emails_custom:
                            template = EmailTemplates.custom_email(
                                subject=subject_custom,
                                body=body_custom,
                                variables=variables
                            )
                            
                            email_tasks.append({
                                'to': email,
                                'subject': template['subject'],
                                'body': template['body'],
                                'from_name': from_name_custom
                            })
                        
                        # Send emails with progress tracking
                        with st.spinner("Sending emails..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            sent, failed = send_emails_sync(email_tasks, progress_bar, status_text)
                            
                            progress_bar.empty()
                            status_text.empty()
                        
                        # Show results
                        if failed == 0:
                            st.success(f"✅ Successfully sent {sent} email(s)!")
                        else:
                            st.warning(f"⚠️ Sent {sent} email(s), {failed} failed")
                            st.info("💡 Check your SMTP settings if emails are failing")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>📧 Lizmail - Automated Email System | Built with Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

"""Streamlit web application for automated email system."""
import streamlit as st
import os
import tempfile
import pandas as pd
from pathlib import Path
import time
from config import Config
from cv_parser import CVParser
from queue_manager import EmailQueueProducer
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
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'extracted_emails' not in st.session_state:
        st.session_state.extracted_emails = []
    if 'email_producer' not in st.session_state:
        st.session_state.email_producer = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary directory."""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path(Config.UPLOAD_FOLDER)
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


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
                            st.error("❌ Connection failed. Check credentials.")
            else:
                st.error("❌ SMTP not configured")
                st.info("Configure SMTP in .env file")
        
        # RabbitMQ Status
        with st.expander("🐰 RabbitMQ Status", expanded=False):
            st.info(f"Host: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
            st.info(f"Queue: {Config.RABBITMQ_QUEUE}")
        
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
                        
                        # Save file
                        file_path = save_uploaded_file(uploaded_file)
                        
                        if file_path:
                            # Extract emails
                            emails = CVParser.process_file(file_path)
                            all_emails.update(emails)
                            
                            results_data.append({
                                'File': uploaded_file.name,
                                'Emails Found': len(emails),
                                'Emails': ', '.join(emails) if emails else 'None'
                            })
                            
                            # Clean up
                            try:
                                os.remove(file_path)
                            except:
                                pass
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Store in session state
                    st.session_state.extracted_emails = list(all_emails)
                    
                    # Display results
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
                        
                        # Download option
                        csv = email_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Email List (CSV)",
                            data=csv,
                            file_name="extracted_emails.csv",
                            mime="text/csv"
                        )
    
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
                    candidate_name = st.text_input("Candidate Name", placeholder="e.g., Candidate or leave blank for generic")
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
                                              placeholder="Any additional details you'd like to include...")
                
                # Email selection
                st.subheader("📧 Select Recipients")
                selected_emails = st.multiselect(
                    "Choose email addresses",
                    st.session_state.extracted_emails,
                    default=st.session_state.extracted_emails
                )
                
                submit_screening = st.form_submit_button("📤 Send Screening Emails", type="primary")
                
                if submit_screening:
                    if not all([company_name, position, hr_name]):
                        st.error("❌ Please fill in all required fields (Company Name, Position, HR Name)")
                    elif not selected_emails:
                        st.error("❌ Please select at least one recipient")
                    else:
                        with st.spinner("Queueing emails..."):
                            try:
                                # Initialize producer
                                producer = EmailQueueProducer()
                                
                                # Prepare emails
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
                                        'from_name': from_name,
                                        'template_type': 'screening'
                                    })
                                
                                # Send to queue
                                stats = producer.send_bulk_email_tasks(email_tasks)
                                producer.close()
                                
                                st.success(f"✅ {stats['success']} email(s) queued successfully!")
                                if stats['failed'] > 0:
                                    st.warning(f"⚠️ {stats['failed']} email(s) failed to queue")
                                
                                st.info("📬 Emails are being processed in the background by the email worker.")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                logger.error(f"Error sending screening emails: {e}")
    
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
                    candidate_name_rej = st.text_input("Candidate Name", placeholder="e.g., Candidate or leave blank", key="rej_candidate")
                    from_name_rej = st.text_input("From Name (Optional)", placeholder="e.g., HR Team", key="rej_from")
                
                additional_message = st.text_area("Additional Message (Optional)", 
                                                 placeholder="Any encouraging words or future opportunities...",
                                                 key="rej_msg")
                
                # Email selection
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
                        with st.spinner("Queueing emails..."):
                            try:
                                producer = EmailQueueProducer()
                                
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
                                        'from_name': from_name_rej,
                                        'template_type': 'rejection'
                                    })
                                
                                stats = producer.send_bulk_email_tasks(email_tasks)
                                producer.close()
                                
                                st.success(f"✅ {stats['success']} email(s) queued successfully!")
                                if stats['failed'] > 0:
                                    st.warning(f"⚠️ {stats['failed']} email(s) failed to queue")
                                
                                st.info("📬 Emails are being processed in the background.")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                logger.error(f"Error sending rejection emails: {e}")
    
    # Tab 4: Custom Email
    with tab4:
        st.header("📋 Send Custom Email")
        st.info("Create and send custom emails with variable placeholders like {candidate_name}, {position}, etc.")
        
        if not st.session_state.extracted_emails:
            st.warning("⚠️ No emails extracted yet. Please upload CVs in the 'Upload & Extract' tab first.")
        else:
            with st.form("custom_form"):
                subject_custom = st.text_input("Email Subject *", placeholder="e.g., Opportunity at {company_name}")
                
                body_custom = st.text_area("Email Body *", height=300,
                    placeholder="""Dear {candidate_name},

We are reaching out regarding {position} position...

Best regards,
{hr_name}
{company_name}""")
                
                st.info("💡 Use placeholders like {candidate_name}, {position}, {company_name}, {hr_name} in your template")
                
                col1, col2 = st.columns(2)
                with col1:
                    var_candidate = st.text_input("candidate_name", placeholder="John Doe", key="custom_candidate")
                    var_position = st.text_input("position", placeholder="Developer", key="custom_position")
                
                with col2:
                    var_company = st.text_input("company_name", placeholder="Tech Corp", key="custom_company")
                    var_hr = st.text_input("hr_name", placeholder="HR Manager", key="custom_hr")
                
                from_name_custom = st.text_input("From Name (Optional)", key="custom_from")
                
                # Email selection
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
                        with st.spinner("Queueing emails..."):
                            try:
                                producer = EmailQueueProducer()
                                
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
                                        'from_name': from_name_custom,
                                        'template_type': 'custom'
                                    })
                                
                                stats = producer.send_bulk_email_tasks(email_tasks)
                                producer.close()
                                
                                st.success(f"✅ {stats['success']} email(s) queued successfully!")
                                if stats['failed'] > 0:
                                    st.warning(f"⚠️ {stats['failed']} email(s) failed to queue")
                                
                                st.info("📬 Emails are being processed in the background.")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                logger.error(f"Error sending custom emails: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>📧 Lizmail - Automated Email System | Built with Streamlit & RabbitMQ</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

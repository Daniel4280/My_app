import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid

# Configuration de l'e-mail d'envoi
SENDER_EMAIL = "dani24d24@gmail.com"
SENDER_PASSWORD = "ervs jsnz aneu ldbe"

# Session state pour stocker les feedbacks si nécessaire
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}

# Récupérer le paramètre "form" de l'URL
query_params = st.query_params
form_type = query_params.get("form", ["agent_feedback"])[0]  # Par défaut : agent_feedback

# Fonction pour envoyer un e-mail
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Connexion et envoi de l'e-mail
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")


# Choix du formulaire en fonction de "form_type"
if form_type == "agent_feedback":
    # Formulaire principal : Feedback de l'agent
    st.title("Agent Feedback Form")

    # Questions du formulaire principal
    section_choice = st.radio("In which section do you want to provide a report?", options=["Fix", "Mobile"])
    involved_person = st.text_input("Who is involved?")
    msisdn_contractor = st.text_input("Add MSISDN or Contractor")
    superoffice_ticket = st.text_input("Add Superoffice Ticket number")
    description = st.text_area("What happened?")
    team_leader_email = st.text_input("Enter the Team Leader's Email Address")

    # Soumettre le formulaire
    if st.button("Submit", key="agent_submit"):
        if involved_person and team_leader_email:
            # Générer un ID unique pour ce feedback
            feedback_id = str(uuid.uuid4())
            st.session_state.feedbacks[feedback_id] = {
                "section": section_choice,
                "involved_person": involved_person,
                "msisdn_contractor": msisdn_contractor,
                "superoffice_ticket": superoffice_ticket,
                "description": description,
            }

            # Générer un lien pour le formulaire Team Leader Feedback
            base_url = "http://your-app-url.com"  # Remplacez par votre URL déployée
            feedback_url = f"{base_url}/?form=team_leader_feedback&feedback_id={feedback_id}"

            # Envoyer un e-mail au Team Leader avec le lien
            email_body = f"""
            <html>
            <body>
                <h2>New Feedback Submission</h2>
                <p>An agent has submitted feedback. Please review it and provide your input by clicking the link below:</p>
                <a href="{feedback_url}" style="background-color: #2E86C1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review and Provide Feedback</a>
            </body>
            </html>
            """
            send_email(team_leader_email, "New Feedback Submission", email_body)

            st.success(f"Feedback submitted successfully! Link sent to Team Leader: {feedback_url}")
        else:
            st.warning("Please complete all required fields.")

elif form_type == "team_leader_feedback":
    # Formulaire secondaire : Feedback du Team Leader
    st.title("Team Leader Feedback Form")

    # Récupérer l'identifiant du feedback depuis l'URL
    feedback_id = query_params.get("feedback_id", [None])[0]

    if feedback_id and feedback_id in st.session_state.feedbacks:
        # Charger les données du feedback principal
        feedback_data = st.session_state.feedbacks[feedback_id]
        st.subheader("Feedback Summary")
        st.write(feedback_data)

        # Questions spécifiques pour le Team Leader
        main_reason = st.radio("Main Reason:", options=[
            "Coaching", "Group Training", "Warning", "Dismissal",
            "Leaver (SST only)", "Wrong agent (invalidate)", "No mistake made (invalidate)"
        ])
        details = st.text_area("Details (Explain your choice):")

        # Soumettre le feedback du Team Leader
        if st.button("Submit Team Leader Feedback"):
            st.session_state.feedbacks[feedback_id]["team_leader_feedback"] = {
                "main_reason": main_reason,
                "details": details
            }
            st.success("Team Leader feedback submitted successfully!")
    else:
        st.error("Feedback not found or invalid ID.")

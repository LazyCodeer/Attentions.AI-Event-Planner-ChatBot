import streamlit as st
import requests
from datetime import datetime
import nest_asyncio
from phi.assistant import Assistant
from phi.utils.log import logger
from agent import get_agent

nest_asyncio.apply()

st.set_page_config(page_title="Wanderlust", page_icon="✨")


# Replace with your FastAPI backend URL
BACKEND_URL = "http://localhost:8000"  # Adjust the port if necessary


def init_session_state():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "email" not in st.session_state:
        st.session_state["email"] = None
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "register_mode" not in st.session_state:
        st.session_state["register_mode"] = False
    if "agent" not in st.session_state:
        st.session_state["agent"] = None
    if "agent_run_id" not in st.session_state:
        st.session_state["agent_run_id"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = None


def login_page():
    """Login page where the user can enter credentials."""
    # st.title("🗺️ AI Tour Planner")

    # Check if the user is in registration mode
    if st.session_state.get("register_mode"):
        register_page()
        return

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if email and password:
                # Send a POST request to your FastAPI backend for authentication
                login_data = {"email": email, "password": password}
                try:
                    response = requests.post(f"{BACKEND_URL}/login", json=login_data)
                    if response.status_code == 200:
                        user_data = response.json()
                        st.session_state["logged_in"] = True
                        st.session_state["name"] = user_data.get("name", "")
                        st.session_state["email"] = user_data.get("email", "")
                        st.session_state["user_id"] = user_data["id"]
                        st.success(user_data.get("msg", "Login successful"))
                        st.experimental_rerun()
                    else:
                        st.error(response.json().get("detail", "Login failed"))
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please enter both email and password.")

    st.write("Don't have an account?")
    if st.button("Register"):
        st.session_state["register_mode"] = True
        st.experimental_rerun()


def register_page():
    """Registration page where the user can create an account."""

    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            if (
                not name
                or not email
                or not contact
                or not password
                or not confirm_password
            ):
                st.error("Please fill in all the fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Prepare registration data according to the schema
                register_data = {
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "password": password,
                }
                # Send a POST request to your FastAPI backend for registration
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/register", json=register_data
                    )
                    if response.status_code == 200:
                        st.success("Registration successful. Please log in.")
                        st.session_state["register_mode"] = False
                        st.experimental_rerun()
                    else:
                        st.error(response.json().get("detail", "Registration failed"))
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")

    if st.button("Back to Login"):
        st.session_state["register_mode"] = False
        st.experimental_rerun()


def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Existing styles */
        .stApp {
            background-color: #323946;
        }
        .stApp header {
            background-color: #323946;
        }
        .stApp footer {
            background-color: #262730;
        }
        [data-testid="stSidebar"] {
            background-color: #1F242D;
            box-shadow: 1px 0 10px rgba(0, 255, 255, 0.3),
                2px 0 20px rgba(0, 255, 255, 0.2),
                3px 0 30px rgba(0, 255, 255, 0.1);
        }
        [data-testid="stSidebar"] * {
            color: white;
        }
        [data-testid="stChatInput"] {
            background-color: #ffffff;
        }
        [data-testid="stChatInput"] {
            background-color: #1F242D;
            color: #00EEFF;
        }
        /* Change the placeholder text color */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #FFF;
        }
        /* Change the send button */
        [data-testid="stChatInput"] button {
            color: #00EEFF;
        }
        /* Center buttons in the sidebar */
        [data-testid="stSidebar"] .stButton {
            margin-top: 15px;
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    """Main application logic."""
    apply_custom_styles()

    init_session_state()

    st.title("✨ Wanderlust")

    if not st.session_state.get("logged_in"):

        login_page()
        return

    # st.subheader(
    #     f"Ready for your next adventure, {st.session_state['name']}? Let's create magic!"
    # )

    # Display user info in sidebar
    # st.sidebar.markdown(
    #     "<h1 style='text-align: center;'>✨ Wanderlust</h1>", unsafe_allow_html=True
    # )
    st.sidebar.markdown(
        """
    <div style='text-align: center; color: #00EEFF;'>
        <h3>Welcome Explorer! 👋</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )
    placeholder_image_url = "https://img.freepik.com/free-vector/smiling-young-man-illustration_1308-174669.jpg?t=st=1731205821~exp=1731209421~hmac=31a0efd1528ab3dbba1fa389983e1ee7f5b9ac1820dd429cb702b405f200ce89&w=740"

    st.sidebar.markdown(
        f"""
        <div style='text-align: center;'>
            <img src={placeholder_image_url} width="100" height="100" style="border-radius:50%; object-fit:cover;">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # st.sidebar.image("images/profile.jpg", width=150)
    # st.sidebar.title("User Info")
    st.sidebar.markdown(
        f"""
        <div style='text-align: center; margin-top:20px; font-size:18px; font-weight:600;'>
            {st.session_state['name']}
        </div>""",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""
        <div style='text-align: center; font-size:18px; font-weight:600;'>
            {st.session_state['email']}
        </div>""",
        unsafe_allow_html=True,
    )
    # st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(
        """
    <div style='background-color: #2A303C; padding: 15px; border-radius: 10px; margin: 10px 0;'>
        <h4 style='color: #00EEFF; margin: 0;'>Trip Stats 📊</h4>
        <hr style='border-color: #00EEFF;'>
        <p style='color: white;'>🎯 Destinations Planned: 0</p>
        <p style='color: white;'>⏱️ Hours Explored: 0</p>
        <p style='color: white;'>💫 Places Visited: 0</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
    <div style='background-color: #2A303C; padding: 15px; border-radius: 10px; margin: 10px 0;'>
        <h4 style='color: #00EEFF; margin: 0;'>Quick Links 🔗</h4>
        <hr style='border-color: #00EEFF;'>
        <p style='color: white;'>📝 My Itineraries</p>
        <p style='color: white;'>⭐ Favorites</p>
        <p style='color: white;'>🎨 Preferences</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # st.sidebar.markdown("<br>", unsafe_allow_html=True)
    

    # Set default LLM model to llama3
    llm_id = "llama3"

    # Get the agent
    agent: Assistant
    if "agent" not in st.session_state or st.session_state["agent"] is None:
        logger.info(f"---*--- Creating Tour Planning Agent with {llm_id} ---*---")
        agent = get_agent(llm_id=llm_id, user_id=st.session_state["user_id"])
        st.session_state["agent"] = agent
    else:
        agent = st.session_state["agent"]

    try:
        st.session_state["agent_run_id"] = agent.create_run()
    except Exception:
        st.warning("Could not create Agent run, is the database running?")
        return

    # Load existing messages
    if "messages" not in st.session_state or st.session_state["messages"] is None:
        assistant_chat_history = agent.memory.get_chat_history()
        if len(assistant_chat_history) > 0:
            logger.debug("Loading chat history")
            st.session_state["messages"] = assistant_chat_history
        else:
            logger.debug("No chat history found")
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Let's plan your perfect day tour! Which city would you like to visit?",
                }
            ]

    # Chat interface
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"], avatar="🌎"):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Immediately show user message in chat
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant", avatar="🌎"):
            response = ""
            resp_container = st.empty()

            # Show a loader while generating the response
            with st.spinner("Exploring hidden gems for you... 🌟"):
                for delta in agent.run(prompt):
                    response += delta
                    resp_container.markdown(response)

            # Add the assistant's response to session state
            st.session_state["messages"].append(
                {"role": "assistant", "content": response}
            )

            # Optionally, store chat messages in the backend
            try:
                chat_data = {
                    "user_id": st.session_state["user_id"],
                    "message": prompt,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                requests.post(f"{BACKEND_URL}/chat/", json=chat_data)
            except:
                logger.warning("Failed to store chat message in backend")

    # Logout button
    if st.sidebar.button("Logout"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.experimental_rerun()


if __name__ == "__main__":
    main()

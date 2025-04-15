import json
import os
import random
import time

import requests
import streamlit as st

from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

#BACKEND_URL = os.getenv("BACKEND_URL")
#BACKEND_TOKEN = os.getenv("BACKEND_TOKEN")
BACKEND_URL = os.environ.get("BACKEND_URL")#AC
BACKEND_TOKEN = os.environ.get("BACKEND_TOKEN")#AC

CHAT_ENDPOINT = "/chat"
QUIZ_ENDPOINT = "/quiz"

QUIZ_DATA = '''
{
    "topic": "Star Wars",
    "questions": [
        {
            "question": "Who was the Sith Lord responsible for training Darth Vader?",
            "choices": ["Darth Sidious", "Darth Maul", "Darth Tyranus", "Darth Plagueis"],
            "answer": "Darth Sidious",
            "origin": "Star Wars: Episode III - Revenge of the Sith",
            "explain": "This Sith Lord manipulated Anakin Skywalker into turning to the dark side and becoming his apprentice."
        },
        {
            "question": "What is the name of Han Solo's ship?",
            "choices": ["TIE Fighter", "X-Wing", "Millennium Falcon", "Slave I"],
            "answer": "Millennium Falcon",
            "origin": "Star Wars: Episode IV - A New Hope",
            "explain": "Known for its speed and modifications, this Corellian freighter was central to many adventures."
        },
        {
            "question": "Which planet is the homeworld of Yoda's species?",
            "choices": ["Tatooine", "Dagobah", "Naboo", "Coruscant"],
            "answer": "Dagobah",
            "origin": "Star Wars: Episode V - The Empire Strikes Back",
            "explain": "This swampy planet in a remote system was where Luke Skywalker sought out the exiled Jedi Master."
        },
        {
            "question": "Who killed Jabba the Hutt?",
            "choices": ["Luke Skywalker", "Han Solo", "Leia Organa", "Boba Fett"],
            "answer": "Leia Organa",
            "origin": "Star Wars: Episode VI - Return of the Jedi",
            "explain": "While disguised as a bounty hunter, this character infiltrated Jabba's palace and ultimately ended his reign."
        },
        {
            "question": "What was the name of the droid that accompanied Luke Skywalker on his journey?",
            "choices": ["C-3PO", "BB-8", "R2-D2", "K-2SO"],
            "answer": "R2-D2",
            "origin": "Star Wars: Episode IV - A New Hope",
            "explain": "This astromech droid carried vital information and was a constant companion to the young Jedi."
        }
    ]
}
'''

def page_setup():
    st.set_page_config(
        page_title="DSFS-33",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={},
    )


def session_setup():
    if "token" not in st.session_state:
        st.session_state.token = BACKEND_TOKEN

    if "cookies" not in st.session_state:
        st.session_state.cookies = {}

    if "active_page" not in st.session_state:
        st.session_state.active_page = "chat-with-our-gpt"

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if 'quiz' not in st.session_state:
        st.session_state.quiz = {}

    if 'quiz_index' not in st.session_state:
        st.session_state.quiz_index = 0

    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}


def call_huggingface_space(url: str, data: dict) -> dict:
    with st.spinner("Thinking..."):
        try:
            headers = {
                "Authorization": f"Bearer {BACKEND_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            response = requests.post(f"{BACKEND_URL}{url}", json=data, headers=headers, cookies=st.session_state.cookies)
            response.raise_for_status()

            st.session_state.cookies = response.cookies

            return response.json()
        except Exception as e:
            return {"error": str(e)}


@st.fragment
def sidebar_menu_fragment():
    st.title("GPT DSFS-33")

    st.markdown("Interagissez avec notre base de connaissances.")

    with st.container(border=True):
        if st.button("Discuter avec GPT DSFS33", type="primary" if st.session_state.active_page == "chat-with-our-gpt" else "secondary",
                     use_container_width=True):
            st.session_state.active_page = "chat-with-our-gpt"
            st.rerun()

        if st.button("Répondre au quiz Programmez", type="primary" if st.session_state.active_page == "take-the-random-quiz" else "secondary",
                     use_container_width=True):
            st.session_state.active_page = "take-the-random-quiz"
            st.rerun()


@st.fragment
def display_chat_with_gpt():
    st.header("Discuter avec GPT DSFS33", anchor="chat-with-our-gpt")
    st.markdown("Vous pouvez discuter avec GPT DSFS33 sur des articles archivés.")

    if st.button("Nouvelle discussion"):
        if "cookies" in st.session_state:
            del st.session_state.cookies["chat_id"]
        st.session_state.chat_messages = []

    with st.container(border=True, height=250):
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user := st.chat_input("Dites-moi ce que vous voulez, ce que vous voulez vraiment, vraiment... ;)"):
        
        st.session_state.chat_messages.append({"role": "user", "content": user})

        response = call_huggingface_space(CHAT_ENDPOINT, {"user": user})

        if "answer" in response:
            answer = response["answer"]
            st.session_state.chat_messages.append({"role": "assistant", "content": ""})

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_text = ""
                for chunk in answer:
                    full_text += chunk
                    placeholder.markdown(full_text)
                    time.sleep(0.02)  # Ajuste le délai selon le rythme voulu

            # Met à jour le message sauvegardé dans session_state
            st.session_state.chat_messages[-1]["content"] = full_text
            st.rerun()


@st.fragment
def display_quiz():
    st.header("Répondre au quiz aléatoire", anchor="take-the-random-quiz")
    st.markdown("Vous pouvez répondre à un quiz aléatoire. Le sujet est choisi parmi nos articles édités.")

    if st.button("Nouveau quiz"):
        subjects = random.sample([
            "Intelligence Artificielle (IA) et Apprentissage Machine (Machine Learning)",
            "Développement Web Front-end",
            "Développement Web Back-end",
            "Cloud Computing",
            "Sécurité Informatique",
            "Langages de Programmation Spécifiques",
            "Bases de Données",
            "Développement Mobile",
            "Tests Logiciels",
            "Méthodologies Agiles",
            "Outils de Développement",
            "Architecture Logicielle",
            "Internet des Objets (IoT)",
            "Science des Données et Big Data",
            "Systèmes d'Exploitation",
            "Performances et Optimisation",
            "Qualité du Code",
            "Aspects Métiers et Business pour Développeurs",
            "Événements et Actualités du Secteur Tech",
            "Histoire de l'Informatique et Technologies Émergentes"], 3)
        subjects = ", ".join(subjects)
        response = call_huggingface_space(QUIZ_ENDPOINT, {"user": f"Génère un quiz conformément aux instructions sur l'un des sujets suivants : {subjects}"})

        if "quiz" in response:
            st.session_state.quiz = response["quiz"]
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = {}
        else:
        # dans ce cas c'est le quiz Star wars!
            st.toast("Désolé, je n'ai pas pu traiter votre demande.")
            st.session_state.quiz = json.loads(QUIZ_DATA)
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = {}

    if st.session_state.quiz:
        st.write(f"##### Quelques questions sur : {st.session_state.quiz['topic']}")
        st.progress(st.session_state.quiz_index / float((len(st.session_state.quiz["questions"]))))

        if st.session_state.quiz_index < len(st.session_state.quiz["questions"]):
            question = st.session_state.quiz["questions"][st.session_state.quiz_index]
            with st.container(border=True):
                st.write(f"##### {st.session_state.quiz_index + 1}: {question['question']}")
                for _, choice in enumerate(question["choices"], start=1):
                    if st.checkbox(choice):
                        st.session_state.quiz_answers[st.session_state.quiz_index] = choice
                        st.session_state.quiz_index += 1
                        st.rerun()
        else:
            st.write("##### Résultats du Quiz")
            for i, question in enumerate(st.session_state.quiz['questions'], start=1):
                with st.container(border=True):
                    st.write(f"**{i}: {question['question']}**")
                    user_choice = st.session_state.quiz_answers.get(i - 1, None)
                    correct_choice = question["answer"]
                    st.write(f"Réponse correcte : {correct_choice}")
                    with st.container(border=True):
                        st.code(question['explain'], language=None, wrap_lines=True)
                    st.caption(f"*Source :* **{question['origin']}**")
                    if user_choice == correct_choice:
                        st.info(random.choice([
                            "Ah, enfin une étincelle dans ce désert de confusion. Bien joué.",
                            "Incroyable ! Pour une fois, vous avez visé juste. Ne vous y habituez pas.",
                            "Félicitations, vous avez temporairement échappé à la médiocrité.",
                            "On dirait que même une horloge cassée peut donner l'heure juste deux fois par jour.",
                            "Impressionnant... pour vos standards, s'entend.",
                            "Qui l'eût cru ? Un éclair de génie dans cette matière grise.",
                            "Vous commencez à nous faire croire que ce n'est pas complètement désespéré.",
                            "Un coup de chance ? Peut-être. Mais savourez l'instant.",
                            "Voilà qui prouve que même les miracles peuvent arriver. Rarement, certes.",
                            "Surprenant ! Continuez comme ça, et qui sait, vous atteindrez peut-être la moyenne un jour."
                        ]), icon=":material/check_box:")
                    else:
                        st.write(f"Votre réponse : {user_choice}")
                        st.error(random.choice([
                            "Ne vous inquiétez pas, l'échec est une étape... vers d'autres échecs.",
                            "Encore une tentative infructueuse. Votre constance dans l'erreur est admirable.",
                            "C'est ça, restez fidèle à vous-même. La mauvaise réponse, votre marque de fabrique.",
                            "Au moins, vous êtes cohérent dans votre incapacité à répondre correctement.",
                            "Chaque mauvaise réponse vous rapproche... de la fin du quiz.",
                            "Votre interprétation de la question est... disons... créative.",
                            "N'ayez pas honte, l'important c'est de participer... et de se tromper.",
                            "On sent la réflexion intense... qui n'a malheureusement pas porté ses fruits.",
                            "C'est une réponse... originale. On ne peut pas vous enlever ça.",
                            "Ne désespérez pas, il reste encore des questions pour confirmer votre talent dans l'erreur."
                        ]), icon=":material/cancel:")


def run():
    page_setup()
    session_setup()
    with st.sidebar:
        sidebar_menu_fragment()

    if st.session_state.active_page == "chat-with-our-gpt":
        display_chat_with_gpt()

    if st.session_state.active_page == "take-the-random-quiz":
        display_quiz()


if __name__ == "__main__":
    run()


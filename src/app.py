import logging

import gradio as gr
import requests
from theme import EzmeralTheme


# LOGO = """
# [![Robot-final-comp.gif](https://i.postimg.cc/pry2R4S8/Robot-final-comp.gif)](https://postimg.cc/T5M8c7fY)
# """

WELCOME = '''Hi! I'm Gema, your Acme sales and quoting AI powered by HPE & NVIDIA. 

How can I help?'''

try: 
    NAMESPACE = open(
        "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
    ).read()
except:
    NAMESPACE = "test"


URL = "http://agent.{0}:9000/{1}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

custom_css = """
#chatbot {
    height: calc(60vh - 50px) !important; /* Adjust the height as needed */
    overflow: auto;
}

.tab{
    background: white;
}

.tab-nav{
    border-bottom: none;
}
.tab button{
    border: 2px solid #F9FAFB;
}


.tab-nav button{
    padding-bottom: 10px;
    border: none;
}

/* .tab-nav button{
    background: #e4e2dd;
    border: 2px solid transparent;
    border-radius: 10px;
    margin-right: 5px;
    color: black;
}*/

.tab-nav button[aria-selected="true"]{
  background-color: white;
color: #01a982;
}

.tabitem{
    border: none;
    background: white;
}

.left{
    margin-right: 20px;
}

.upload-label{
    font-size: 24px !important;
    margin-bottom: 10px;
}

.menu-item > *{
    margin-bottom: 15px;
}
.file-preview-holder{
    margin-top: 15px;
}
#logo{
width: 100%;
}

.download a{
    color: #01a982 !important;
}

footer {
    visibility: hidden
}
"""


def chat_service(
        message,
        chat_history,
        temperature,
        max_tokens,
        ctx,
        manual_options,
        request: gr.Request):
    headers = {"Authorization": request.headers.get("authorization")}

    logger.info(f"Message: {message}")
    logger.info(f"Chat history: {chat_history}")
    logger.info(f"Context: {ctx}")
    if ctx == "Yes":
        ctx = True
    else:
        ctx = False

    inputs = {"input": 
        {
            "question": message,
            "chat_history": chat_history,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "ctx": ctx,
            "manual_options": manual_options
        }
    }
    response = requests.post(
        URL.format(NAMESPACE, "invoke"), json=inputs, headers=headers)

    logger.info(f"Response: {response.text}")

    bot_message = response.json()["output"]

    logger.info(f"Bot message: {bot_message}")

    chat_history.append((message, bot_message))
    
    return "", chat_history


def update_ui(choice):
    if choice == "Smart":
        return gr.update(visible=False, value=None)
    else:
        return gr.update(visible=True, value="Chat", interactive=True)


def upload_document(files, request: gr.Request):
    headers = {"Authorization": request.headers.get("authorization")}

    # Create a list of documents (when valid)
    list_file_path = [x.name for x in files if x is not None]

    for file_path in list_file_path:
        logger.info(f"Uploading file: {file_path}")
    
        f = {'file': open(file_path, 'rb')}

        response = requests.post(
            URL.format(NAMESPACE,"uploadpdf"), files=f, headers=headers)
        
    if response.status_code == 200:
        logger.info("Files uploaded successfully.")
        return f"{str(len(files))} files uploaded successfully."

    return "An error occurred while uploading files. Please try again."


def main(): 
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="emerald"), css=custom_css) as app:
        with gr.Row():
            html = gr.HTML(
            "<div >"
            "<img src='file/images/acme.png' id='logo' alt='image One'>"
            + "</div>"
            )  
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["left"]):
                # gr.Markdown(
                #     "<b>To leverage your own private documents for this quote, upload them below.<br></b>"
                # )
                with gr.Tab("File Upload"):
                    with gr.Row():
                        document = gr.Files(
                            height=300, file_count="multiple",
                            file_types=["pdf"], interactive=True,
                            label="Upload PDF documents",
                            show_label=False)
                    with gr.Row():
                        db_progress = gr.Label(
                            value="No files uploaded.", show_label=False, elem_classes=["upload-label"])
                    with gr.Row():
                        # ctx = gr.Checkbox(
                        #     value=True,
                        #     label="Use Private Knowledge Base"
                        # )
                        ctx = gr.Radio(
                            choices=["Yes", "No"],
                            info="Give access to the uploaded files stored in your Private Knowledge Base?",
                            label="Private Knowledge Base",
                            value="Yes",
                            elem_classes=["menu-item"]
                        )
                with gr.Tab("Settings"):
                    with gr.Row():
                        model = gr.Dropdown(
                            ["meta-llama/Meta-Llama-2-7B", "meta-llama/Meta-Llama-3-8B", "microsoft/Phi-3-mini-128k-instruct"], interactive=True, allow_custom_value=True, value="meta-llama/Meta-Llama-2-7B", label="Large Language Model", elem_classes=["menu-item"]
                            )    
                    with gr.Row():
                        radio_buttons = gr.Radio(
                            choices=["Smart", "Manual"],
                            info="Select mode of operation. In Smart mode, the chatbot"
                                " will use an intelligent model to determine the flow."
                                " In manual mode, you can choose the type of query to perform.",
                            value="Smart",
                            label="AI Mode",
                            elem_classes=["menu-item"]
                        )
                    with gr.Row():
                        manual_options = gr.Radio(
                            choices=["Chat", "SQL Query", "Vector Store Query"],
                            info="Select the type of query you want to perform.",
                            visible=False,
                            label="Manual Chat Mode",
                            elem_classes=["menu-item"]
                        )
                with gr.Tab("Advanced"):     
                        with gr.Row():
                            with gr.Column():
                                temperature = gr.Slider(
                                    label="Temperature",
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=0.1,
                                    info="The model temperature. Larger values increase"
                                        " creativity but decrease factuality.",
                                        elem_classes=["menu-item"]
                                )
                            with gr.Column():
                                max_tokens = gr.Number(
                                    label="Max Tokens",
                                    minimum=10,
                                    maximum=1000,
                                    value=200,
                                    info="The maximum number of tokens to generate.",
                                    elem_classes=["menu-item"]
                                )
            with gr.Column(scale=2):
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="SalesAI",
                        show_copy_button=True,
                        elem_id="chatbot"
                    )
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Enter your message...",
                        show_label=False,
                        autofocus=True)
                with gr.Row():
                    with gr.Column():
                        submit_btn = gr.Button("Submit", variant="primary")
                    with gr.Column():
                        clear_btn = gr.ClearButton([msg, chatbot])

        inputs = [msg, chatbot, temperature, max_tokens, ctx, manual_options]

        submit_btn.click(chat_service, inputs, [msg, chatbot])
        # upload_btn.click(
        #     upload_document, inputs=[document], outputs=[db_progress])
        document.change(upload_document, inputs=[document], outputs=[db_progress])
        clear_btn.click
        radio_buttons.change(
            update_ui, 
            radio_buttons, 
            manual_options
        )

        msg.submit(chat_service, inputs, [msg, chatbot])

    app.launch(server_name="0.0.0.0", server_port=8080, allowed_paths=["."])
    # app.launch(allowed_paths=["."])


if __name__ == "__main__":
    main()

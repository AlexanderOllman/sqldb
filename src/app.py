import inspect
import time
from typing import Iterable
from theme import EzmeralTheme

from gradio_client.documentation import document_fn

import gradio as gr

import logging

import requests
import os


# LOGO = """
# [![Robot-final-comp.gif](https://i.postimg.cc/pry2R4S8/Robot-final-comp.gif)](https://postimg.cc/T5M8c7fY)
# """

WELCOME = '''Hi! I'm the HPE Portfolio Assistant, your sales information and quote builder AI powered by HPE GreenLake & NVIDIA. 

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

session_file = "session.txt"

def load_session_variables():
    array = []
    try:
        with open(session_file, 'r') as file:  # Open the file in read mode
            for line in file:
                array.append(line.strip())  # Strip newline characters and add to array
        print("File successfully read into an array.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return array


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
        return gr.update(
            visible=True, value="Yes"), gr.update(visible=False, value=None)
    else:
        return gr.update(
            visible=False, value="No"), gr.update(visible=True, value="Chat", interactive=True)


def load_theme():
    loaded_text = []
    loaded_css = "theme.css"
    try:
        with open(session_file, 'r') as file:  # Open the file in read mode
            for line in file:
                loaded_text.append(line.strip())  # Strip newline characters and add to array
        print("File successfully read into an array.")
    except Exception as e:
        print(f"An error occurred: {e}")
    print(loaded_text)
    if loaded_text[0] == "None":
        loaded_theme = gr.themes.Soft(primary_hue="slate")
    else:
        loaded_theme = EzmeralTheme()

    return loaded_theme, loaded_css


def update_theme(choice, inputs):
    # try:
    #     with open(session_file, 'w') as file:
    #         file.truncate(0)
    #         file.write(f"{choice}\n")

    #     # with open(session_file, 'a') as file:  # Open the file in append mode
    #     #     for input in inputs:
    #     #         file.write(f"{input}\n")  # Write each element followed by a newline
    #     # file.write(f"{choice}\n")
    #     # print("Array successfully written to the file.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    if choice == "None":
        return [gr.update(visible=False), gr.update(label="Chat")]
    else:
        return [gr.update(visible=True), gr.update(label="HPE Portfolio Assistant")]
    
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
        if len(files) == 1:
            message = f"{str(len(files))} file uploaded successfully."
        else:
            message = f"{str(len(files))} files uploaded successfully."
        return [gr.update(value=None), message]

    return [gr.update(value=None), "An error occurred while uploading files. Please try again."]

themes = [
    gr.themes.Base,
    gr.themes.Default,
    gr.themes.Soft,
    gr.themes.Monochrome,
    gr.themes.Glass,
    EzmeralTheme
]
colors = gr.themes.Color.all
sizes = gr.themes.Size.all

palette_range = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
size_range = ["xxs", "xs", "sm", "md", "lg", "xl", "xxl"]
docs_theme_core = document_fn(gr.themes.Base.__init__, gr.themes.Base)[1]
docs_theme_vars = document_fn(gr.themes.Base.set, gr.themes.Base)[1]


def get_docstr(var):
    for parameters in docs_theme_core + docs_theme_vars:
        if parameters["name"] == var:
            return parameters["doc"]
    raise ValueError(f"Variable {var} not found in theme documentation.")


def get_doc_theme_var_groups():
    source = inspect.getsource(gr.themes.Base.set)
    groups = []
    group, desc, variables, flat_variables = None, None, [], []
    for line in source.splitlines():
        line = line.strip()
        if line.startswith(")"):
            break
        elif line.startswith("# "):
            if group is not None:
                groups.append((group, desc, variables))
            group, desc = line[2:].split(": ")
            variables = []
        elif "=" in line:
            var = line.split("=")[0]
            variables.append(var)
            flat_variables.append(var)
    groups.append((group, desc, variables))
    return groups, flat_variables


variable_groups, flat_variables = get_doc_theme_var_groups()

css = """
.gradio-container {
    overflow: visible !important;
    max-width: none !important;
}
#controls {
    max-height: 100vh;
    flex-wrap: unset;
    overflow-y: scroll;
    position: sticky;
    top: 0;
}
#controls::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 7px;
}

#controls::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(0, 0, 0, .5);
  box-shadow: 0 0 1px rgba(255, 255, 255, .5);
}
"""

with gr.Blocks(  # noqa: SIM117
    theme=gr.themes.Base(),
    css=css,
    title="Gradio Theme Builder",
) as demo:
    with gr.Row():
        with gr.Column(scale=1, elem_id="controls", min_width=400):
            with gr.Tab("Settings"):
                with gr.Row() as upload_field:
                    document = gr.Files(
                        height=300, file_count="multiple",
                        file_types=["pdf"], interactive=True,
                        label="Upload PDF documents",
                        show_label=False)
                with gr.Row() as upload_button:
                    upload_btn = gr.Button("Upload")
                with gr.Row() as upload_label:
                    db_progress = gr.Label(
                        value="", show_label=False, elem_classes=["upload-label"])
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
                        label="Chat Mode",
                        elem_classes=["menu-item"]
                    )
            with gr.Tab("Advanced"):
                with gr.Row():
                    model = gr.Dropdown(
                        ["meta-llama/Meta-Llama-2-7B", "meta-llama/Meta-Llama-3-8B", "microsoft/Phi-3-mini-128k-instruct", "mistralai/Mistral-7B-v0.3"], interactive=True, allow_custom_value=True, value="meta-llama/Meta-Llama-2-7B", label="Large Language Model", elem_classes=["menu-item"]
                        )    
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
                        theme = gr.Radio(
                        choices=["None", "HPE Portfolio Assistant"],
                        value="None",
                        label="Theme",
                        elem_classes=["menu-item"]
                    )
            with gr.Tab("Theme"):
                with gr.Row():
                    undo_btn = gr.Button("Undo", size="sm")
                    dark_mode_btn = gr.Button("Dark Mode", variant="primary", size="sm")
                with gr.Row():
                    gr.Markdown(
                            """
                        Select a base theme below you would like to build off of. Note: when you click 'Load Theme', all variable values in other tabs will be overwritten!
                        """
                        )
                with gr.Row():
                    base_theme_dropdown = gr.Dropdown(
                        [theme.__name__ for theme in themes],
                        value="Base",
                        show_label=False,
                        label="Theme",
                    )
                with gr.Row():
                    load_theme_btn = gr.Button("Load Theme", elem_id="load_theme")
                with gr.Tabs(visible=False):                
                    with gr.TabItem("Core Colors"):
                        gr.Markdown(
                            """Set the three hues of the theme: `primary_hue`, `secondary_hue`, and `neutral_hue`.
                            Each of these is a palette ranging from 50 to 950 in brightness. Pick a preset palette - optionally, open the accordion to overwrite specific values.
                            Note that these variables do not affect elements directly, but are referenced by other variables with asterisks, such as `*primary_200` or `*neutral_950`."""
                        )
                        primary_hue = gr.Dropdown(
                            [color.name for color in colors], label="Primary Hue"
                        )
                        with gr.Accordion(label="Primary Hue Palette", open=False):
                            primary_hues = []
                            for i in palette_range:
                                primary_hues.append(
                                    gr.ColorPicker(
                                        label=f"primary_{i}",
                                    )
                                )

                        secondary_hue = gr.Dropdown(
                            [color.name for color in colors], label="Secondary Hue"
                        )
                        with gr.Accordion(label="Secondary Hue Palette", open=False):
                            secondary_hues = []
                            for i in palette_range:
                                secondary_hues.append(
                                    gr.ColorPicker(
                                        label=f"secondary_{i}",
                                    )
                                )

                        neutral_hue = gr.Dropdown(
                            [color.name for color in colors], label="Neutral hue"
                        )
                        with gr.Accordion(label="Neutral Hue Palette", open=False):
                            neutral_hues = []
                            for i in palette_range:
                                neutral_hues.append(
                                    gr.ColorPicker(
                                        label=f"neutral_{i}",
                                    )
                                )

                    with gr.TabItem("Core Sizing"):
                        gr.Markdown(
                            """Set the sizing of the theme via: `text_size`, `spacing_size`, and `radius_size`.
                            Each of these is set to a collection of sizes ranging from `xxs` to `xxl`. Pick a preset size collection - optionally, open the accordion to overwrite specific values.
                            Note that these variables do not affect elements directly, but are referenced by other variables with asterisks, such as `*spacing_xl` or `*text_sm`.
                            """
                        )
                        text_size = gr.Dropdown(
                            [size.name for size in sizes if size.name.startswith("text_")],
                            label="Text Size",
                        )
                        with gr.Accordion(label="Text Size Range", open=False):
                            text_sizes = []
                            for i in size_range:
                                text_sizes.append(
                                    gr.Textbox(
                                        label=f"text_{i}",
                                    )
                                )

                        spacing_size = gr.Dropdown(
                            [
                                size.name
                                for size in sizes
                                if size.name.startswith("spacing_")
                            ],
                            label="Spacing Size",
                        )
                        with gr.Accordion(label="Spacing Size Range", open=False):
                            spacing_sizes = []
                            for i in size_range:
                                spacing_sizes.append(
                                    gr.Textbox(
                                        label=f"spacing_{i}",
                                    )
                                )

                        radius_size = gr.Dropdown(
                            [
                                size.name
                                for size in sizes
                                if size.name.startswith("radius_")
                            ],
                            label="Radius Size",
                        )
                        with gr.Accordion(label="Radius Size Range", open=False):
                            radius_sizes = []
                            for i in size_range:
                                radius_sizes.append(
                                    gr.Textbox(
                                        label=f"radius_{i}",
                                    )
                                )

                    with gr.TabItem("Core Fonts"):
                        gr.Markdown(
                            """Set the main `font` and the monospace `font_mono` here.
                            Set up to 4 values for each (fallbacks in case a font is not available).
                            Check "Google Font" if font should be loaded from Google Fonts.
                            """
                        )
                        gr.Markdown("### Main Font")
                        main_fonts, main_is_google = [], []
                        for i in range(4):
                            with gr.Row():
                                font = gr.Textbox(label=f"Font {i + 1}")
                                font_is_google = gr.Checkbox(label="Google Font")
                                main_fonts.append(font)
                                main_is_google.append(font_is_google)

                        mono_fonts, mono_is_google = [], []
                        gr.Markdown("### Monospace Font")
                        for i in range(4):
                            with gr.Row():
                                font = gr.Textbox(label=f"Font {i + 1}")
                                font_is_google = gr.Checkbox(label="Google Font")
                                mono_fonts.append(font)
                                mono_is_google.append(font_is_google)

                    theme_var_input = []

                    core_color_suggestions = (
                        [f"*primary_{i}" for i in palette_range]
                        + [f"*secondary_{i}" for i in palette_range]
                        + [f"*neutral_{i}" for i in palette_range]
                    )

                    variable_suggestions = {
                        "fill": core_color_suggestions[:],
                        "color": core_color_suggestions[:],
                        "text_size": [f"*text_{i}" for i in size_range],
                        "radius": [f"*radius_{i}" for i in size_range],
                        "padding": [f"*spacing_{i}" for i in size_range],
                        "gap": [f"*spacing_{i}" for i in size_range],
                        "weight": [
                            "100",
                            "200",
                            "300",
                            "400",
                            "500",
                            "600",
                            "700",
                            "800",
                        ],
                        "shadow": ["none"],
                        "border_width": [],
                    }
                    for variable in flat_variables:
                        if variable.endswith("_dark"):
                            continue
                        for style_type in variable_suggestions:
                            if style_type in variable:
                                variable_suggestions[style_type].append("*" + variable)
                                break

                    variable_suggestions["fill"], variable_suggestions["color"] = (
                        variable_suggestions["fill"]
                        + variable_suggestions["color"][len(core_color_suggestions) :],
                        variable_suggestions["color"]
                        + variable_suggestions["fill"][len(core_color_suggestions) :],
                    )

                    for group, desc, variables in variable_groups:
                        with gr.TabItem(group):
                            gr.Markdown(
                                desc
                                + "\nYou can set these to one of the dropdown values, or clear the dropdown to set a custom value."
                            )
                            for variable in variables:
                                suggestions = []
                                for style_type in variable_suggestions:
                                    if style_type in variable:
                                        suggestions = variable_suggestions[style_type][:]
                                        if "*" + variable in suggestions:
                                            suggestions.remove("*" + variable)
                                        break
                                dropdown = gr.Dropdown(
                                    label=variable,
                                    info=get_docstr(variable),
                                    choices=suggestions,
                                    allow_custom_value=True,
                                )
                                theme_var_input.append(dropdown)
            
            # App

        with gr.Column(scale=6, elem_id="app"):
            with gr.Column(variant="panel"):
                with gr.Accordion("View Code", open=False, visible=False):
                    output_code = gr.Code(language="python")

                with gr.Row():
                    html = gr.Markdown(
                    """
                    ![GreenLake](/file=greenlake.png)
                    """
                    )
                    html2 = gr.Markdown(
                    """
                    ![GreenLake](/file=greenlake.png)
                    """
                    )
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="Chat",
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
        upload_btn.click(
            upload_document, inputs=[document], outputs=[upload_btn, db_progress], )
        # document.change(upload_document, inputs=[document], outputs=[db_progress])
        clear_btn.click
        radio_buttons.change(
            update_ui, 
            radio_buttons, 
            [ctx, manual_options]
        )



        msg.submit(chat_service, inputs, [msg, chatbot])
                

        # Event Listeners

        secret_css = gr.Textbox(visible=False)
        secret_font = gr.JSON(visible=False)

        demo.load(  # doing this via python was not working for some reason, so using this hacky method for now
            None,
            None,
            None,
            js="""() => {
                document.head.innerHTML += "<style id='theme_css'></style>";
                let evt_listener = window.setTimeout(
                    () => {
                        load_theme_btn = document.querySelector('#load_theme');
                        if (load_theme_btn) {
                            load_theme_btn.click();
                            window.clearTimeout(evt_listener);
                        }
                    },
                    100
                );
            }""",
            show_api=False,
        )

        theme_inputs = (
            [primary_hue, secondary_hue, neutral_hue]
            + primary_hues
            + secondary_hues
            + neutral_hues
            + [text_size, spacing_size, radius_size]
            + text_sizes
            + spacing_sizes
            + radius_sizes
            + main_fonts
            + main_is_google
            + mono_fonts
            + mono_is_google
            + theme_var_input
        )

        def load_theme(theme_name):
            theme = [theme for theme in themes if theme.__name__ == theme_name][0]

            parameters = inspect.signature(theme.__init__).parameters
            primary_hue = parameters["primary_hue"].default
            secondary_hue = parameters["secondary_hue"].default
            neutral_hue = parameters["neutral_hue"].default
            text_size = parameters["text_size"].default
            spacing_size = parameters["spacing_size"].default
            radius_size = parameters["radius_size"].default

            theme = theme()

            font = theme._font[:4]
            font_mono = theme._font_mono[:4]
            font_is_google = [isinstance(f, gr.themes.GoogleFont) for f in font]
            font_mono_is_google = [
                isinstance(f, gr.themes.GoogleFont) for f in font_mono
            ]

            def pad_to_4(x):
                return x + [None] * (4 - len(x))

            var_output = []
            for variable in flat_variables:
                theme_val = getattr(theme, variable)
                if theme_val is None and variable.endswith("_dark"):
                    theme_val = getattr(theme, variable[:-5])
                var_output.append(theme_val)

            return (
                [primary_hue.name, secondary_hue.name, neutral_hue.name]
                + primary_hue.expand()
                + secondary_hue.expand()
                + neutral_hue.expand()
                + [text_size.name, spacing_size.name, radius_size.name]
                + text_size.expand()
                + spacing_size.expand()
                + radius_size.expand()
                + pad_to_4([f.name for f in font])
                + pad_to_4(font_is_google)
                + pad_to_4([f.name for f in font_mono])
                + pad_to_4(font_mono_is_google)
                + var_output
            )

        def generate_theme_code(
            base_theme, final_theme, core_variables, final_main_fonts, final_mono_fonts
        ):
            base_theme_name = base_theme
            base_theme = [theme for theme in themes if theme.__name__ == base_theme][
                0
            ]()

            parameters = inspect.signature(base_theme.__init__).parameters
            primary_hue = parameters["primary_hue"].default
            secondary_hue = parameters["secondary_hue"].default
            neutral_hue = parameters["neutral_hue"].default
            text_size = parameters["text_size"].default
            spacing_size = parameters["spacing_size"].default
            radius_size = parameters["radius_size"].default
            font = parameters["font"].default
            font = [font] if not isinstance(font, Iterable) else font
            font = [
                gr.themes.Font(f) if not isinstance(f, gr.themes.Font) else f
                for f in font
            ]
            font_mono = parameters["font_mono"].default
            font_mono = (
                [font_mono] if not isinstance(font_mono, Iterable) else font_mono
            )
            font_mono = [
                gr.themes.Font(f) if not isinstance(f, gr.themes.Font) else f
                for f in font_mono
            ]

            core_diffs = {}
            specific_core_diffs = {}
            core_var_names = [
                "primary_hue",
                "secondary_hue",
                "neutral_hue",
                "text_size",
                "spacing_size",
                "radius_size",
            ]
            for value_name, base_value, source_class, final_value in zip(
                core_var_names,
                [
                    primary_hue,
                    secondary_hue,
                    neutral_hue,
                    text_size,
                    spacing_size,
                    radius_size,
                ],
                [
                    gr.themes.Color,
                    gr.themes.Color,
                    gr.themes.Color,
                    gr.themes.Size,
                    gr.themes.Size,
                    gr.themes.Size,
                ],
                core_variables,
            ):
                if base_value.name != final_value:
                    core_diffs[value_name] = final_value
                source_obj = [
                    obj for obj in source_class.all if obj.name == final_value
                ][0]
                final_attr_values = {}
                diff = False
                for attr in dir(source_obj):
                    if attr in ["all", "name", "expand"] or attr.startswith("_"):
                        continue
                    final_theme_attr = (
                        value_name.split("_")[0]
                        + "_"
                        + (attr[1:] if source_class == gr.themes.Color else attr)
                    )
                    final_attr_values[final_theme_attr] = getattr(
                        final_theme, final_theme_attr
                    )
                    if getattr(source_obj, attr) != final_attr_values[final_theme_attr]:
                        diff = True
                if diff:
                    new_final_attr_values = {}
                    # We need to update the theme keys to match the color and size attribute names
                    for key, val in final_attr_values.items():
                        if key.startswith(("primary_", "secondary_", "neutral_")):
                            color_key = "c" + key.split("_")[-1]
                            new_final_attr_values[color_key] = val
                        elif key.startswith(("text_", "spacing_", "radius_")):
                            size_key = key.split("_")[-1]
                            new_final_attr_values[size_key] = val
                        else:
                            new_final_attr_values[key] = val
                    specific_core_diffs[value_name] = (
                        source_class,
                        new_final_attr_values,
                    )

            font_diffs = {}

            final_main_fonts = [font for font in final_main_fonts if font[0]]
            final_mono_fonts = [font for font in final_mono_fonts if font[0]]
            font = font[:4]
            font_mono = font_mono[:4]
            for base_font_set, theme_font_set, font_set_name in [
                (font, final_main_fonts, "font"),
                (font_mono, final_mono_fonts, "font_mono"),
            ]:
                if len(base_font_set) != len(theme_font_set) or any(
                    base_font.name != theme_font[0]
                    or isinstance(base_font, gr.themes.GoogleFont) != theme_font[1]
                    for base_font, theme_font in zip(base_font_set, theme_font_set)
                ):
                    font_diffs[font_set_name] = [
                        f"gr.themes.GoogleFont('{font_name}')"
                        if is_google_font
                        else f"'{font_name}'"
                        for font_name, is_google_font in theme_font_set
                    ]

            newline = "\n"

            core_diffs_code = ""
            if len(core_diffs) + len(specific_core_diffs) > 0:
                for var_name in core_var_names:
                    if var_name in specific_core_diffs:
                        cls, vals = specific_core_diffs[var_name]
                        core_diffs_code += f"""    {var_name}=gr.themes.{cls.__name__}({', '.join(f'''{k}="{v}"''' for k, v in vals.items())}),\n"""
                    elif var_name in core_diffs:
                        var_val = core_diffs[var_name]
                        if var_name.endswith("_size"):
                            var_val = var_val.split("_")[-1]
                        core_diffs_code += f"""    {var_name}="{var_val}",\n"""

            font_diffs_code = ""

            if len(font_diffs) > 0:
                font_diffs_code = "".join(
                    [
                        f"""    {font_set_name}=[{", ".join(fonts)}],\n"""
                        for font_set_name, fonts in font_diffs.items()
                    ]
                )
            var_diffs = {}
            for variable in flat_variables:
                base_theme_val = getattr(base_theme, variable)
                final_theme_val = getattr(final_theme, variable)
                if base_theme_val is None and variable.endswith("_dark"):
                    base_theme_val = getattr(base_theme, variable[:-5])
                if base_theme_val != final_theme_val:
                    var_diffs[variable] = getattr(final_theme, variable)

            newline = "\n"

            vars_diff_code = ""
            if len(var_diffs) > 0:
                vars_diff_code = f""".set(
    {(',' + newline + "    ").join([f"{k}='{v}'" for k, v in var_diffs.items()])}
)"""

            output = f"""
import gradio as gr

theme = gr.themes.{base_theme_name}({newline if core_diffs_code or font_diffs_code else ""}{core_diffs_code}{font_diffs_code}){vars_diff_code}

with gr.Blocks(theme=theme) as demo:
    ..."""
            return output

        history = gr.State([])
        current_theme = gr.State(None)

        def render_variables(history, base_theme, *args):
            primary_hue, secondary_hue, neutral_hue = args[0:3]
            primary_hues = args[3 : 3 + len(palette_range)]
            secondary_hues = args[3 + len(palette_range) : 3 + 2 * len(palette_range)]
            neutral_hues = args[3 + 2 * len(palette_range) : 3 + 3 * len(palette_range)]
            text_size, spacing_size, radius_size = args[
                3 + 3 * len(palette_range) : 6 + 3 * len(palette_range)
            ]
            text_sizes = args[
                6 + 3 * len(palette_range) : 6
                + 3 * len(palette_range)
                + len(size_range)
            ]
            spacing_sizes = args[
                6 + 3 * len(palette_range) + len(size_range) : 6
                + 3 * len(palette_range)
                + 2 * len(size_range)
            ]
            radius_sizes = args[
                6 + 3 * len(palette_range) + 2 * len(size_range) : 6
                + 3 * len(palette_range)
                + 3 * len(size_range)
            ]
            main_fonts = args[
                6 + 3 * len(palette_range) + 3 * len(size_range) : 6
                + 3 * len(palette_range)
                + 3 * len(size_range)
                + 4
            ]
            main_is_google = args[
                6 + 3 * len(palette_range) + 3 * len(size_range) + 4 : 6
                + 3 * len(palette_range)
                + 3 * len(size_range)
                + 8
            ]
            mono_fonts = args[
                6 + 3 * len(palette_range) + 3 * len(size_range) + 8 : 6
                + 3 * len(palette_range)
                + 3 * len(size_range)
                + 12
            ]
            mono_is_google = args[
                6 + 3 * len(palette_range) + 3 * len(size_range) + 12 : 6
                + 3 * len(palette_range)
                + 3 * len(size_range)
                + 16
            ]
            remaining_args = args[
                6 + 3 * len(palette_range) + 3 * len(size_range) + 16 :
            ]

            final_primary_color = gr.themes.Color(*primary_hues)
            final_secondary_color = gr.themes.Color(*secondary_hues)
            final_neutral_color = gr.themes.Color(*neutral_hues)
            final_text_size = gr.themes.Size(*text_sizes)
            final_spacing_size = gr.themes.Size(*spacing_sizes)
            final_radius_size = gr.themes.Size(*radius_sizes)

            final_main_fonts = []
            font_weights = set()
            for attr, val in zip(flat_variables, remaining_args):
                if "weight" in attr:
                    font_weights.add(val)
            font_weights = sorted(font_weights)

            for main_font, is_google in zip(main_fonts, main_is_google):
                if not main_font:
                    continue
                if is_google:
                    main_font = gr.themes.GoogleFont(main_font, weights=font_weights)
                final_main_fonts.append(main_font)
            final_mono_fonts = []
            for mono_font, is_google in zip(mono_fonts, mono_is_google):
                if not mono_font:
                    continue
                if is_google:
                    mono_font = gr.themes.GoogleFont(mono_font, weights=font_weights)
                final_mono_fonts.append(mono_font)

            theme = gr.themes.Base(
                primary_hue=final_primary_color,
                secondary_hue=final_secondary_color,
                neutral_hue=final_neutral_color,
                text_size=final_text_size,
                spacing_size=final_spacing_size,
                radius_size=final_radius_size,
                font=final_main_fonts,
                font_mono=final_mono_fonts,
            )

            theme.set(**dict(zip(flat_variables, remaining_args)))
            new_step = (base_theme, args)
            if len(history) == 0 or str(history[-1]) != str(new_step):
                history.append(new_step)

            return (
                history,
                theme._get_theme_css(),
                theme._stylesheets,
                generate_theme_code(
                    base_theme,
                    theme,
                    (
                        primary_hue,
                        secondary_hue,
                        neutral_hue,
                        text_size,
                        spacing_size,
                        radius_size,
                    ),
                    list(zip(main_fonts, main_is_google)),
                    list(zip(mono_fonts, mono_is_google)),
                ),
                theme,
            )

        def attach_rerender(evt_listener):
            return evt_listener(
                render_variables,
                [history, base_theme_dropdown] + theme_inputs,
                [history, secret_css, secret_font, output_code, current_theme],
                show_api=False,
            ).then(
                None,
                [secret_css, secret_font],
                None,
                js="""(css, fonts) => {
                    document.getElementById('theme_css').innerHTML = css;
                    let existing_font_links = document.querySelectorAll('link[rel="stylesheet"][href^="https://fonts.googleapis.com/css"]');
                    existing_font_links.forEach(link => {
                        if (fonts.includes(link.href)) {
                            fonts = fonts.filter(font => font != link.href);
                        } else {
                            link.remove();
                        }
                    });
                    fonts.forEach(font => {
                        let link = document.createElement('link');
                        link.rel = 'stylesheet';
                        link.href = font;
                        document.head.appendChild(link);
                    });
                }""",
                show_api=False,
            )

        attach_rerender(
            load_theme_btn.click(
                load_theme, base_theme_dropdown, theme_inputs, show_api=False
            ).then
        )

        for theme_box in (
            text_sizes + spacing_sizes + radius_sizes + main_fonts + mono_fonts
        ):
            attach_rerender(theme_box.blur)
            attach_rerender(theme_box.submit)
        for theme_box in theme_var_input:
            attach_rerender(theme_box.blur)
            attach_rerender(theme_box.select)
        for checkbox in main_is_google + mono_is_google:
            attach_rerender(checkbox.select)

        dark_mode_btn.click(
            None,
            None,
            None,
            js="""() => {
            if (document.querySelectorAll('.dark').length) {
                document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
            } else {
                document.querySelector('body').classList.add('dark');
            }
        }""",
            show_api=False,
        )

        def undo(history_var):
            if len(history_var) <= 1:
                return {history: gr.skip()}
            else:
                history_var.pop()
                old = history_var.pop()
                return [history_var, old[0]] + list(old[1])

        attach_rerender(
            undo_btn.click(
                undo,
                [history],
                [history, base_theme_dropdown] + theme_inputs,
                show_api=False,
            ).then
        )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080, allowed_paths=["./"])
    # demo.launch(allowed_paths=["./"])
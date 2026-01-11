from streamlit.web.bootstrap import run as streamlit_run
import os


def main():
    app_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
    streamlit_run(
        app_path,
        is_hello=False,
        args=[],
        flag_options={},
    )


if __name__ == "__main__":
    main()

from blogwise import create_app
from flask_debugtoolbar import DebugToolbarExtension

app = create_app()
if app.debug:
    DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run()


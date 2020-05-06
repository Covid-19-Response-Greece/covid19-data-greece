"""
@author: Elena Stamatelou
"""
import dash
from layout import layout
from callbacks import register_callbacks
#
#import os
#from flask_caching import Cache

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server
app.layout = layout
register_callbacks(app)

# Main
if __name__ == "__main__":
    app.run_server(debug=False, port=80)

# open app http://127.0.0.1:80/ 


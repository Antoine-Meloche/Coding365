import http.client
import json
from datetime import datetime

import flask
from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def generate_svg():
    user_name: str | None = request.args.get('user')
    if user_name == None:
        user_name = "bob"

    with open('api.token', 'r') as f:
        token = f.read().strip()

    conn = http.client.HTTPSConnection("api.github.com")

    payload = "{\"query\":\"query {\\nuser(login: \\\""+user_name+"\\\") {\\nrepositories(ownerAffiliations: OWNER, isFork: false, first: 100) {\\nnodes {\\nname\\nlanguages(first: 10, orderBy: {field: SIZE, direction: DESC}) {\\nedges{\\nsize\\nnode{\\ncolor\\nname\\n}\\n}\\n}\\n}\\n}\\n}\\n}\"}"

    headers = {
        'Authorization': "bearer "+token,
        'Content-Type': "application/json",
        'Accept': "application/vnd.github.v4.idl",
        'User-Agent': "Github-Streak"
    }

    conn.request("POST", "/graphql", payload, headers)

    res = conn.getresponse()
    data = res.read()

    json_data = json.loads(data.decode("utf-8"))

    repositories = json_data['data']['user']['repositories']['nodes']

    languages: dict = {}

    for repo in repositories:
        for language in repo['languages']['edges']:
            if language['node']['name'] not in languages.keys():
                languages[language['node']['name']] = {
                    'size': language['size'],
                    'color': language['node']['color']
                }
            else:
                languages[language['node']['name']
                          ]['size'] += language['size']
    languages = (dict(sorted(languages.items(),
                 key=lambda item: item[1]['size'], reverse=True)))

    total_size = sum(languages[language]['size'] for language in languages)

    for language in languages:
        languages[language]['width'] = languages[language]['size'] / total_size * 445

    response = flask.Response(f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="495px" height="195px" viewBox="0 0 496 195" fill="none" role="img" aria-labelledby="descId">
        <title id="titleId"/>
        <desc id="descId"/>
        <style>
          .header {{
            font: 600 18px Sans-Serif;
            fill: #bd93f9;
          }}
          @supports(-moz-appearance: auto) {{
            /* Selector detects Firefox */
            .header {{ font-size: 15.5px; }}
          }}
          .lang-name {{ font: 400 11px Sans-Serif; fill: #f8f8f2 }}
        </style>
        <rect data-testid="card-bg" x="0" y="0" rx="4.5" height="100%" stroke="#6272A4" width="495px" fill="#282a36" stroke-opacity="1"/>
        <g data-testid="card-title" transform="translate(25, 35)">
            <g transform="translate(0, 0)">
                <text x="0" y="0" class="header" data-testid="header">Most Used Languages</text>
            </g>
        </g>    

        <g data-testid="main-card-body" transform="translate(0, 55)">
                
            <svg data-testid="lang-items" x="25">
            
                <mask id="rect-mask">
                    <rect x="0" y="0" width="445" height="8" fill="white" rx="5"/>
                </mask>
                {language_bar(languages=languages)}
                {language_list(languages=languages)}
            </svg>
        </g>
    </svg>
    ''', mimetype="image/svg+xml")
    response.headers['Cache-Control'] = 'max-age=1800000'

    return response, 200

def language_bar(languages: dict):
    bar = ""
    used_width = 0
    for language in languages:
        bar += f"<rect mask=\"url(#rect-mask)\" data-testid=\"lang-progress\" x=\"{used_width}\" y=\"0\" width=\"{languages[language]['width']}\" height=\"8\" fill=\"{languages[language]['color']}\"/>"
        used_width += languages[language]['width']
    return bar


def language_list(languages: dict):
    list = ""
    y = 25
    x = 0

    for i, language in enumerate(languages):
        list += f"<g transform=\"translate({x}, {y})\"><g><circle cx=\"5\" cy=\"6\" r=\"5\" fill=\"{languages[language]['color']}\"/><text data-testid=\"lang-name\" x=\"15\" y=\"10\" class=\"lang-name\">{language} {round(languages[language]['width'] / 4.45, ndigits=1)}%</text></g></g>"
        y += 30
        if i in [3, 7, 11]:
            y = 25
            x += 125
        if i == 15:
            break
    
    return list

if __name__ == "__main__":
    app.run()

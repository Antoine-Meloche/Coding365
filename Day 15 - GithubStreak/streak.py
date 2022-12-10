import http.client
import json
from datetime import datetime
import flask
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def generate_svg():
        user_name = request.args.get('user')
        if user_name == None:
            user_name = "bob"

        with open('api.token', 'r') as f:
                token = f.read().strip()

        conn = http.client.HTTPSConnection("api.github.com")

        payload = "{\"query\":\"query {\\n\\tuser(login: \\\""+user_name+"\\\") {\\n\\t\\tcontributionsCollection {\\n\\t\\t\\tcontributionYears\\n\\t\\t}\\n\\t}\\n}\"}"

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

        contributions_years = json_data['data']['user']['contributionsCollection']['contributionYears']

        graphs = []

        total_commits = 0
        for year in contributions_years:
                payload = "{\"query\":\"query {user(login: \\\""+user_name+"\\\") {contributionsCollection(from: \\\""+str(year)+"-01-01T00:00:00Z\\\", to: \\\""+str(year)+"-12-31T23:59:59Z\\\") {contributionCalendar {totalContributions weeks {contributionDays {contributionCount date}}}}}}\"}"
                
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
                graphs.append(json_data)

                total_commits += json_data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']

        graphs = graphs[::-1]


        today = datetime.now().strftime('%F')

        first_contribution = ''
        current_streak_start = ''
        longest_streak_range = ['', '']
        is_done = False
        streak = 0
        longest_streak = 0
        count = 0
        no_streak = True
        prev_day = ''
        last_day = ''
        for graph in graphs:
                for week in graph['data']['user']['contributionsCollection']['contributionCalendar']['weeks']:
                        if is_done:
                                break
                        for day in week['contributionDays']:
                                streak = count
                                if streak > longest_streak:
                                        longest_streak = streak
                                        longest_streak_range[0] = current_streak_start
                                        longest_streak_range[1] = prev_day

                                if day['date'] == today:
                                        if day['contributionCount'] > 0:
                                                streak += 1
                                                last_day = day['date']
                                                if streak > longest_streak:
                                                        longest_streak = streak
                                                        longest_streak_range[0] = current_streak_start
                                                        longest_streak_range[1] = day['date']
                                        is_done = True
                                        break

                                if day['contributionCount'] > 0:
                                        if first_contribution == '':
                                                first_contribution = day['date']
                                        count = 1+streak
                                        prev_day = day['date']
                                        last_day = day['date']
                                        if no_streak:
                                                current_streak_start = day['date']
                                                no_streak = False
                                else:
                                        count = 0
                                        no_streak = True


        #print(total_commits)
        #print(f'{streak}: {current_streak_start}-{today}')
        #print(f'{longest_streak}: {longest_streak_range[0]}-{longest_streak_range[1]}')

        return flask.Response(f"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' style='isolation: isolate' viewBox='0 0 495 195' width='495px' height='195px' direction='ltr'><style>@keyframes currstreak {{0% {{ font-size: 3px; opacity: 0.2; }}80% {{ font-size: 34px; opacity: 1; }}100% {{ font-size: 28px; opacity: 1; }}}}@keyframes fadein {{0% {{ opacity: 0; }}100% {{ opacity: 1; }}}}</style><defs><clipPath id='outer_rectangle'><rect width='495' height='195' rx='4.5'/></clipPath><mask id='mask_out_ring_behind_fire'><rect width='495' height='195' fill='white'/><ellipse id='mask-ellipse' cx='247.5' cy='32' rx='13' ry='18' fill='black'/></mask></defs><g clip-path='url(#outer_rectangle)'><g style='isolation: isolate'><rect stroke='#e4e2e2' fill='#282a36' rx='4.5' x='0.5' y='0.5' width='494' height='194'/></g><g style='isolation: isolate'><line x1='330' y1='28' x2='330' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#e4e2e2' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/><line x1='165' y1='28' x2='165' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#e4e2e2' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/></g><g style='isolation: isolate'><!-- Total Contributions Big Number --><g transform='translate(1,48)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>{total_commits}</text></g><!-- Total Contributions Label --><g transform='translate(1,84)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.7s'>Total Contributions</text></g><!-- total contributions range --><g transform='translate(1,114)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.8s'>{first_contribution} - Present</text></g></g><g style='isolation: isolate'><!-- Current Streak Big Number --><g transform='translate(166,48)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#79dafa' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='animation: currstreak 0.6s linear forwards'>{streak}</text></g><!-- Current Streak Label --><g transform='translate(166,108)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#79dafa' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>Current Streak</text></g><!-- Current Streak Range --><g transform='translate(166,145)'><text x='81.5' y='21' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>{current_streak_start} - {last_day}</text></g><!-- ring around number --><g mask='url(#mask_out_ring_behind_fire)'><circle cx='247.5' cy='71' r='40' fill='none' stroke='#ff6e96' stroke-width='5' style='opacity: 0; animation: fadein 0.5s linear forwards 0.4s'></circle></g><!-- fire icon --><g stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'><path d=' M 235.5 19.5 L 259.5 19.5 L 259.5 43.5 L 235.5 43.5 L 235.5 19.5 Z ' fill='none'/><path d=' M 249 20.17 C 249 20.17 249.74 22.82 249.74 24.97 C 249.74 27.03 248.39 28.7 246.33 28.7 C 244.26 28.7 242.7 27.03 242.7 24.97 L 242.73 24.61 C 240.71 27.01 239.5 30.12 239.5 33.5 C 239.5 37.92 243.08 41.5 247.5 41.5 C 251.92 41.5 255.5 37.92 255.5 33.5 C 255.5 28.11 252.91 23.3 249 20.17 Z  M 247.21 38.5 C 245.43 38.5 243.99 37.1 243.99 35.36 C 243.99 33.74 245.04 32.6 246.8 32.24 C 248.57 31.88 250.4 31.03 251.42 29.66 C 251.81 30.95 252.01 32.31 252.01 33.7 C 252.01 36.35 249.86 38.5 247.21 38.5 Z ' fill='#ff6e96' stroke-opacity='0'/></g></g><g style='isolation: isolate'><!-- Longest Streak Big Number --><g transform='translate(331,48)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.2s'>{longest_streak}</text></g><!-- Longest Streak Label --><g transform='translate(331,84)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe , Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.3s'>Longest Streak</text></g><!-- Longest Streak Range --><g transform='translate(331,114)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.4s'>{longest_streak_range[0]} - {longest_streak_range[1]}</text></g></g></g></svg>", mimetype='image/svg+xml'), 200

if __name__ == '__main__':
    app.run()

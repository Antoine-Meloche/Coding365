let options = {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: " bearer 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",
    Accept: "application/vnd.github.v4.idl",
  },
  body: JSON.stringify({
    query: `
    query {
      user(login: "Antoine-Meloche") {
        contributionsCollection {
          contributionYears
        }
      }
    }`,
  }),
};

fetch("https://api.github.com/graphql", options)
  .then((response) => response.json())
  .then((data) => {
    let contributionYears =
      data.data.user.contributionsCollection.contributionYears;

    const getTotalCommits = async () => {
      let totalCommits = 0;
      let graphs = [];
      for (const year of contributionYears) {
        options.body = JSON.stringify({
          query: `
        query {
          user(login: "Antoine-Meloche") {
            contributionsCollection(from: "${year}-01-01T00:00:00Z", to: "${year}-12-31T23:59:59") {
              contributionCalendar {
                totalContributions weeks {
                  contributionDays {
                    contributionCount date
                  }
                }
          }
        }
      }
    }`,
        });
        await fetch("https://api.github.com/graphql", options)
          .then((response) => response.json())
          .then((data) => {
            totalCommits +=
              data.data.user.contributionsCollection.contributionCalendar
                .totalContributions;
            graphs.push(data);
          });
      }
      return [totalCommits, graphs];
    };
    getTotalCommits().then((returnValue) => {
      totalCommits = returnValue[0];
      graphs = returnValue[1];

      let today = new Date();

      let firstContribution = "";
      let streakCount = 0;
      let newStreakCount = 0;
      let counting = true;
      let longestStreak = 0;
      let longestStreakStart = "";
      graphs.reverse();
      for (const graph of graphs) {
        if (!counting) {
          break;
        }

        for (const week of graph.data.user.contributionsCollection
          .contributionCalendar.weeks) {
          if (!counting) {
            break;
          }

          for (const day of week.contributionDays) {
            streakCount = newStreakCount;

            if (streakCount > longestStreak) {
              longestStreak = streakCount;
              longestStreakStart = currentStreakStart;
            }

            if (firstContribution == "" && day.contributionCount > 0) {
              firstContribution = day.date;
            }

            let date = new Date(day.date);
            date.setDate(date.getDate() + 1);
            if (day.contributionCount > 0) {
              if (streakCount == 0) {
                currentStreakStart = day.date;
              }
              newStreakCount++;
              lastDay = day.date;
            } else {
              newStreakCount = 0;
            }

            if (
              date.getFullYear() == today.getFullYear() &&
              date.getMonth() == today.getMonth() &&
              date.getDate() == today.getDate()
            ) {
              if (streakCount < newStreakCount) {
                streakCount = newStreakCount;
                lastDay = day.date;
                if (streakCount > longestStreak) {
                  longestStreak = streakCount;
                  longestStreakStart = currentStreakStart;
                }
              }
              counting = false;
              break;
            }
          }
        }
      }

      let date = new Date(longestStreakStart);
      date.setDate(date.getDate()+longestStreak);
      let longestStreakEnd = `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate().toString().padStart(2, "0")}`

      document.body.innerHTML = `
      <svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' style='isolation: isolate' viewBox='0 0 495 195' width='495px' height='195px' direction='ltr'>
      <style>
        @keyframes currstreak {
          0% { font-size: 3px; opacity: 0.2; }
          80% { font-size: 34px; opacity: 1; }
          100% { font-size: 28px; opacity: 1; }
        }
        @keyframes fadein {
          0% { opacity: 0; }
          100% { opacity: 1; }
        }
      </style>
      <defs>
      <clipPath id='outer_rectangle'>
      <rect width='495' height='195' rx='4.5'/>
      </clipPath><mask id='mask_out_ring_behind_fire'>
      <rect width='495' height='195' fill='white'/>
      <ellipse id='mask-ellipse' cx='247.5' cy='32' rx='13' ry='18' fill='black'/>
      </mask>
      </defs>
      <g clip-path='url(#outer_rectangle)'>
      <g style='isolation: isolate'><rect stroke='#e4e2e2' fill='#282a36' rx='4.5' x='0.5' y='0.5' width='494' height='194'/>
      </g>
      <g style='isolation: isolate'><line x1='330' y1='28' x2='330' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#e4e2e2' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
      <line x1='165' y1='28' x2='165' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#e4e2e2' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
      </g>
      <g style='isolation: isolate'>
      <!-- Total Contributions Big Number -->
      <g transform='translate(1,48)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
        ${totalCommits}
      </text>
      </g>
      <!-- Total Contributions Label -->
      <g transform='translate(1,84)'><text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.7s'>Total Contributions</text></g>
      <!-- total contributions range -->
      <g transform='translate(1,114)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.8s'>
        ${firstContribution} - Present
      </text>
      </g>
      </g>
      <g style='isolation: isolate'>
      <!-- Current Streak Big Number -->
      <g transform='translate(166,48)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#79dafa' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='animation: currstreak 0.6s linear forwards'>
        ${streakCount}
      </text>
      </g>
      <!-- Current Streak Label -->
      <g transform='translate(166,108)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#79dafa' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>Current Streak</text>
      </g>
      <!-- Current Streak Range -->
      <g transform='translate(166,145)'>
      <text x='81.5' y='21' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>
        ${currentStreakStart} - ${lastDay}
      </text>
      </g>
      <!-- ring around number -->
      <g mask='url(#mask_out_ring_behind_fire)'>
      <circle cx='247.5' cy='71' r='40' fill='none' stroke='#ff6e96' stroke-width='5' style='opacity: 0; animation: fadein 0.5s linear forwards 0.4s'>
      </circle>
      </g>
      <!-- fire icon -->
      <g stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
      <path d=' M 235.5 19.5 L 259.5 19.5 L 259.5 43.5 L 235.5 43.5 L 235.5 19.5 Z ' fill='none'/>
      <path d=' M 249 20.17 C 249 20.17 249.74 22.82 249.74 24.97 C 249.74 27.03 248.39 28.7 246.33 28.7 C 244.26 28.7 242.7 27.03 242.7 24.97 L 242.73 24.61 C 240.71 27.01 239.5 30.12 239.5 33.5 C 239.5 37.92 243.08 41.5 247.5 41.5 C 251.92 41.5 255.5 37.92 255.5 33.5 C 255.5 28.11 252.91 23.3 249 20.17 Z  M 247.21 38.5 C 245.43 38.5 243.99 37.1 243.99 35.36 C 243.99 33.74 245.04 32.6 246.8 32.24 C 248.57 31.88 250.4 31.03 251.42 29.66 C 251.81 30.95 252.01 32.31 252.01 33.7 C 252.01 36.35 249.86 38.5 247.21 38.5 Z ' fill='#ff6e96' stroke-opacity='0'/>
      </g>
      </g>
      <g style='isolation: isolate'>
      <!-- Longest Streak Big Number -->
      <g transform='translate(331,48)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.2s'>
        ${longestStreak}
      </text>
      </g>
      <!-- Longest Streak Label -->
      <g transform='translate(331,84)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#ff6e96' stroke='none' font-family='Segoe , Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.3s'>Longest Streak</text>
      </g>
      <!-- Longest Streak Range -->
      <g transform='translate(331,114)'>
      <text x='81.5' y='32' stroke-width='0' text-anchor='middle' fill='#f8f8f2' stroke='none' font-family='Segoe UI, Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.4s'>
        ${longestStreakStart} - ${longestStreakEnd}
      </text>
      </g>
      </g>
      </g>
      </svg>`;
    });
  });

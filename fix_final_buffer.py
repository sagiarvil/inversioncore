import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_code = """        }
        termBox.innerHTML = formatHarmoniousColors(accumulated);
        document.getElementById('speedBadge').textContent = `TAMAMLANDI (${((performance.now() - t0) / 1000).toFixed(1)}s)`;"""

new_code = """        }
        if (buffer.trim().startsWith("data: ")) {
          const dataStr = buffer.trim().slice(6).trim();
          if (dataStr !== "[DONE]") {
            try {
              const parsed = JSON.parse(dataStr);
              const delta = parsed.choices?.[0]?.delta?.content || "";
              accumulated += delta;
            } catch(e) {}
          }
        }
        termBox.innerHTML = formatHarmoniousColors(accumulated);
        document.getElementById('speedBadge').textContent = `TAMAMLANDI (${((performance.now() - t0) / 1000).toFixed(1)}s)`;"""

if old_code in html:
    html = html.replace(old_code, new_code)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Buffer flush logic added.")
else:
    print("Could not find old code.")

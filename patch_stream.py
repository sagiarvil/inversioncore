import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_stream_code = """        let accumulated = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const dataStr = line.slice(6).trim();
              if (dataStr === "[DONE]") break;
              try {
                const parsed = JSON.parse(dataStr);
                const delta = parsed.choices?.[0]?.delta?.content || "";
                accumulated += delta;
                termBox.innerHTML = formatHarmoniousColors(accumulated) + '<span class="blinking-cursor"></span>';
                termBox.scrollTop = termBox.scrollHeight;
                document.getElementById('speedBadge').textContent = `CANLI AKIŞ: ${((performance.now() - t0) / 1000).toFixed(1)}s`;
              } catch (e) {}
            }
          }
        }"""

new_stream_code = """        let accumulated = "";
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\\n");
          buffer = lines.pop(); 
          for (const line of lines) {
            if (line.trim().startsWith("data: ")) {
              const dataStr = line.trim().slice(6).trim();
              if (dataStr === "[DONE]") break;
              try {
                const parsed = JSON.parse(dataStr);
                const delta = parsed.choices?.[0]?.delta?.content || "";
                accumulated += delta;
                termBox.innerHTML = formatHarmoniousColors(accumulated) + '<span class="blinking-cursor"></span>';
                termBox.scrollTop = termBox.scrollHeight;
                document.getElementById('speedBadge').textContent = `CANLI AKIŞ: ${((performance.now() - t0) / 1000).toFixed(1)}s`;
              } catch (e) {}
            }
          }
        }"""

if old_stream_code in html:
    html = html.replace(old_stream_code, new_stream_code)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Stream logic patched successfully.")
else:
    print("Could not find old stream code.")

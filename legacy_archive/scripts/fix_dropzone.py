import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the first block
first_block = """    const dropZone = document.getElementById('dropZone');
    const inputArea = document.getElementById('inputArea');

    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); if (!dropZone.contains(e.relatedTarget)) dropZone.classList.remove('dragover'); });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault(); dropZone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => { inputArea.value = `[DOSYA İÇERİĞİ: ${file.name}]\\n\\n` + evt.target.result; };
      reader.readAsText(file);
    });"""

if first_block in html:
    html = html.replace(first_block, "    const inputArea = document.getElementById('inputArea');")
else:
    print("Could not find first block")

# Rename the second block dropZone to mainDropZone
second_block = """    const dropZone = document.getElementById('dropOverlay').parentElement;
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); document.getElementById('dropOverlay').classList.add('bg-indigo-50/80'); });
    dropZone.addEventListener('dragleave', () => { document.getElementById('dropOverlay').classList.remove('bg-indigo-50/80'); });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      document.getElementById('dropOverlay').classList.remove('bg-indigo-50/80');"""

second_block_new = """    const mainDropZone = document.getElementById('dropOverlay').parentElement;
    mainDropZone.addEventListener('dragover', (e) => { e.preventDefault(); document.getElementById('dropOverlay').classList.add('bg-indigo-50/80'); });
    mainDropZone.addEventListener('dragleave', () => { document.getElementById('dropOverlay').classList.remove('bg-indigo-50/80'); });
    mainDropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      document.getElementById('dropOverlay').classList.remove('bg-indigo-50/80');"""

if second_block in html:
    html = html.replace(second_block, second_block_new)
else:
    print("Could not find second block")

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("dropZone issues fixed.")

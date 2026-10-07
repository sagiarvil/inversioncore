import os
import json
import urllib.request
import urllib.error
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input_text: str
    system_prompt: str
    history: list
    draft: str
    critique: str
    loop_count: int
    final_response: str
    passed: bool

def call_llm(messages: list, max_tokens: int = 1200) -> str:
    # 1. PRIMARY: Qwen Local 8080
    try:
        req_data = json.dumps({
            "model": "qwen",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.85
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "http://127.0.0.1:8080/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=90) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            return res_json['choices'][0]['message']['content']
            
    except Exception as alfa_err:
        print(f"[ALFA SUNUCUSU HATASI: {alfa_err}]")
        return f"[MOTOR ÇÖKTÜ: {alfa_err}]"

def generator_node(state: AgentState):
    input_text = state["input_text"]
    critique = state.get("critique", "")
    sys_prompt = state.get("system_prompt", "Sen acımasız ve tavizsiz bir tersine mühendislik uzmanısın.")
    history = state.get("history", [])
    
    if critique:
        system_instruction = f"{sys_prompt}\nDİKKAT! Önceki taslağın şu eleştirileri aldı: {critique}\nBunu tamamen yok et. Metni BAŞTAN YAZ. Çok daha DENGESİZ, uzun, felsefi ve derin ol. Markdown (koyu, liste, başlık) kullan."
    else:
        system_instruction = f"{sys_prompt}\nLÜTFEN ÇOK UZUN, DETAYLI VE SARSICI BİR ANALİZ YAZ. Başlıklar, listeler ve kalın metinler (Markdown) kullanarak yapılandır. Kullanıcıya net bir reçete sun."
        
    messages = [{"role": "system", "content": system_instruction}]
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": input_text})
    
    draft = call_llm(messages)
    return {"draft": draft, "loop_count": state.get("loop_count", 0) + 1}

def critic_node(state: AgentState):
    draft = state["draft"]
    
    evaluation_prompt = f"Sen 'Acımasızlık Denetçisi'sin.\nAşağıdaki metin kullanıcının illüzyonlarını parçalamalıdır.\n\nMETİN:\n{draft}\n\nGÖREV:\n1. Metinde empati, acıma, 'Anlıyorum' gibi zayıf kelimeler var mı?\n2. Metin yeterince UZUN, ukala ve sarsıcı mı?\n3. Markdown (başlık, kalın yazı, listeler) iyi kullanılmış mı?\n\nEğer metin KUSURSUZ ise sadece 'GEÇTİ' yaz. Değilse, çok kısa eleştiri yaz (Örn: 'REDDEDİLDİ: Çok kısa ve kibar')."

    eval_result = call_llm([{"role": "user", "content": evaluation_prompt}], max_tokens=300)
    
    if "GEÇTİ" in eval_result.upper() and "REDDEDİLDİ" not in eval_result.upper():
        return {"passed": True, "critique": "", "final_response": draft}
    else:
        return {"passed": False, "critique": eval_result}

def router(state: AgentState):
    if state.get("passed", False) or state.get("loop_count", 0) >= 1:
        return "end"
    return "generator"

workflow = StateGraph(AgentState)
workflow.add_node("generator", generator_node)
workflow.add_node("critic", critic_node)
workflow.set_entry_point("generator")
workflow.add_edge("generator", "critic")
workflow.add_conditional_edges("critic", router, {"end": END, "generator": "generator"})

inversion_psychopath_app = workflow.compile()

def run_psychopath_analysis(input_text: str, system_prompt: str) -> str:
    final_state = inversion_psychopath_app.invoke({
        "input_text": input_text,
        "system_prompt": system_prompt,
        "history": [],
        "loop_count": 0,
        "passed": False,
        "draft": "",
        "critique": "",
        "final_response": ""
    })
    return final_state.get("final_response", final_state.get("draft"))

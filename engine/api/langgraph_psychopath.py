import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from litellm import completion

class AgentState(TypedDict):
    input_text: str
    system_prompt: str
    draft: str
    critique: str
    loop_count: int
    final_response: str
    passed: bool

def call_llm(prompt: str, model_name: str = "deepseek/deepseek-flash", max_tokens: int = 2500) -> str:
    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.8,
            api_key=os.environ.get("DEEPSEEK_API_KEY", "dummy"),
            api_base="https://api.deepseek.com"
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM Çağrı Hatası: {e}")
        return f"[MİMARİ HATA: {str(e)}]"

def generator_node(state: AgentState):
    input_text = state["input_text"]
    critique = state.get("critique", "")
    sys_prompt = state.get("system_prompt", "Sen acımasız ve tavizsiz bir tersine mühendislik uzmanısın.")
    
    if critique:
        system_instruction = f"""{sys_prompt}
DİKKAT! Önceki taslağın şu psikolojik eleştirileri aldı: 
{critique}

Bu zayıflıkları tamamen yok et. Metni baştan yaz. Kesinlikle empati gösterme. Daha zeki, daha yıkıcı ve narsist ol. Felsefi alıntılar ve kök neden analizine sadık kal."""
    else:
        system_instruction = sys_prompt
        
    prompt = f"{system_instruction}\n\nKULLANICI GİRDİSİ:\n{input_text}"
    
    draft = call_llm(prompt)
    return {"draft": draft, "loop_count": state.get("loop_count", 0) + 1}

def critic_node(state: AgentState):
    draft = state["draft"]
    
    evaluation_prompt = f"""Sen bir "Acımasızlık ve Gerçeklik Denetçisi"sin (Kırmızı Takım).
Aşağıdaki metni incele. Metin, psikopatolojik bir dürüstlükle kullanıcının illüzyonlarını parçalamalıdır.

METİN:
{draft}

GÖREV:
1. Metinde empati, acıma, teselli veya "Anlıyorum, haklısın" gibi zayıf kelimeler var mı?
2. Metin yeterince ukala, zeki, felsefi ve sarsıcı mı? 
3. 'Via Negativa' kuralına uymuş mu? (Neyin eksiltilmesi gerektiğine odaklanmış mı?)

Eğer metin KUSURSUZ derecede acımasız, felsefi ve analitikse sadece 'GEÇTİ' yaz. 
Eğer metin zayıf, kibar veya standart bir asistan gibi hissettiriyorsa, düzeltilmesi gereken yerleri çok kısa bir eleştiri olarak yaz (Örn: 'REDDEDİLDİ: 2. paragraf çok yumuşak. Tavsiye veriyorsun, tavsiye verme, gerçeği yüzüne çarp.')"""

    eval_result = call_llm(evaluation_prompt, max_tokens=500)
    
    if "GEÇTİ" in eval_result.upper() and "REDDEDİLDİ" not in eval_result.upper():
        return {"passed": True, "critique": "", "final_response": draft}
    else:
        return {"passed": False, "critique": eval_result}

def router(state: AgentState):
    if state.get("passed", False) or state.get("loop_count", 0) >= 3:
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
        "loop_count": 0,
        "passed": False,
        "draft": "",
        "critique": "",
        "final_response": ""
    })
    
    return final_state.get("final_response", final_state.get("draft"))


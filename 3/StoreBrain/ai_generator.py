import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# هنا سنستخدم مفتاح الذكاء الاصطناعي (سأعلمك كيف تحصل عليه في الخطوة القادمة)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_product_details(user_input):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    أنت خبير تسويق إلكتروني. قم بكتابة تفاصيل منتج بناءً على هذا الوصف البسيط: {user_input}
    المطلوب هو الرد بتنسيق محدد جداً كالتالي:
    TITLE: [اسم المنتج الجذاب هنا]
    DESCRIPTION: [وصف تسويقي مقنع باللغة العربية مع مميزات المنتج]
    TAGS: [كلمات دلالية مفصولة بفاصلة]
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    test_input = "ساعة ذكية رياضية"
    print("🤖 AI is thinking...")
    result = generate_product_details(test_input)
    print("\n--- AI Suggestion ---\n")
    print(result)
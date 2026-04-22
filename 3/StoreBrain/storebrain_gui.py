import os
import requests
import json
import urllib.parse
import threading
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# ==========================================================
# 1. إعدادات النظام والترميز (تهيئة بيئة التشغيل لملفات EXE)
# ==========================================================
# هذا الجزء يضمن عدم حدوث خطأ NoneType عند تشغيل البرنامج بدون شاشة سوداء
if sys.stdout is not None:
    try:
        # محاولة فرض ترميز UTF-8 لدعم اللغة العربية في السجلات الخفية
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError as attr_err:
        # في حال كان إصدار بايثون لا يدعم إعادة التكوين
        pass 
    except Exception as general_err:
        # تجاوز أي خطأ آخر لتجنب توقف البرنامج عند التشغيل
        pass 

# تحميل متغيرات البيئة من ملف .env الموجود في مجلد البرنامج
load_dotenv()

# استخراج إعدادات الربط والتأكد من تحميلها من الذاكرة
GROQ_KEY = os.getenv("GROQ_API_KEY")
SHOPIFY_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOP_URL = os.getenv('SHOP_URL')
SHOPIFY_API_VERSION = "2024-04"

# ==========================================================
# 2. الفئة الرئيسية للنظام (StoreBrain AI - v13 The Ultimate Empire)
# ==========================================================
class StoreBrainEmpire:
    def __init__(self, root):
        self.root = root
        self.root.title("StoreBrain AI v13 - The Ultimate Unabridged Empire")
        self.root.geometry("850x850")
        self.root.configure(bg="#2c3e50")
        
        # --------------------------------------------------------
        # أحداث التزامن بين الخيوط (Thread Safety) - لحل خطأ Tkinter
        # --------------------------------------------------------
        self.price_event = threading.Event()
        self.current_price = None

        # إعداد الأنماط المرئية للواجهة (Themes)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#2c3e50", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="white", font=("Segoe UI", 11))
        
        # --- الهيدر العلوي ---
        header = tk.Label(
            root, 
            text="👑 StoreBrain AI - النسخة الإمبراطورية v13 المفصلة", 
            font=("Segoe UI", 22, "bold"), 
            bg="#1a252f", 
            fg="#2ecc71", 
            pady=30
        )
        header.pack(fill="x")

        # حاوية العناصر المركزية
        container = tk.Frame(root, bg="#2c3e50")
        container.pack(pady=10, padx=50, fill="x")

        # --- قسم إدارة المدخلات والروابط ---
        input_frame = tk.LabelFrame(
            container, 
            text="📦 مدخلات المنتجات والروابط", 
            bg="#2c3e50", 
            fg="#bdc3c7", 
            font=("Segoe UI", 11, "bold"), 
            pady=15, 
            padx=15
        )
        input_frame.pack(fill="x", pady=10)

        # زر التحميل الجماعي
        self.btn_bulk = tk.Button(
            input_frame, 
            text="📂 تحميل قائمة روابط من ملف (.txt)", 
            bg="#3498db", 
            fg="white", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            cursor="hand2", 
            command=self.load_bulk_file
        )
        self.btn_bulk.pack(side="top", fill="x", pady=(0, 10))

        # حقل إدخال الرابط الفردي
        ttk.Label(input_frame, text="أو ألصق رابط منتج فردي للرفع الفوري:").pack(anchor="w")
        self.entry_url = ttk.Entry(input_frame)
        self.entry_url.pack(fill="x", pady=5)
        self.entry_url.insert(0, "https://aliExpress.com/item/...")
        
        # تفعيل وظيفة الزر الأيمن للفأرة في حقل الإدخال
        self.setup_context_menu(self.entry_url) 

        # --- قسم إعدادات الربح والتسعير الآلي ---
        pricing_frame = tk.LabelFrame(
            container, 
            text="💰 معادلة الربح الذكية", 
            bg="#2c3e50", 
            fg="#bdc3c7", 
            font=("Segoe UI", 11, "bold"), 
            pady=15, 
            padx=15
        )
        pricing_frame.pack(fill="x", pady=10)

        # شبكة حقول الأرقام
        grid_frame = tk.Frame(pricing_frame, bg="#2c3e50")
        grid_frame.pack()

        # حقل معامل الربح
        tk.Label(grid_frame, text="معامل الربح (Markup):", bg="#2c3e50", fg="white").grid(row=0, column=1, sticky="e", padx=10, pady=5)
        self.markup_entry = ttk.Entry(grid_frame, width=15)
        self.markup_entry.insert(0, "2.5")
        self.markup_entry.grid(row=0, column=0, pady=5)

        # حقل تكلفة الشحن
        tk.Label(grid_frame, text="تكلفة الشحن الثابتة ($):", bg="#2c3e50", fg="white").grid(row=1, column=1, sticky="e", padx=10, pady=5)
        self.shipping_entry = ttk.Entry(grid_frame, width=15)
        self.shipping_entry.insert(0, "5.0")
        self.shipping_entry.grid(row=1, column=0, pady=5)

        # --- زر البدء الرئيسي ---
        self.btn_run = tk.Button(
            root, 
            text="🚀 إطلاق عملية الأتمتة الشاملة", 
            font=("Segoe UI", 16, "bold"), 
            bg="#27ae60", 
            fg="white",
            activebackground="#2ecc71", 
            relief="raised", 
            cursor="hand2", 
            command=self.start_process_thread
        )
        self.btn_run.pack(pady=25, ipadx=70, ipady=15)

        # --- شاشة سجل العمليات (Console Log) ---
        log_label = tk.Label(root, text="🖥️ حالة النظام والعمليات الحالية:", bg="#2c3e50", fg="#bdc3c7", font=("Segoe UI", 10))
        log_label.pack(anchor="w", padx=50)
        
        self.log_text = tk.Text(
            root, 
            height=12, 
            bg="#1e1e1e", 
            fg="#00ff00", 
            font=("Consolas", 10), 
            padx=15, 
            pady=15, 
            state="disabled"
        )
        self.log_text.pack(padx=50, fill="x", pady=(0, 20))

        # تهيئة المتغيرات الأساسية للنظام
        self.links_list = []
        self.desktop_img_path = self.prepare_image_folder()
        
        # إجراء فحص الاتصال الأولي بالمفاتيح
        self.initial_check()

    # ==========================================================
    # 3. الدوال البرمجية (Logic Functions) بالتفصيل الكامل
    # ==========================================================

    def prepare_image_folder(self):
        """تجهيز مجلد الصور على سطح المكتب لحفظ نتائج الذكاء الاصطناعي"""
        user_profile = os.environ.get('USERPROFILE', '')
        desktop_path = os.path.join(user_profile, 'Desktop')
        final_path = os.path.join(desktop_path, 'StoreBrain_Images')
        
        # إنشاء المجلد إذا لم يكن موجوداً
        if not os.path.exists(final_path):
            os.makedirs(final_path)
            
        return final_path

    def setup_context_menu(self, widget):
        """إضافة وظيفة القص والنسخ واللصق بيمين الفأرة لحقل الإدخال"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="قص (Cut)", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="نسخ (Copy)", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="لصق (Paste)", command=lambda: widget.event_generate("<<Paste>>"))
        
        def do_popup(event):
            menu.tk_popup(event.x_root, event.y_root)
            
        widget.bind("<Button-3>", do_popup)

    def log(self, message):
        """كتابة الرسائل في سجل البرنامج بالواجهة مع طابع زمني"""
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%H:%M:%S")
        
        # تفعيل الحقل للكتابة ثم إغلاقه مجدداً
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        # تحديث الواجهة لتظهر التغييرات فوراً
        self.root.update()

    def initial_check(self):
        """فحص وجود مفاتيح الاتصال في ملف البيئة .env"""
        if not GROQ_KEY or not SHOPIFY_TOKEN or not SHOP_URL:
            self.log("❌ تنبيه حرج: لم يتم العثور على إعدادات .env كاملة بجوار البرنامج.")
        else:
            self.log("✅ جميع المحركات (Llama 3.3 & Shopify) متصلة وجاهزة للعمل.")

    def load_bulk_file(self):
        """قراءة روابط المنتجات من ملف خارجي نصي"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # تنظيف القائمة من الأسطر الفارغة
                self.links_list = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line:
                        self.links_list.append(stripped_line)
                        
            self.log(f"📋 تم استيراد قائمة تحتوي على {len(self.links_list)} رابط بنجاح.")

    def start_process_thread(self):
        """تشغيل العمليات في خلفية البرنامج لضمان عدم توقف واجهة المستخدم"""
        url_input = self.entry_url.get().strip()
        
        # تحديد الروابط: إما من الملف المحمل أو من الحقل المباشر
        final_links = []
        if self.links_list:
            final_links = self.links_list
        else:
            if "http" in url_input:
                final_links = [url_input]
        
        # التحقق من وجود روابط قابلة للعمل
        if not final_links:
            messagebox.showwarning("تنبيه", "يرجى إدخال رابط أو تحميل ملف روابط أولاً!")
            return

        # ميزة تفريغ الحقل التلقائي استعداداً للرابط التالي
        self.entry_url.delete(0, tk.END)

        # تعطيل زر التشغيل لتجنب تشغيل عمليات متداخلة
        self.btn_run.config(state="disabled", bg="#7f8c8d")
        self.log("="*60)
        
        # إطلاق خيط المعالجة (Thread) المستقل
        processing_thread = threading.Thread(target=self.main_execution_loop, args=(final_links,))
        processing_thread.daemon = True
        processing_thread.start()

    # ==========================================================
    # 4. دوال التزامن لحل مشكلة توقف الواجهة (Thread Safety)
    # ==========================================================

    def _show_price_dialog_in_main_thread(self, product_name):
        """هذه الدالة تُنفذ داخل الواجهة الرئيسية (Main Thread) فقط لتجنب انهيار Tkinter"""
        prompt_text = f"أدخل سعر المورد للمنتج:\n{product_name}"
        self.current_price = simpledialog.askfloat("تأكيد السعر", prompt_text, parent=self.root)
        
        # إرسال إشارة للخيط الخلفي بأن المستخدم أدخل السعر ويمكنه إكمال العمل
        self.price_event.set()

    def get_supplier_price_safe(self, product_name):
        """هذه الدالة توقف الخيط الخلفي وتطلب من الواجهة عرض نافذة السعر بأمان"""
        self.price_event.clear()
        
        # جدولة عرض النافذة في الواجهة الرئيسية فوراً
        self.root.after(0, self._show_price_dialog_in_main_thread, product_name)
        
        # إيقاف الخيط الخلفي مؤقتاً حتى يقوم المستخدم بإدخال السعر
        self.price_event.wait()
        
        return self.current_price

    # ==========================================================
    # 5. الدورة البرمجية الأساسية
    # ==========================================================

    def main_execution_loop(self, links):
        """الدورة البرمجية الشاملة لمعالجة كافة الروابط في القائمة"""
        self.log(f"🚀 بدء معالجة أتمتة لـ {len(links)} منتج...")
        
        for index, url in enumerate(links):
            current_item_number = index + 1
            total_items = len(links)
            self.log(f"🔄 جاري العمل على المنتج رقم ({current_item_number}/{total_items})")
            
            # استدعاء دالة معالجة المنتج الفردي
            success = self.process_single_product(url)
            
            if not success:
                self.log(f"⚠️ تم تخطي المنتج بسبب أخطاء أو إلغاء من المستخدم.")
                
            self.log("-" * 40)
            
        self.log("🏁 انتهت المهمة الإمبراطورية لكافة المنتجات بنجاح!")
        # إعادة تفعيل زر التشغيل بعد الانتهاء
        self.btn_run.config(state="normal", bg="#27ae60")

    def process_single_product(self, product_url):
        """خطوات معالجة منتج واحد من السحب وحتى الرفع في شوبيفاي"""
        try:
            # 1. الاتصال بصفحة المنتج لسحب الاسم بشكل آمن ومدرع
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(product_url, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # استخراج الاسم وتجنب خطأ NoneType إذا كانت الصفحة فارغة
            raw_title = "منتج مستورد رائع"
            if soup.title is not None:
                if soup.title.text is not None:
                    cleaned_title = soup.title.text.strip()
                    if cleaned_title != "":
                        raw_title = cleaned_title[:75]
            
            # 2. طلب السعر من المستخدم عبر الجسر الآمن (Thread-Safe)
            supplier_price = self.get_supplier_price_safe(raw_title)
            
            # التحقق مما إذا كان المستخدم قد ضغط على Cancel
            if supplier_price is None:
                self.log("⏭️ تم تخطي المنتج بناءً على طلبك.")
                return False

            # 3. احتساب السعر البيعي النهائي بناءً على المدخلات
            markup_value = float(self.markup_entry.get())
            shipping_value = float(self.shipping_entry.get())
            
            calculated_price = (supplier_price * markup_value) + shipping_value
            final_store_price = round(calculated_price, 2)
            
            self.log(f"💰 التكلفة: ${supplier_price} | سعر البيع النهائي: ${final_store_price}")

            # 4. الاتصال بـ API لتوليد المحتوى التسويقي
            self.log("🧠 جاري تأليف الوصف التسويقي عبر الذكاء الاصطناعي...")
            ai_generated_data = self.fetch_ai_content(raw_title)
            
            # التحقق الصارم من صحة رد الذكاء الاصطناعي
            if ai_generated_data is None:
                self.log("❌ خطأ: فشل الذكاء الاصطناعي في الاستجابة (لا توجد بيانات).")
                return False
                
            if 'title' not in ai_generated_data:
                self.log("❌ خطأ: رد الذكاء الاصطناعي غير مكتمل (مفتاح العنوان مفقود).")
                return False

            # 5. توليد وحفظ صورة المنتج
            self.log("🎨 جاري رسم صورة المنتج وحفظها على سطح المكتب...")
            self.generate_and_save_image(ai_generated_data['title'])

            # 6. الرفع النهائي إلى متجر شوبيفاي
            self.log("📤 جاري الرفع المباشر وتصدير المنتج إلى شوبيفاي...")
            self.push_to_shopify(ai_generated_data, final_store_price)
            
            return True

        except requests.exceptions.RequestException as req_err:
            self.log(f"❌ خطأ في الاتصال بالرابط: {str(req_err)}")
            return False
        except ValueError as val_err:
            self.log(f"❌ خطأ في حسابات الأرقام (تأكد من صحة المدخلات): {str(val_err)}")
            return False
        except Exception as general_error:
            self.log(f"❌ خطأ غير متوقع أثناء معالجة المنتج: {str(general_error)}")
            return False

    def fetch_ai_content(self, input_product_name):
        """الاتصال بخوادم Groq لإنشاء وصف احترافي وعناوين للمنتج"""
        api_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        
        request_headers = {
            "Authorization": f"Bearer {GROQ_KEY}", 
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            f"قم بصياغة منتج شوبيفاي احترافي ومغري جداً باللغة العربية بناءً على هذا الاسم الخام: '{input_product_name}'. "
            "الرد يجب أن يكون بصيغة JSON فقط ويحتوي حصراً على المفاتيح التالية: "
            "'title' (عنوان قصير وجذاب), 'description' (وصف تسويقي بتنسيق HTML), 'tags' (كلمات مفتاحية)."
        )
        
        payload_data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": system_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        try:
            api_response = requests.post(api_endpoint, headers=request_headers, json=payload_data, timeout=30)
            
            if api_response.status_code == 200:
                response_json = api_response.json()
                content_string = response_json['choices'][0]['message']['content']
                parsed_content = json.loads(content_string)
                return parsed_content
            else:
                self.log(f"❌ خطأ في خادم الذكاء الاصطناعي. رمز الخطأ: {api_response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.log("❌ انتهى وقت الاتصال بالذكاء الاصطناعي (Timeout).")
            return None
        except json.JSONDecodeError:
            self.log("❌ فشل في تحليل رد الذكاء الاصطناعي (ليس بتنسيق JSON صحيح).")
            return None
        except Exception as e:
            self.log(f"❌ خطأ عام أثناء الاتصال بـ Groq: {str(e)}")
            return None

    def generate_and_save_image(self, ai_product_title):
        """إنشاء صورة للمنتج باستخدام Pollinations وحفظها في المسار المحلي"""
        try:
            # تنظيف اسم الملف ليكون آمناً لنظام التشغيل خطوة بخطوة
            safe_chars = []
            for char in ai_product_title:
                if char.isalnum() or char == ' ':
                    safe_chars.append(char)
                    
            clean_filename = "".join(safe_chars).strip()
            # تقصير الاسم لتجنب أخطاء طول مسار الملف
            clean_filename = clean_filename[:35]
            
            # ترميز نص الطلب للرابط
            image_prompt = f"Professional high-end commercial product photography of {clean_filename}, pure white studio background, studio lighting, 8k resolution"
            encoded_prompt = urllib.parse.quote(image_prompt)
            
            # بناء الرابط النهائي
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
            
            # تحميل الصورة من الخادم
            image_response = requests.get(pollinations_url, timeout=30)
            
            if image_response.status_code == 200:
                image_binary_data = image_response.content
                
                # تحديد مسار الحفظ النهائي
                file_save_path = os.path.join(self.desktop_img_path, f"{clean_filename}.jpg")
                
                # كتابة البيانات الثنائية في الملف
                with open(file_save_path, 'wb') as file:
                    file.write(image_binary_data)
                    
                self.log(f"💾 تم حفظ الصورة بنجاح باسم: {clean_filename}.jpg")
            else:
                self.log(f"⚠️ فشل تحميل الصورة من الخادم. الرمز: {image_response.status_code}")
                
        except Exception as e:
            self.log(f"⚠️ خطأ أثناء محاولة توليد أو حفظ الصورة: {str(e)}")

    def push_to_shopify(self, product_data, final_sale_price):
        """إرسال بيانات المنتج وصياغته النهائية إلى متجر شوبيفاي مع الأتمتة الذكية"""
        clean_shop_domain = SHOP_URL.replace("https://", "").replace("http://", "").rstrip('/')
        shopify_api_url = f"https://{clean_shop_domain}/admin/api/{SHOPIFY_API_VERSION}/products.json"
        request_headers = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
        
        # --- تحديث الأتمتة: دمج تاغ الذكاء الاصطناعي مع تاغ المجموعة الآلية ---
        ai_tags = product_data.get('tags', '')
        if isinstance(ai_tags, list):
            ai_tags = ", ".join(ai_tags)
        
        # إضافة التاغ السري الذي سيجعل المنتج يطير مباشرة لمجموعة Best Sellers
        final_automated_tags = f"{ai_tags}, StoreBrain_Auto" if ai_tags else "StoreBrain_Auto"
        shopify_payload = {
            "product": {
                "title": product_data.get('title'),
                "body_html": product_data.get('description'),
                "tags": final_automated_tags,  # <--- السر هنا
                "status": "active",
                "variants": [{"price": str(final_sale_price), "inventory_management": "shopify"}]
            }
        }
        
        try:
            shopify_response = requests.post(shopify_api_url, headers=request_headers, json=shopify_payload, timeout=40)
            if shopify_response.status_code == 201:
                new_product_id = shopify_response.json()['product']['id']
                self.log(f"✅ مبروك! المنتج متوفر وتم إضافته للقسم الآلي بنجاح.")
                self.log(f"🔗 رابط إدارة المنتج: https://{clean_shop_domain}/admin/products/{new_product_id}")
            else:
                self.log(f"❌ فشل الرفع لشوبيفاي. الرمز: {shopify_response.status_code}")
                self.log(f"تفاصيل الخطأ: {shopify_response.text}")
                
        except requests.exceptions.Timeout:
            self.log("❌ فشل الرفع: انتهى وقت الاتصال بخادم شوبيفاي.")
        except Exception as error:
            self.log(f"❌ خطأ غير متوقع أثناء الاتصال بشوبيفاي: {str(error)}")

# ==========================================================
# 6. نقطة انطلاق تشغيل البرنامج
# ==========================================================
if __name__ == "__main__":
    try:
        # إنشاء النافذة الرئيسية لتطبيق الواجهة الرسومية
        app_main_window = tk.Tk()
        
        # تهيئة فئة الإمبراطورية وتشغيل الواجهة
        storebrain_application = StoreBrainEmpire(app_main_window)
        app_main_window.mainloop()
        
    except Exception as fatal_exception:
        # التقاط الأخطاء القاتلة على مستوى التطبيق وطباعتها في سطر الأوامر (إن وجد)
        print(f"حدث خطأ قاتل أدى إلى منع تشغيل التطبيق بالكامل: {str(fatal_exception)}")
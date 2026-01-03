import google.generativeai as genai
from django.conf import settings

# Konfigurasi API
genai.configure(api_key=settings.GEMINI_API_KEY)

# SYSTEM PROMPT → AI akan selalu bertindak sebagai guru privat
TEACHER_INSTRUCTION = """
Anda adalah "Guruku AI", asisten guru privat cerdas yang didedikasikan KHUSUS untuk siswa SMP dan SMA di Indonesia.

**Identitas & Batasan Mutlak:**
- **Identitas:** Guru privat profesional, sabar, dan fokus pada akademik sekolah.
- **Fokus Utama:** Pelajaran sekolah (Matematika, Fisika, Kimia, Biologi, Bahasa Indonesia, Bahasa Inggris, Geografi, Sejarah, Ekonomi, Sosiologi, TIK, Seni Budaya, PJOK).
- **NON-TOLERANSI UTAMA:** Anda DILARANG KERAS menjawab pertanyaan tentang:
    1. **Hiburan/Pop Culture:** Gosip artis, YouTuber (Kai Cenat, IShowSpeed, dll), selebgram, film, musik pop non-edukatif.
    2. **Keuangan Pribadi/Skema Cepat Kaya:** "Cara menjadi kaya", "Investasi saham untuk pemula" (kecuali dalam konteks teori ekonomi makro/mikro di sekolah atau pelajaran Ekonomi), perjudian, slot.
    3. **Percintaan/Hubungan:** Tips pacaran, galau, zodiak.
    4. **Gaming:** Berita game, cheat, e-sport (kecuali jika siswa bertanya tentang pengembangan game/coding dalam konteks TIK).
    5. **Topik Sensitif:** Politik praktis, SARA, konten dewasa.

**Protokol Respon (Refusal & Redirection):**
Jika pengguna bertanya hal di luar konteks pelajaran sekolah:
1. **LANGSUNG MENOLAK** dengan sopan, singkat, dan tegas.
2. **JANGAN MEMBERIKAN PENJELASAN** tentang topik tersebut (jangan menjelaskan siapa itu figur publik yg ditanya, jangan memberi tips investasi).
3. **ALIHKAN KEMBALI** ke topik belajar.

*Contoh Respons Penolakan:*
- *"Maaf, Guruku AI hanya fokus menjawab pertanyaan pelajaran sekolah seperti Matematika atau Fisika. Yuk, kita bahas PR kamu saja!"*
- *"Wah, itu di luar keahlian saya sebagai guru sekolah. Saya lebih jago jelaskan Hukum Newton atau Tata Bahasa Indonesia. Ada yang mau ditanyakan soal itu?"*
- *"Saya tidak bisa menjawab pertanyaan tentang hiburan atau personal. Mari kembali fokus ke materi SMP/SMA."*

**Gaya Pengajaran (Socratic & Scaffolding):**
1. **Jangan Langsung Jawab:** Untuk soal latihan/hitungan, berikan langkah-langkah atau petunjuk (clue) terlebih dahulu. Biarkan siswa berpikir.
2. **Jelaskan Konsep:** Jika siswa bingung, jelaskan konsep dasarnya dengan bahasa sederhana dan analogi sehari-hari.
3. **Format Matematika (WAJIB LaTeX):**
   - Gunakan `$$ rumus $$` untuk rumus block (tampilan besar di tengah).
   - Gunakan `$ rumus $` untuk rumus inline (di dalam teks).
   - Contoh: "Rumus pythagoras adalah $$ a^2 + b^2 = c^2 $$".

**Tujuan Akhir:** Membantu siswa mengerti materi sekolah dan sukses ujian, bukan menjadi teman ngobrol santai tentang hal duniawi.
"""

# Inisialisasi model dengan instruction tetap
# Konfigurasi Safety Settings yang ketat
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    }
]

# Konfigurasi Generation Config
generation_config = genai.types.GenerationConfig(
    temperature=0.3, # Rendah agar lebih patuh pada instruksi, mengurangi halusinasi
    candidate_count=1,
    max_output_tokens=2048,
)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    system_instruction=TEACHER_INSTRUCTION,
    safety_settings=safety_settings,
    generation_config=generation_config
)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def generate_material_content(file_path, mime_type):
    """Generates educational content from a file using Gemini."""
    try:
        # Upload file
        uploaded_file = upload_to_gemini(file_path, mime_type=mime_type)
        
        # Create prompt
        prompt = """
        Analyze this educational document.
        Create a comprehensive lesson module in Markdown format based strictly on the content of this file.
        
        Requirements:
        1. **Summary**: Brief summary of the topic.
        2. **Key Concepts**: Explain main concepts clearly.
        3. **Equations**: If there are mathematical formulas, convert them to LaTeX format enclosed in $$ (block) or $ (inline).
        4. **Examples**: Provide examples if available in the text.
        5. **Quiz/Practice**: Create 3 simple practice questions based on the content.
        
        Format the output as clean Markdown.
        """
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": [uploaded_file, prompt]}
        ])
        
        response = chat.send_message("Generate the content now.")
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def ask_gemini(prompt: str, history: list = None) -> str:
    try:
        chat = model.start_chat(history=history or [])
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

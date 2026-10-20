#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مشروع جلب القرآن الكريم كاملاً وتوليد ملفات Markdown مفهرسة لكل سورة
Quran Markdown Exporter & Indexer
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
import urllib.request
import urllib.error

# ضمان عمل التيرمينال بترميز UTF-8 في بيئة ويندوز دون أخطاء
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# الأسماء الرسمية المعيارية للسور الـ 114
SURAH_CANONICAL_NAMES = {
    1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
    6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
    11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
    16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
    21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
    26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
    31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
    36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
    41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
    46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
    51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
    56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
    61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
    66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
    71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
    76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
    81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
    86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
    91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
    96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
    101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
    106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
    111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
}

# ترتيب النزول المعتمد (وفق مصحف المدينة المنورة وروايات أهل العلم)
REVELATION_ORDER = {
    1: 5, 2: 87, 3: 89, 4: 92, 5: 112, 6: 55, 7: 39, 8: 88, 9: 113, 10: 51,
    11: 52, 12: 53, 13: 96, 14: 72, 15: 54, 16: 70, 17: 50, 18: 69, 19: 44, 20: 45,
    21: 73, 22: 103, 23: 74, 24: 102, 25: 42, 26: 47, 27: 48, 28: 49, 29: 85, 30: 84,
    31: 57, 32: 75, 33: 90, 34: 58, 35: 43, 36: 41, 37: 56, 38: 38, 39: 59, 40: 60,
    41: 61, 42: 62, 43: 63, 44: 64, 45: 65, 46: 66, 47: 95, 48: 111, 49: 106, 50: 34,
    51: 67, 52: 76, 53: 23, 54: 37, 55: 97, 56: 46, 57: 94, 58: 105, 59: 101, 60: 91,
    61: 109, 62: 110, 63: 104, 64: 108, 65: 99, 66: 107, 67: 77, 68: 2, 69: 78, 70: 79,
    71: 71, 72: 40, 73: 3, 74: 4, 75: 31, 76: 98, 77: 33, 78: 80, 79: 81, 80: 24,
    81: 7, 82: 82, 83: 86, 84: 83, 85: 27, 86: 36, 87: 8, 88: 68, 89: 10, 90: 35,
    91: 26, 92: 9, 93: 11, 94: 12, 95: 28, 96: 1, 97: 25, 98: 100, 99: 93, 100: 14,
    101: 30, 102: 16, 103: 13, 104: 32, 105: 19, 106: 29, 107: 17, 108: 15, 109: 18, 110: 114,
    111: 6, 112: 22, 113: 20, 114: 21
}

# نمط التعرف على البسملة المسبوقة في أول آية من سور القرآن (ما عدا الفاتحة والتوبة)
BISMILLAH_PATTERN = re.compile(r'^\ufeff?بّ?ِسْمِ\s+ٱللَّهِ\s+ٱلرَّحْمَٰنِ\s+ٱلرَّحِيمِ\s*')
BISMILLAH_TEXT = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"

def to_arabic_number(n: int) -> str:
    """تحويل الأرقام الإنجليزية إلى أرقام عربية مشرقية داخل أقواس الترقيم المصحفي"""
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    return "".join(arabic_digits[int(d)] for d in str(n))

def get_surah_filename(surah_num: int) -> str:
    """توليد اسم الملف بصيغة ثلاثية الخانات لضمان الترتيب الأبجدي والرقمي السليم"""
    canonical_name = SURAH_CANONICAL_NAMES.get(surah_num, f"سورة_{surah_num}")
    safe_name = canonical_name.replace(" ", "_")
    return f"{surah_num:03d}_سورة_{safe_name}.md"

def fetch_quran_data(edition: str = "quran-uthmani", cache_file: str = None, force: bool = False):
    """جلب بيانات القرآن الكريم من واجهة برمجة التطبيقات أو من الكاش في حال تحديده"""
    if cache_file:
        cache_path = Path(cache_file)
        if not force and cache_path.exists():
            print(f"[+] تحميل بيانات القرآن من الذاكرة المحلية: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

    url = f"https://api.alquran.cloud/v1/quran/{edition}"
    print(f"[...] جلب القرآن الكريم كاملاً من الخادم ({edition}): {url}")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "QuranMarkdownProject/1.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            content = response.read().decode("utf-8")
            data = json.loads(content)
            
            if data.get("code") == 200 and "data" in data:
                if cache_file:
                    cache_path = Path(cache_file)
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[✓] تم حفظ البيانات محلياً في: {cache_path}")
                print("[✓] تم استلام البيانات بنجاح.")
                return data
            else:
                raise ValueError(f"استجابة غير صالحة من المصدر: {data.get('status')}")
    except Exception as e:
        print(f"[!] خطأ أثناء الاتصال بالخادم: {e}")
        if cache_file and Path(cache_file).exists():
            print("[!] استخدام النسخة المخزنة مسبقاً بدلاً من ذلك...")
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        raise

def format_surah_markdown(surah: dict, total_surahs: int = 114) -> str:
    """تنسيق سورة واحدة بصيغة Markdown فائقة الجودة والدقة"""
    num = surah["number"]
    full_name = surah["name"]
    canonical_name = SURAH_CANONICAL_NAMES.get(num, surah.get("englishName", ""))
    english_name = surah["englishName"]
    english_trans = surah.get("englishNameTranslation", "")
    rev_type_en = surah["revelationType"]
    rev_type_ar = "مكية" if rev_type_en.lower() == "meccan" else "مدنية"
    ayahs = surah["ayahs"]
    ayah_count = surah.get("numberOfAyahs", len(ayahs))
    rev_order = REVELATION_ORDER.get(num, "-")
    juz_set = sorted(list(set(a["juz"] for a in ayahs)))
    juz_display = f"الجزء {juz_set[0]}" if len(juz_set) == 1 else f"الأجزاء {juz_set[0]} إلى {juz_set[-1]}"
    
    pages = sorted(list(set(a["page"] for a in ayahs)))
    page_display = f"{pages[0]}" if pages[0] == pages[-1] else f"{pages[0]} - {pages[-1]}"

    # تجهيز روابط التنقل
    prev_link = ""
    next_link = ""
    if num > 1:
        prev_num = num - 1
        prev_name = SURAH_CANONICAL_NAMES.get(prev_num, "")
        prev_file = get_surah_filename(prev_num)
        prev_link = f"[➡️ سورة {prev_name}]({prev_file})"
    else:
        prev_link = "بداية المصحف الشريف"

    if num < total_surahs:
        next_num = num + 1
        next_name = SURAH_CANONICAL_NAMES.get(next_num, "")
        next_file = get_surah_filename(next_num)
        next_link = f"[سورة {next_name} ⬅️]({next_file})"
    else:
        next_link = "ختام المصحف الشريف"

    index_link = "[📑 الفهرس الرئيسي](000_الفهرس.md)"

    # بناء رأس الملف بصيغة YAML Frontmatter
    md = [
        "---",
        f"number: {num}",
        f'name: "{canonical_name}"',
        f'name_full: "{full_name}"',
        f'name_en: "{english_name}"',
        f'name_translation: "{english_trans}"',
        f'revelation_type: "{rev_type_ar}"',
        f"revelation_order: {rev_order}",
        f"number_of_ayahs: {ayah_count}",
        f"juz: {juz_set}",
        f"pages: [{page_display}]",
        "---",
        "",
        f"# 📖 سورة {canonical_name}",
        "",
        '<div align="center">',
        "",
        "| رقم السورة | مكان النزول | ترتيب النزول | عدد الآيات | أجزاء السورة | أرقام الصفحات |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |",
        f"| {num} | {rev_type_ar} | {rev_order} | {ayah_count} | {juz_display} | {page_display} |",
        "",
        "</div>",
        "",
        "---",
        ""
    ]

    # إضافة البسملة إذا كانت السورة تتطلب ذلك (جميع السور عدا الفاتحة لأنها آيتها الأولى، وعدا التوبة)
    if num not in (1, 9):
        md.extend([
            '<div align="center">',
            "",
            f"### {BISMILLAH_TEXT}",
            "",
            "</div>",
            "",
            "---",
            ""
        ])

    # تجهيز نصوص الآيات بدقة مع إزالة البسملة من أول آية إن وجدت
    processed_ayahs = []
    for a in ayahs:
        ayah_num = a["numberInSurah"]
        raw_text = a["text"].replace("\ufeff", "").strip()
        
        if num == 1:
            clean_text = raw_text
        elif num == 9:
            clean_text = raw_text
        else:
            if ayah_num == 1:
                clean_text = BISMILLAH_PATTERN.sub("", raw_text).strip()
            else:
                clean_text = raw_text
                
        is_sajda = bool(a.get("sajda"))
        processed_ayahs.append({
            "num": ayah_num,
            "text": clean_text,
            "juz": a.get("juz"),
            "page": a.get("page"),
            "hizb": a.get("hizbQuarter"),
            "sajda": is_sajda
        })

    # 1. نص السورة المتواصل (قراءة المصحف)
    md.extend([
        "## 📜 نص السورة (قراءة متواصلة)",
        ""
    ])

    continuous_parts = []
    for pa in processed_ayahs:
        sajda_mark = " ۩" if pa["sajda"] else ""
        ayah_bracket = f" ﴿{to_arabic_number(pa['num'])}{sajda_mark}﴾ "
        continuous_parts.append(f"{pa['text']}{ayah_bracket}")

    md.append("".join(continuous_parts).strip())
    md.extend([
        "",
        "---",
        "",
        "## 📑 آيات السورة بالتفصيل",
        ""
    ])

    # 2. الآيات بالتفصيل (مرقمة وواضحة للتدبر والمطالعة)
    for pa in processed_ayahs:
        sajda_badge = " *(۩ سجدة تلاوة)*" if pa["sajda"] else ""
        meta_info = f"*(الجزء: {pa['juz']} | الصفحة: {pa['page']}){sajda_badge}*"
        md.append(f"{pa['num']}. **{pa['text']}** {meta_info}")

    # تذييل التنقل
    md.extend([
        "",
        "---",
        "",
        '<div align="center">',
        "",
        f"| {prev_link} | {index_link} | {next_link} |",
        "| :---: | :---: | :---: |",
        "",
        "</div>",
        ""
    ])

    return "\n".join(md)

def generate_index_markdown(surahs: list) -> str:
    """توليد الفهرس الشامل للقرآن الكريم مع إحصائيات وروابط مباشرة وجدول الأجزاء"""
    total_ayahs = sum(s.get("numberOfAyahs", len(s["ayahs"])) for s in surahs)
    meccan_count = sum(1 for s in surahs if s["revelationType"].lower() == "meccan")
    medinan_count = len(surahs) - meccan_count
    
    lines = [
        "# 📖 فهرس القرآن الكريم الشامل",
        "",
        "الحمد لله رب العالمين، والصلاة والسلام على خاتم الأنبياء والمرسلين نبينا محمد وعلى آله وصحبه أجمعين.",
        "",
        "> هذا المشروع يضم النص الكامل للقرآن الكريم مكتوباً بالرسم العثماني المعتمد، مقسماً ومفهرساً في 114 ملف Markdown لكل سورة على حدة مع بياناتها وأرقام أجزائها وصفحاتها وروابط تنقل سهلة وسريعة.",
        "",
        "### 📊 إحصائيات عامة للمصحف الشريف",
        "",
        '<div align="center">',
        "",
        "| الإحصائية | القيمة |",
        "| :--- | :---: |",
        f"| **إجمالي عدد السور** | 114 سورة |",
        f"| **إجمالي عدد الآيات** | {total_ayahs:,} آية |",
        f"| **السور المكية** | {meccan_count} سورة |",
        f"| **السور المدنية** | {medinan_count} سورة |",
        "| **عدد الأجزاء** | 30 جزءاً |",
        "| **عدد الأحزاب** | 60 حزباً |",
        "| **سجدات التلاوة** | 15 سجدة |",
        "",
        "</div>",
        "",
        "---",
        "",
        "## 📑 الفهرس المرتب حسب المصحف الشريف",
        "",
        "| # | اسم السورة | الاسم بالإنجليزية | مكان النزول | ترتيب النزول | عدد الآيات | الأجزاء | الصفحات | سجدة |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    # فهرس الأجزاء لتسهيل التصفح عبر الأجزاء الـ 30
    juz_map = {i: [] for i in range(1, 31)}

    for s in surahs:
        num = s["number"]
        canonical_name = SURAH_CANONICAL_NAMES.get(num, s.get("name", ""))
        english_name = s["englishName"]
        rev_ar = "مكية" if s["revelationType"].lower() == "meccan" else "مدنية"
        rev_order = REVELATION_ORDER.get(num, "-")
        ayah_count = s.get("numberOfAyahs", len(s["ayahs"]))
        
        juz_list = sorted(list(set(a["juz"] for a in s["ayahs"])))
        juz_str = f"{juz_list[0]}" if len(juz_list) == 1 else f"{juz_list[0]}-{juz_list[-1]}"
        for j in juz_list:
            juz_map[j].append((num, canonical_name))
            
        pages = sorted(list(set(a["page"] for a in s["ayahs"])))
        page_str = f"{pages[0]}" if pages[0] == pages[-1] else f"{pages[0]}-{pages[-1]}"
        
        has_sajda = any(bool(a.get("sajda")) for a in s["ayahs"])
        sajda_str = "۩" if has_sajda else "-"
        
        filename = get_surah_filename(num)
        surah_link = f"[سورة {canonical_name}]({filename})"
        
        lines.append(
            f"| {num:03d} | {surah_link} | {english_name} | {rev_ar} | {rev_order} | {ayah_count} | {juz_str} | {page_str} | {sajda_str} |"
        )

    # إضافة فهرس الأجزاء
    lines.extend([
        "",
        "---",
        "",
        "## 📚 فهرس أجزاء القرآن الكريم (30 جزءاً)",
        "",
        "| الجزء | السور المتضمنة |",
        "| :---: | :--- |"
    ])

    for juz_num in range(1, 31):
        surah_items = juz_map[juz_num]
        seen_nums = set()
        unique_surahs = []
        for n, cname in surah_items:
            if n not in seen_nums:
                seen_nums.add(n)
                unique_surahs.append(f"[{cname}]({get_surah_filename(n)})")
        lines.append(f"| **الجزء {juz_num}** | {', '.join(unique_surahs)} |")

    lines.extend([
        "",
        "---",
        "",
        "**تم توليد هذا الفهرس آلياً بدقة متناهية بالرسم العثماني المعتمد.**"
    ])

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="مشروع جلب وتصدير القرآن الكريم إلى ملفات Markdown مفهرسة")
    parser.add_argument("--output-dir", default="القران", help="المجلد المستهدف لتوليد ملفات السور والفهرس (الافتراضي: القران)")
    parser.add_argument("--cache-file", default=None, help="مسار ملف التخزين المؤقت المحلي للبيانات (اختياري)")
    parser.add_argument("--force-download", action="store_true", help="إعادة تحميل البيانات من الخادم وتجاوز الملف المخزن محلياً")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("      مشروع تصدير القرآن الكريم كاملاً إلى ملفات Markdown      ")
    print("=" * 60)
    print(f"[*] مجلد الإخراج: {output_dir.resolve()}")
    if args.cache_file:
        print(f"[*] ملف التخزين المؤقت: {Path(args.cache_file).resolve()}")
    
    # 1. جلب البيانات
    quran_json = fetch_quran_data(cache_file=args.cache_file, force=args.force_download)
    surahs = quran_json["data"]["surahs"]
    print(f"[+] تم استلام {len(surahs)} سورة بنجاح. جاري إنشاء ملفات Markdown...")

    # 2. إنشاء ملف Markdown لكل سورة
    for s in surahs:
        num = s["number"]
        canonical_name = SURAH_CANONICAL_NAMES.get(num, s.get("name", ""))
        filename = get_surah_filename(num)
        filepath = output_dir / filename
        
        surah_md = format_surah_markdown(s, total_surahs=len(surahs))
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(surah_md)
        
        print(f"  [✓] ({num:03d}/114) سورة {canonical_name} -> {filename}")

    # 3. إنشاء الفهرس الرئيسي (000_الفهرس.md)
    print("[*] جاري توليد الفهرس العام الشامل...")
    index_md = generate_index_markdown(surahs)
    
    index_path = output_dir / "000_الفهرس.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_md)
    print(f"[✓] تم إنشاء الفهرس الشامل: {index_path.name}")

    print("\n" + "=" * 60)
    print("✨ تم اكتمال المشروع بنجاح!")
    print(f"📁 تم حفظ جميع السور (114 سورة) مع الفهرس في المجلد: {output_dir.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    main()

# speclite

> A condensed, 5-phase spec-driven development workflow adapted from [GitHub Spec Kit](https://github.com/github/spec-kit) - with a built-in manager, per-feature reference folders, and phase-by-phase check logs.

**[العربية](#العربية) | [English](#english)**

---

## العربية

### ما هي هذه المهارة؟

**speclite** أداة عمل مبنية على فلسفة [GitHub Spec Kit](https://github.com/github/spec-kit) للتطوير المبني على المواصفات (Spec-Driven Development)، لكنها مختصرة إلى **5 مراحل** بدل 10 أوامر منفصلة، مع الحفاظ على جودة وآليات Spec Kit الأصلية (تصنيف أسئلة التوضيح، فلسفة "اختبارات الوحدة للمتطلبات"، فحوصات الاتساق).

المراحل الخمس:

| # | المرحلة | تشمل |
|---|---|---|
| 1 | **Constitution** | ملف واحد فقط **لكل المشروع** (وليس لكل ميزة) يحتوي مبادئ غير قابلة للتفاوض - تمامًا كآلية Spec Kit الأصلية. أي تعارض لاحق مع مبدأ "MUST" في أي مرحلة يوقف العمل فورًا ويطلب من المستخدم تعديل المبدأ صراحةً عبر هذه المرحلة، بدل الالتفاف عليه بصمت في خطة أو مهمة |
| 2 | **Specify** | كتابة المواصفة (spec) + طرح أسئلة التوضيح اللازمة |
| 3 | **Plan** | كتابة خطة التنفيذ + قائمة تحقق لجودة المتطلبات |
| 4 | **Tasks** | تفكيك الخطة إلى مهام + فحص اتساق شامل قبل البدء بالتنفيذ |
| 5 | **Implement** | تنفيذ المهام + فحص نهائي للتأكد من عدم وجود أي نقص |

بالإضافة إلى ذلك:

- **مدير تلقائي** (`status`) يكتشف بنفسه في أي مرحلة أنت الآن، فلا تحتاج لتتذكر الترتيب أو أين توقفت - حتى لو رجعت بعد أسابيع.
- **مجلد `references/`** لكل ميزة، بداخله `PRD/ images/ fonts/ sounds/ videos/ data/ docs/` لوضع أي مستندات أو صور أو ملفات مرجعية تخص الميزة.
- **مجلد `logs/`** لكل ميزة، بمجلد فرعي لكل مرحلة، يحوي سجل فحوصات تلقائي بالإضافة لأي توثيق إضافي (نتائج اختبارات، لقطات شاشة، ملاحظات) ينظّمه الوكيل حسب النوع.
- سكربتات **Python** و **PowerShell** متطابقة تمامًا، تعمل على أي نظام تشغيل.

### التثبيت

1. حمّل هذا المستودع أو استنسخه (`git clone`).
2. انسخ مجلد `speclite/` بالكامل إلى داخل جذر مشروعك (بجانب باقي ملفات المشروع).
3. من داخل جذر المشروع، شغّل سكربت التثبيت المناسب:

   ```bash
   # Linux / macOS
   python speclite/install.py
   ```

   ```powershell
   # Windows
   pwsh speclite/Install.ps1
   ```

سكربت التثبيت **لا يكتب إلا داخل مجلد `.speclite/`** الجديد، ولا يمس أي ملف آخر في مشروعك، ولا يستبدل أي ملف موجود مسبقًا - إذا وُجد تعارض يتجاوزه ويخبرك في النهاية بما تم تخطيه، حتى تستطيع مراجعته يدويًا. آمن لإعادة التشغيل في أي وقت (مثلًا بعد تحديث النسخة).

### الاستخدام

بعد التثبيت، ابدأ بتشغيل فاحص الحالة (أو دع وكيل الذكاء الاصطناعي الذي تستخدمه يفعل ذلك تلقائيًا إذا فعّلت المهارة عبر `SKILL.md`):

```bash
python .speclite/scripts/python/status.py --json
```

النتيجة تخبرك مباشرة بالمرحلة التالية (`NEXT_PHASE`) وسببها. تابع القراءة والتنفيذ من ملف الأمر المطابق داخل `.speclite/commands/`، ثم أعد تشغيل `status` بعد كل مرحلة للانتقال تلقائيًا للتالية:

```
constitution → specify → plan → tasks → implement
```

للاستخدام كـ **Claude Skill**: ضع مجلد `speclite/` داخل مجلد المهارات، وسيقرأ Claude ملف `SKILL.md` ويتولى تشغيل المراحل تلقائيًا بالاعتماد على `status`.

راجع `speclite/README.md` داخل الحزمة لتفاصيل بنية المجلدات الكاملة وجدول مقارنة كل مرحلة بأوامر Spec Kit الأصلية.

---

## English

### What is this?

**speclite** is a workflow tool built on the philosophy of [GitHub Spec Kit](https://github.com/github/spec-kit)'s spec-driven development, condensed into **5 phases** instead of 10 separate commands, while preserving Spec Kit's original rigor (clarification question taxonomy, "unit tests for requirements" checklist philosophy, cross-artifact consistency checks).

The 5 phases:

| # | Phase | Covers |
|---|---|---|
| 1 | **Constitution** | ONE file for the **entire project** (never per-feature) holding non-negotiable principles - exactly Spec Kit's own model. If any later phase finds a conflict with a "MUST" rule, it stops immediately and requires the user to explicitly amend the rule through this phase, instead of silently working around it in a plan or task |
| 2 | **Specify** | Draft the spec + ask the clarifying questions it needs |
| 3 | **Plan** | Write the implementation plan + a requirements-quality checklist |
| 4 | **Tasks** | Break the plan into tasks + a full consistency pass before implementation starts |
| 5 | **Implement** | Execute the tasks + a final gap-check to confirm nothing was missed |

Also included:

- A **built-in manager** (`status`) that auto-detects which phase to run next, so you never have to track the order or remember where you left off - even after weeks away.
- A **`references/` folder** per feature, with `PRD/ images/ fonts/ sounds/ videos/ data/ docs/` subfolders for any source material relevant to that feature.
- A **`logs/` folder** per feature, with one subfolder per phase holding an automatic check log plus any extra documentation (test results, screenshots, notes) the agent organizes by type.
- **Python** and **PowerShell** scripts, fully mirrored, so it works the same way on any OS.

### Installation

1. Download or clone this repository.
2. Copy the whole `speclite/` folder into your project's root, next to your other project files.
3. From the project root, run the installer for your platform:

   ```bash
   # Linux / macOS
   python speclite/install.py
   ```

   ```powershell
   # Windows
   pwsh speclite/Install.ps1
   ```

The installer **only ever writes inside the new `.speclite/` folder** - it never touches anything else in your project, and it never overwrites a file that already exists. If it finds a conflict, it skips that file and reports it at the end so you can review it manually. Safe to re-run any time (e.g. after updating to a newer version).

### Usage

After installing, run the status checker (or let your AI agent do this automatically if you've enabled the skill via `SKILL.md`):

```bash
python .speclite/scripts/python/status.py --json
```

The output tells you exactly what to do next (`NEXT_PHASE`) and why. Follow the matching command file under `.speclite/commands/`, then re-run `status` after each phase to automatically move to the next one:

```
constitution → specify → plan → tasks → implement
```

**To use as a Claude Skill**: place the `speclite/` folder in your skills directory - Claude will read `SKILL.md` and drive the phases automatically using `status`.

See `speclite/README.md` inside the package for the full directory layout and a phase-by-phase comparison against the original Spec Kit commands.

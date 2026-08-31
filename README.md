# speclite

> A condensed, 5-phase spec-driven development workflow adapted from [GitHub Spec Kit](https://github.com/github/spec-kit) - with a built-in manager, per-feature reference and evidence folders, artifact-based phase tracking (no separate check-log ledger), and installable commands + skills matching Spec Kit's own distribution.

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
- **مجلد `logs/` واحد مسطّح** لكل ميزة (وليس مقسّمًا حسب المرحلة) - مساحة حرة لأدلة داعمة ينظّمها الوكيل بنفسه (نتائج اختبارات، صور شاشة حتى ما شاركه المستخدم سابقًا في المحادثة، ملاحظات جلسة). لا يُستخدم أبدًا لتحديد اكتمال أي مرحلة - ذلك يُقرأ مباشرة من المستندات نفسها (checkbox في spec.md/plan.md/tasks.md)، بنفس أسلوب Spec Kit تمامًا.
- **خريطة مشروع اختيارية** (`specs/PROJECT_MAP.md` وملفاتها المرافقة) تنمو مع المشروع وتربط كل متطلب بالكود الفعلي الذي ينفّذه - تُحدَّث بتكلفة منخفضة (فحص التغييرات فقط منذ آخر مزامنة عبر git)، وتُقترح فقط في اللحظات المناسبة (بعد `constitution` لمشروع قائم، أو بعد `implement`) ولا تُفرض أبدًا.
- سكربتات **Python** و **PowerShell** متطابقة تمامًا، تعمل على أي نظام تشغيل.
- تُثبَّت كملفات أوامر مسطّحة `.agents/commands/*.md` **وأيضًا** كمجلدات `skills/<name>/SKILL.md` مستقلة بذاتها — نفس أسلوب التوزيع المزدوج الذي يستخدمه Spec Kit نفسه.

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

سكربت التثبيت يوزّع الملفات في **3 مواقع فقط ولا يكتب في غيرها إطلاقًا**:

- `.speclite/` — الآلية الداخلية: السكربتات، القوالب، وحالة المشروع.
- `.agents/commands/` — ملفات الأوامر الخمسة + أمر خريطة المشروع، بشكل مسطّح، لأي وكيل يقرأ أوامر مخصّصة من مجلد `.agents/` على مستوى المشروع.
- `skills/` — نفس الـ6 ملفات + المدير، كل واحدة كمجلد `skills/<name>/SKILL.md` مستقل بذاته — بنفس طريقة Spec Kit تمامًا في توزيع `skills/speckit-<name>/SKILL.md`.

لا يستبدل أي ملف موجود مسبقًا في أي من هذه المواقع الثلاثة — إذا وُجد تعارض يتجاوزه ويخبرك في النهاية بما تم تخطيه، حتى تستطيع مراجعته يدويًا. آمن لإعادة التشغيل في أي وقت (مثلًا بعد تحديث النسخة).

### الاستخدام

بعد التثبيت، ابدأ بتشغيل فاحص الحالة (أو دع وكيل الذكاء الاصطناعي الذي تستخدمه يفعل ذلك تلقائيًا إذا فعّلت المهارة عبر `SKILL.md`):

```bash
python .speclite/scripts/python/status.py --json
```

النتيجة تخبرك مباشرة بالمرحلة التالية (`NEXT_PHASE`) وسببها. تابع القراءة والتنفيذ من ملف الأمر المطابق داخل `.agents/commands/` (أو المهارة المطابقة داخل `skills/`)، ثم أعد تشغيل `status` بعد كل مرحلة للانتقال تلقائيًا للتالية:

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
- A **single flat `logs/` folder** per feature (not split by phase) - free-form space for supporting evidence the agent organizes itself (test results, screenshots including anything the user already shared in chat, session notes). Never used to decide whether a phase is done - that's read directly from the artifacts themselves (a checkbox in spec.md/plan.md/tasks.md), Spec Kit's own style.
- An **optional Project Map** (`specs/PROJECT_MAP.md` and its siblings) that grows with the project and traces every requirement to the code that implements it - updated cheaply (only what changed since the last sync, via git) and only ever suggested at the right moments (after `constitution` for an existing project, or after `implement`), never forced.
- **Python** and **PowerShell** scripts, fully mirrored, so it works the same way on any OS.
- Installs as both flat `.agents/commands/*.md` files and self-contained `skills/<name>/SKILL.md`
  folders - the same dual distribution Spec Kit itself uses.

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

The installer deploys to **three locations only, and never writes anywhere else**:

- `.speclite/` - internal machinery: scripts, templates, and project state.
- `.agents/commands/` - the 5 phase command files plus the Project Map command, flat, for
  any agent that reads project-level custom slash-commands from an `.agents/` directory.
- `skills/` - the same 6 command files plus the manager, each as a self-contained
  `skills/<name>/SKILL.md` folder - matching Spec Kit's own `skills/speckit-<name>/SKILL.md`
  distribution exactly.

It never overwrites a file that already exists at any of these three destinations. If it finds
a conflict, it skips that file and reports it at the end so you can review it manually. Safe to
re-run any time (e.g. after updating to a newer version).

### Usage

After installing, run the status checker (or let your AI agent do this automatically if you've enabled the skill via `SKILL.md`):

```bash
python .speclite/scripts/python/status.py --json
```

The output tells you exactly what to do next (`NEXT_PHASE`) and why. Follow the matching command file under `.agents/commands/` (or the matching skill under `skills/`), then re-run `status` after each phase to automatically move to the next one:

```
constitution → specify → plan → tasks → implement
```

**To use as a Claude Skill**: place the `speclite/` folder in your skills directory - Claude will read `SKILL.md` and drive the phases automatically using `status`.

See `speclite/README.md` inside the package for the full directory layout and a phase-by-phase comparison against the original Spec Kit commands.

# speclite

**[العربية](#العربية) | [English](#english)**

---

## العربية

نسخة مختصرة من 5 مراحل مقتبسة من [GitHub Spec Kit](https://github.com/github/spec-kit) لمنهجية
التطوير المبني على المواصفات، مع مدير مدمج يكتشف تلقائيًا المرحلة التالية الواجب تنفيذها، مجلد
`references/` لكل ميزة لوضع المواد المرجعية التي يقدّمها المستخدم، مجلد `logs/` واحد مسطّح لكل
ميزة لتوثيق أدلة حرة الشكل (نتائج اختبارات، صور شاشة، ملاحظات جلسة) ينظّمها الوكيل حسب النوع،
وخريطة مشروع اختيارية غير مُلزِمة تنمو مع المشروع عبر تحديثات تراكمية منخفضة التكلفة. تُثبَّت
الحزمة كملفات أوامر مسطّحة `.agents/commands/*.md` **وأيضًا** كمجلدات `skills/<name>/SKILL.md`
مستقلة بذاتها - نفس أسلوب التوزيع المزدوج الذي يستخدمه Spec Kit نفسه.

### التثبيت

1. انسخ مجلد `speclite/` بالكامل إلى داخل جذر مشروعك، بجانب باقي ملفات المشروع.
2. شغّل سكربت التثبيت من جذر المشروع:
   - لينكس / macOS: `python speclite/install.py`
   - ويندوز: `pwsh speclite/Install.ps1`

يوزّع السكربت الملفات على 3 مواقع فقط **ولا يكتب في أي مكان آخر إطلاقًا**:

- `.speclite/` - الآلية الداخلية: السكربتات، القوالب، وحالة المشروع.
- `.agents/commands/` - ملفات الأوامر الخمسة + أمر خريطة المشروع، بشكل مسطّح، لأي وكيل يقرأ
  أوامر مخصّصة على مستوى المشروع.
- `skills/` - نفس الـ6 ملفات + المدير، كل واحدة كمجلد `skills/<name>/SKILL.md` مستقل بذاته -
  بنفس طريقة Spec Kit تمامًا في `skills/speckit-<name>/SKILL.md`.

لا يستبدل أي ملف موجود مسبقًا في أي من هذه المواقع - إذا وُجد تعارض بعد تحديث الحزمة، يتجاوزه
ويُدرجه في النهاية بدل استبداله، حتى تستطيع مقارنته ودمجه يدويًا إن أردت النسخة الأحدث.

```
$ python speclite/install.py
Installing speclite into: /path/to/project
  -> .speclite/    (scripts, templates, project state)
  -> .agents/commands/  (the 5 phase command files + map)
  -> skills/       (Skill-format wrappers, one per phase + the manager)

Installed 41 file(s).
No conflicts.

Done. Next step: run /speclite.constitution (Phase 1) to get started.
```

### المدير

لا تحتاج لتذكّر ترتيب المراحل، ولا لتتبّع أين توقفت - هذا بالضبط دور `status.py` / `status.ps1`.
شغّله في أي وقت (أي وكيل ذكاء اصطناعي يستخدم هذه المهارة يشغّله تلقائيًا، دائمًا، قبل فعل أي شيء):

```
$ python .speclite/scripts/python/status.py --json
{
  "INSTALLED": true,
  "REPO_ROOT": "/path/to/project",
  "ALL_FEATURES": ["001-oauth2-login"],
  "HAS_PROJECT_PRINCIPLES": true,
  "ACTIVE_FEATURE": "/path/to/project/specs/001-oauth2-login",
  "NEXT_PHASE": "plan",
  "REASON": "plan.md not created yet.",
  "NEEDS_USER_INPUT": false,
  "MAP_SUGGESTION": null,
  "MAP_REASON": null
}
```

`NEXT_PHASE` يخبرك دومًا بما يجب فعله تاليًا - حتى لو ابتعدت (أنت أو الوكيل) أسبوعًا كاملًا
ونسيت كل شيء. لو وُجدت عدة ميزات ولا واحدة منها مُفعَّلة كـ"نشطة"، يُرجِع `status` القيمة
`ambiguous` بدل التخمين، فيسأل الوكيل المستخدم عن الميزة المطلوب استئنافها بدل الاختيار
الخاطئ بصمت. أما `MAP_SUGGESTION` (`"build"` / `"update"` / `null`) فهو حقل معلوماتي منفصل
تمامًا بخصوص خريطة المشروع الاختيارية - انظر أدناه - ولا يؤثر إطلاقًا على `NEXT_PHASE`.

### لماذا 5 مراحل بدل 10 في Spec Kit - ولماذا ليس أقل؟

| # | أمر/أوامر Spec Kit | مرحلة speclite | لماذا الدمج بهذا الشكل (وليس أكثر) |
|---|---|---|---|
| 1 | `constitution` | **1. Constitution** | أُبقيت مرحلة مستقلة، وأُبقيت ملفًا واحدًا لـ *كل المشروع* - تمامًا كنموذج Spec Kit الأصلي، وليست لكل ميزة. قاعدة MUST غير قابلة للتفاوض: أي تعارض يُكتشف لاحقًا يوقف المرحلة ويتطلب رجوعًا واعيًا إلى هنا، وليس تعديلًا صامتًا حولها. تم تبسيطها من مراسم semantic-version/Sync-Impact-Report الخاصة بـ Spec Kit إلى ملف عادي. |
| 2، 3 | `specify` + `clarify` | **2. Specify** | دُمجتا - التوضيح أرخص فور صياغة المواصفة مباشرة، بينما السياق ما زال محمَّلًا. حافظتُ بأمانة على قواعد التوضيح الأصلية لـ Spec Kit (حد 5 أسئلة، سؤال واحد كل مرة، صيغة الخيار الموصى به، تصنيف التغطية) عبر `clarify-taxonomy.md`، بدل نسخة مختصرة. |
| 4، 6 | `plan` + `checklist` | **3. Plan** | دُمجتا - قائمة التحقق هي بوابة جودة *على الخطة نفسها* ("اختبارات وحدة للمتطلبات")، فمكانها الطبيعي هو نفس مكان كتابة الخطة، تُصحَّح مباشرة بدل جدولتها كأمر منفصل لاحق. القواعد الكاملة محفوظة في `checklist-guide.md`. |
| 5، 7 | `tasks` + `analyze` | **4. Tasks** | دُمجتا، وأُبقيتا عمدًا **منفصلتين عن كل من Plan وImplement** (مسودة سابقة لهذه الأداة دمجت التحليل ضمن الفحص الأولي لـ implement، وكان ذلك سطحيًا جدًا) - التحليل يحتاج قائمة المهام الكاملة ليفحص التغطية عليها، ويجب أن يعمل *قبل* كتابة الكود، لا بعده. قواعد الفحص الكاملة محفوظة في `analyze-guide.md`. |
| 8، 9 | `implement` + `converge` | **5. Implement** | دُمجتا - بدل أمر تدقيق منفصل يعمل بعد implement (يكتفي بإضافة مهام والتوقف)، يُغلق speclite الحلقة فورًا: أي فجوة تُكتشف في الفحص النهائي تُنفَّذ في نفس الجولة، لا تُترك لتشغيل يدوي لاحق. |
| 10 | `taskstoissues` | *(إضافة اختيارية، غير مبرمجة)* | خاص بـ GitHub ويهم فئة محدودة من المستخدمين؛ موثّق كنمط يُنفَّذ عند الحاجة في `SKILL.md` بدل أن يكون مرحلة مخصصة. |

النتيجة الصافية: **5 مراحل، 3 ملفات لكل ميزة (`spec.md`, `plan.md`, `tasks.md`) بالإضافة إلى
`references/` و`logs/`**، بدل حتى 8 ملفات لكل ميزة في Spec Kit الأصلي (spec, plan, tasks,
research, data-model, quickstart, contracts/, checklists/) و10 أوامر - مع الحفاظ الكامل على
آليات الجودة الفعلية لكل مرحلة (تصنيف أسئلة التوضيح، فلسفة قائمة تحقق المتطلبات، فحوصات
التحليل، تدرّج الخطورة) عبر ملفات `*-guide.md` المرجعية، دون تخفيف. أُسقطت آلية extension-hooks
(`.specify/extensions.yml`) لنفس سبب "تقليل الأجزاء المتحركة".

**إضافة حقيقية واحدة** تتجاوز أوامر Spec Kit العشرة الأصلية: **خريطة المشروع** (انظر أدناه) -
ليست مفهومًا موجودًا في Spec Kit، أُضيفت لأن تتبّع متطلبات كل ميزة إلى الكود الفعلي، على مستوى
المشروع كله، قيّم بما يكفي لتبرير قدرة سادسة اختيارية تمامًا.

### خريطة المشروع (اختيارية، ليست إحدى المراحل الخمس)

خريطة مرجعية على مستوى المشروع كله تنمو مع المشروع - `PROJECT_MAP.md`، `PRD_TRACEABILITY.md`،
`ARCHITECTURE_MAP.md`، `FILE_INDEX.md`، و`PROJECT_MAP.json` - تتيح لأي وكيل أو مطوّر يأتي لاحقًا
فهم المشروع بسرعة ودقة، بما في ذلك كيف تتتبّع متطلبات كل ميزة إلى الكود الفعلي الذي ينفّذها.
غير مُلزِمة، غير مطلوبة أبدًا، ولا تعمل بصمت - تُقترَح فقط.

- **تعيش داخل `specs/` مباشرة**، كملفات شقيقة لمجلدات `specs/NNN-feature/` (وليس داخل أي منها) -
  على مستوى المشروع كله مثل الدستور، وليست لكل ميزة مثل spec/plan/tasks.
- **أمر واحد، `commands/speclite.map.md`، ووضعان يُكتشفان تلقائيًا**: `setup_map_stage.py` /
  `setup-map-stage.ps1` يُرجِع `MODE: build` إن لم يوجد `specs/PROJECT_MAP.md` بعد، أو
  `MODE: update` إن وُجد.
- **تراكمية بالتصميم، فتبقى رخيصة عند إعادة التشغيل**: عند التحديث، يحسب السكربت
  `CHANGED_FILES` - عبر `git diff` منذ آخر مزامنة مسجَّلة (أو الرجوع لأوقات تعديل الملفات إن لم
  يوجد تاريخ git صالح) - فلا يقرأ الوكيل إلا ما تغيّر فعلًا، وليس المشروع كاملًا مجددًا. حالة
  المزامنة (آخر commit / الوقت) محفوظة كتعليق مخفي `<!-- speclite-map-state -->` أعلى
  `PROJECT_MAP.md` نفسه - بدون ملف سجل منفصل، بالتصميم (هذه القدرة الوحيدة التي لا تتكامل مع
  `logs/`).
- **`PROJECT_MAP.json`** - نسخة هيكلية مضغوطة فقط من نفس العلاقات (متطلب ← ملفات ← رموز ← حالة؛
  ملف ← غرض ← تبعيات)، مفعّلة افتراضيًا لأنها لا تكرر أبدًا نثر Markdown، فتبقى رخيصة التحديث.
  مفيدة لو أردت لاحقًا أن تستعلمها أداة أو سكربت آخر برمجيًا بدل تحليل Markdown.
- **`status.py` / `status.ps1` يضيفان حقل `MAP_SUGGESTION` معلوماتيًا بحتًا** (`"build"` /
  `"update"` / `null`) لا يؤثر إطلاقًا على `NEXT_PHASE`. يُظهره المدير فقط في اللحظات المناسبة:
  بعد `/speclite.constitution` إن كان المستودع يحوي كودًا فعليًا مسبقًا (`MAP_SUGGESTION: build`
  - تبنّي مشروع قائم)، أو بعد نجاح الفحص النهائي لـ `/speclite.implement`
  (`MAP_SUGGESTION: update`). دائمًا عرض، أبدًا تلقائي، ولا يتكرر في نفس الجلسة إن رُفض.
- قواعد الدقة الكاملة (تحقّق، لا تخمّن؛ فرّق بين المتطلب المذكور والتنفيذ الحالي والعلاقة
  المُستنتَجة؛ `needs verification` بدل يقين مُختلَق؛ فحص تحقق نهائي قبل الإنهاء) موجودة في
  `templates/map-guide.md`.

### بنية المجلدات

```
your-project/
├── speclite/                       # هذه الحزمة - أبقها، install.py آمن لإعادة التشغيل
│   └── tools/build_skills.py       # يعيد توليد skills/ من commands/ بعد أي تعديل
├── .agents/
│   └── commands/                   # ملفات الأوامر الخمسة + الخريطة، بشكل مسطّح
│       ├── speclite.constitution.md
│       ├── speclite.specify.md
│       ├── speclite.plan.md
│       ├── speclite.tasks.md
│       ├── speclite.implement.md
│       └── speclite.map.md
├── skills/                         # نسخ بصيغة Skill - نفس المحتوى، مستقلة بذاتها
│   ├── speclite/SKILL.md           # المدير (نسخة من speclite/SKILL.md بمسارات مُصحَّحة)
│   ├── speclite-constitution/SKILL.md
│   ├── speclite-specify/SKILL.md
│   ├── speclite-plan/SKILL.md
│   ├── speclite-tasks/SKILL.md
│   ├── speclite-implement/SKILL.md
│   └── speclite-map/SKILL.md
├── .speclite/
│   ├── feature.json                # أي specs/NNN-* هي "النشطة" حاليًا
│   ├── memory/
│   │   └── principles.md           # الدستور الوحيد لكل المشروع (نموذج Spec Kit الأصلي)
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── principles-template.md
│   │   ├── clarify-taxonomy.md     # دليل مرجعي للمرحلة 2
│   │   ├── checklist-guide.md      # دليل مرجعي للمرحلة 3
│   │   ├── analyze-guide.md        # دليل مرجعي للمرحلة 4
│   │   ├── map-guide.md            # دليل مرجعي لخريطة المشروع
│   │   ├── project-map-template.md
│   │   ├── prd-traceability-template.md
│   │   ├── architecture-map-template.md
│   │   ├── file-index-template.md
│   │   └── overrides/              # ضع ملفًا بنفس الاسم هنا لتجاوز أي قالب
│   └── scripts/
│       ├── python/                 # status.py, constitution_setup.py, new_feature.py,
│       │                           # setup_stage.py, setup_tasks_stage.py,
│       │                           # check_prerequisites.py, setup_map_stage.py, common.py
│       └── powershell/             # نفس المجموعة، PascalCase/.ps1
└── specs/
    ├── PROJECT_MAP.md               # اختياري - انظر "خريطة المشروع" أعلاه، شقيقة
    ├── PRD_TRACEABILITY.md          # لمجلدات الميزات أدناه، وليست داخل أي منها
    ├── ARCHITECTURE_MAP.md
    ├── FILE_INDEX.md
    ├── PROJECT_MAP.json
    └── 001-your-feature/
        ├── spec.md
        ├── plan.md
        ├── tasks.md                 # يتضمن checkboxes الـ Analysis Pass / Final Gap-Check
        ├── references/
        │   ├── PRD/     ├── images/   ├── fonts/
        │   ├── sounds/  ├── videos/   ├── data/
        │   └── docs/
        └── logs/                    # مجلد واحد مسطّح - أدلة حرة الشكل، ينظّمها الوكيل
            ├── test-results/          # يُنشئه الوكيل عند الحاجة
            ├── screenshots/           # يُنشئه الوكيل عند الحاجة
            └── notes/                 # يُنشئه الوكيل عند الحاجة
```

#### الأوامر مقابل المهارات - لماذا كلاهما؟

نفس التقسيم الذي يستخدمه Spec Kit نفسه: `.agents/commands/*.md` ملف مسطّح يقرأه الوكيل الذي
يدعم أوامر مخصّصة على مستوى المشروع؛ `skills/<name>/SKILL.md` هي نفس التعليمات مُغلَّفة بصيغة
Skill (ترويسة فيها `name`، `description`، `compatibility`، `metadata.source`) للوكلاء التي
تكتشف القدرات بهذه الطريقة بدلًا من ذلك - Claude من بينها. المحتوى متطابق عمدًا، وليس مجرد
متشابه: `tools/build_skills.py` يولّد كل ملف تحت `skills/` مباشرة من الملف المقابل تحت
`commands/`، فلا يمكن أن ينحرفا عن بعضهما طالما أعدت تشغيله بعد تعديل أي أمر. كلاهما يُثبَّت
تلقائيًا؛ أي واحد يقرؤه وكيل معيّن فعليًا يعتمد كليًا على ذلك الوكيل، لا عليك.

### إشارات اكتمال المرحلة (معتمدة على المستند نفسه، بأسلوب Spec Kit)

لا يوجد سجل فحص منفصل يقرر اكتمال أي مرحلة - `status.py`/`status.ps1` يقرأ المستند الذي تنتجه
تلك المرحلة مباشرة، بنفس طريقة عمل Spec Kit نفسه:

| المرحلة | تكتمل عندما |
|---|---|
| 1. Constitution | `.speclite/memory/principles.md` موجود (يُتحقَّق منه، لا يُشترَط) |
| 2. Specify | `spec.md` لا يحوي أي ماركر `[NEEDS CLARIFICATION]` متبقٍّ |
| 3. Plan | قائمة التحقق قبل التنفيذ في `plan.md` معلَّمة بالكامل |
| 4. Tasks | مربع `Analysis complete` في `tasks.md` معلَّم |
| 5. Implement | كل مهمة في `tasks.md` معلَّمة `[X]` + مربع `Final Gap-Check` معلَّم |

كلا مربعي الاختيار الجديدين للمرحلتين 4 و5 موجودان مباشرة في `tasks-template.md`، بجانب قائمة
المهام تمامًا - علِّمهما فقط عند الاكتمال الحقيقي، أبدًا كشكليات.

### `logs/` - مجلد واحد مسطّح لكل ميزة، أدلة حرة الشكل فقط

غير مقسَّم حسب المرحلة، ولا يقرؤه `status` أبدًا لتحديد الاكتمال - مكان بحت للأدلة الداعمة:

```
# بدون ترويسة، بدون جدول - فقط ملفات، ينظّمها الوكيل كما يراه مناسبًا
logs/
├── test-results/   # نتائج اختبارات آلية / مخرجات ترمنال
├── screenshots/    # لقطات واجهة تثبت عمل مهمة ما - بما فيها أي شيء
│                   # قدّمه المستخدم سابقًا في المحادثة؛ احفظ نسخة هنا
│                   # بدل تركه فقط في سجل المحادثة
└── notes/          # ملخص موجز لقرار أو نقاش يستحق الحفظ ولم
                     # يُسجَّل أصلًا في spec.md / plan.md / tasks.md
```

**موصى به: استثناؤه من ضبط الإصدار (git).** أضف هذا إلى `.gitignore` الخاص بمشروعك:

```
specs/*/logs/
```

لا يعدّل speclite ملف `.gitignore` بنفسه أبدًا - يقترح ذلك فقط، ضمن المحادثة، ويترك الإضافة
لك. هذا المجلد غالبًا يحوي أدلة كبيرة الحجم أو قابلة للاستغناء عنها لا مصدر حقيقة، كما أن
استثناءه يبقي فحص `git diff` التراكمي لخريطة المشروع نظيفًا من ضجيج الصور/السجلات (انظر "خريطة
المشروع" أعلاه).

محتوى `logs/` مفيد أيضًا كمُدخَل عند بناء أو تحديث خريطة المشروع - ملاحظة تشرح *لماذا* بُني شيء
ما بطريقة معينة غالبًا تبقى محفوظة هناك حتى لو لم تكن واضحة من الكود وحده؛ `map-guide.md` يوجّه
الوكيل الذي يبني الخريطة للاطلاع عليها.

### يمكن أن يمتد العمل الكبير أو المعقّد عبر أكثر من جولة أو جلسة

لا تحتاج أي من المراحل الخمس للاكتمال في جولة واحدة. مواصفة كبيرة، خطة معقدة، قائمة مهام
طويلة، أو تنفيذ مهام كثيرة - كل ذلك يمكن أن يستغرق بشكل مشروع عدة جولات، أو أن يغلق المستخدم
المحادثة ويعود لاحقًا - `status` ومربعات الاختيار المعتمدة على المستند موجودة بالضبط لهذا: التوقف
منتصف مرحلة ما لا يكلّف شيئًا عند الاستئناف. ضغط أو تسريع عمل كبير فقط لجعل مرحلة ما تبدو
"مكتملة" في جولة واحدة ينتج مخرجات أضعف، وغالبًا يكلّف أكثر إجمالًا (وقتًا وتوكنز) من إنجازه
بشكل صحيح عبر العدد الحقيقي من الجولات التي يحتاجها. هذا مذكور صراحة في
`commands/speclite.tasks.md` (فحص التحليل) و`commands/speclite.implement.md` (تنفيذ المهام
والفحص النهائي)، ولدى `map-guide.md` إرشاد مماثل لبناء `/speclite.map` على مشروع كبير.

### البدء السريع

```bash
# 1. التثبيت مرة واحدة لكل مشروع (غير مُتلِف، آمن لإعادة التشغيل)
python speclite/install.py

# 2. دع المدير يتولى الأمر من هنا - يشغّل status، يرى NEXT_PHASE: constitution،
#    يساعد في صياغة principles.md الخاص بالمشروع، ثم يواصل تسلسل المراحل تلقائيًا:
#      constitution -> specify -> plan -> tasks -> implement
#
# 3. ضع أي PRD/صور شاشة/خطوط/إلخ في مجلدات references/ الفرعية للميزة النشطة
#    في أي وقت - كل مرحلة تتحقق منها قبل افتراض أي شيء.
```

### ملفات الأوامر ونظائرها من المهارات

- `commands/speclite.constitution.md` → `skills/speclite-constitution/SKILL.md`
- `commands/speclite.specify.md` → `skills/speclite-specify/SKILL.md`
- `commands/speclite.plan.md` → `skills/speclite-plan/SKILL.md`
- `commands/speclite.tasks.md` → `skills/speclite-tasks/SKILL.md`
- `commands/speclite.implement.md` → `skills/speclite-implement/SKILL.md`
- `commands/speclite.map.md` → `skills/speclite-map/SKILL.md` *(اختياري، ليست إحدى المراحل الخمس)*

كل ملف `commands/*.md` هو المصدر الأساسي - ملف تعليمات مستقل بذاته يقرأه وكيل الذكاء الاصطناعي
قبل تنفيذ تلك المرحلة، بنفس اتفاقية ملفات الأوامر `.md` الخاصة بـ Spec Kit نفسه. الملف المقابل
`skills/*/SKILL.md` مولَّد منه (انظر `tools/build_skills.py`)؛ بعد تعديل أي أمر، أعد تشغيل ذلك
السكربت للحفاظ على تطابقهما. `SKILL.md` في جذر الحزمة (ونظيره المولَّد `skills/speclite/SKILL.md`)
هو المدير الذي يقرر أي مرحلة يقرأها تاليًا، باستخدام `status.py` / `status.ps1`.

---

## English

A 5-phase clone of [GitHub Spec Kit](https://github.com/github/spec-kit)'s spec-driven
development workflow, with a built-in manager that auto-detects which phase to run next, a
`references/` folder per feature for user-supplied source material, a single flat `logs/`
folder per feature for free-form evidence (test output, screenshots, session notes) the agent
organizes by type, and an optional, non-blocking Project Map that grows with the project via
cheap incremental updates. Installs as both flat `.agents/commands/*.md` files and
self-contained `skills/<name>/SKILL.md` folders, matching Spec Kit's own dual distribution.

### Install

1. Copy this whole `speclite/` folder into your project root, next to your other project files.
2. Run the installer from the project root:
   - Linux/macOS: `python speclite/install.py`
   - Windows: `pwsh speclite/Install.ps1`

The installer deploys to three locations and **only ever writes inside them** - nothing else in
your project is touched:

- `.speclite/` - internal machinery: scripts, templates, and project state.
- `.agents/commands/` - the 5 phase command files plus the Project Map command, flat, for
  any agent that reads project-level custom slash-commands.
- `skills/` - the same 6 command files plus the manager, each as a self-contained
  `skills/<name>/SKILL.md` folder, matching Spec Kit's own `skills/speckit-<name>/SKILL.md`
  layout.

It never overwrites a file that already exists at any destination; if you re-run it after
updating this package, conflicting files are skipped and listed at the end instead of being
clobbered, so you can diff and merge them by hand if you want the newer version.

```
$ python speclite/install.py
Installing speclite into: /path/to/project
  -> .speclite/    (scripts, templates, project state)
  -> .agents/commands/  (the 5 phase command files)
  -> skills/       (Skill-format wrappers, one per phase + the manager)

Installed 41 file(s).
No conflicts.

Done. Next step: run /speclite.constitution (Phase 1) to get started.
```

### The manager

You don't need to remember the phase order, and you don't need to track where you left off -
that's what `status.py` / `status.ps1` is for. Run it any time (an AI agent using this skill
runs it automatically, always, before doing anything else):

```
$ python .speclite/scripts/python/status.py --json
{
  "INSTALLED": true,
  "REPO_ROOT": "/path/to/project",
  "ALL_FEATURES": ["001-oauth2-login"],
  "HAS_PROJECT_PRINCIPLES": true,
  "ACTIVE_FEATURE": "/path/to/project/specs/001-oauth2-login",
  "NEXT_PHASE": "plan",
  "REASON": "plan.md not created yet.",
  "NEEDS_USER_INPUT": false,
  "MAP_SUGGESTION": null,
  "MAP_REASON": null
}
```

`NEXT_PHASE` is always exactly what to do next - even if you (or the agent) walk away for a week
and come back having forgotten everything. If several features exist and none is marked active,
`status` reports `ambiguous` instead of guessing, so the agent asks which one to resume rather
than picking wrong silently. `MAP_SUGGESTION` (`"build"` / `"update"` / `null`) is a separate,
purely informational nudge about the optional Project Map - see below - and never affects
`NEXT_PHASE`.

### Why 5 phases instead of Spec Kit's 10 - and why not fewer?

| # | Spec Kit command(s) | speclite phase | Why merged this way (and not further) |
|---|---|---|---|
| 1 | `constitution` | **1. Constitution** | Kept as its own phase, and kept as ONE file for the *entire project* - exactly like Spec Kit's own model, never per-feature. A MUST rule is non-negotiable: any conflict found later stops the phase and requires a conscious trip back here, never a silent edit around it. Simplified from Spec Kit's own semantic-version/Sync-Impact-Report ceremony to a plain file. |
| 2, 3 | `specify` + `clarify` | **2. Specify** | Merged - clarification is cheapest immediately after drafting the spec, while context is loaded. Kept faithful to Spec Kit's own clarify rules (5-question cap, one at a time, recommended-option format, coverage taxonomy) via `clarify-taxonomy.md`, rather than a shortcut version. |
| 4, 6 | `plan` + `checklist` | **3. Plan** | Merged - the checklist is a quality gate *on the plan itself* ("unit tests for requirements"), so it belongs right where the plan is written, fixed inline instead of scheduled as a separate later command. Full rules preserved in `checklist-guide.md`. |
| 5, 7 | `tasks` + `analyze` | **4. Tasks** | Merged, and deliberately kept **separate from both plan and implement** (an earlier draft of this tool merged analyze into implement's pre-flight, which was too shallow) - analyze needs the finished task list to check coverage against, and needs to run *before* code is written, not after. Full detection-pass rules preserved in `analyze-guide.md`. |
| 8, 9 | `implement` + `converge` | **5. Implement** | Merged - rather than a separate audit command run after implement (which just appends tasks and stops), speclite closes the loop immediately: gaps found in the final check are implemented in the same pass, not left for a manual follow-up run. |
| 10 | `taskstoissues` | *(optional extra, not scripted)* | GitHub-specific and only relevant to a subset of users; documented as an ad-hoc pattern in `SKILL.md` instead of a dedicated phase. |

Net effect: **5 phases, 3 files per feature (`spec.md`, `plan.md`, `tasks.md`) plus
`references/` and `logs/`**, instead of Spec Kit's up to 8 files per feature (spec, plan, tasks,
research, data-model, quickstart, contracts/, checklists/) and 10 commands - while keeping every
phase's actual quality mechanics (clarification taxonomy, requirements-checklist philosophy,
analyze detection passes, severity grading) intact via the `*-guide.md` reference docs, not
watered down. Extension-hook machinery (`.specify/extensions.yml`) was dropped for the same
"fewer moving parts" reason.

One genuine **addition** beyond Spec Kit's original 10 commands: the **Project Map** (see
below) - not a Spec Kit concept, added because tracing every feature's requirements to actual
code, project-wide, is valuable enough to justify a 6th, strictly optional capability.

### Project Map (optional, not one of the 5 phases)

A project-wide reference map that grows alongside the project - `PROJECT_MAP.md`,
`PRD_TRACEABILITY.md`, `ARCHITECTURE_MAP.md`, `FILE_INDEX.md`, and `PROJECT_MAP.json` - so any
agent or developer coming later can understand the project quickly and accurately, including
how every feature's Functional Requirements trace to the actual code that implements them.
Never blocking, never required, and never run silently - only ever suggested.

- **Lives in `specs/` directly**, as a sibling of `specs/NNN-feature/` (not inside any one of
  them) - project-wide like the constitution, not per-feature like spec/plan/tasks.
- **One command, `commands/speclite.map.md`, two auto-detected modes**: `setup_map_stage.py` /
  `setup-map-stage.ps1` reports `MODE: build` if `specs/PROJECT_MAP.md` doesn't exist yet, or
  `MODE: update` if it does.
- **Incremental by design, so re-running it stays cheap**: on update, the script computes
  `CHANGED_FILES` - a `git diff` since the last recorded sync (falling back to file
  modification times if there's no usable git history) - so the agent only reads what actually
  changed, never the whole project again. The sync state (last commit / timestamp) lives in an
  invisible `<!-- speclite-map-state -->` comment at the top of `PROJECT_MAP.md` itself - no
  separate log file, by design (this is the one capability with no `logs/` integration).
- **`PROJECT_MAP.json`** - a compact, structural-only mirror of the same relationships
  (requirement → files → symbols → status; file → purpose → dependencies), enabled by default
  because it never duplicates the Markdown prose, so it stays cheap to keep in sync. Useful if
  you ever want another tool or script to query the map programmatically instead of parsing
  Markdown.
- **`status.py` / `status.ps1` add a purely informational `MAP_SUGGESTION`** field
  (`"build"` / `"update"` / `null`) that never affects `NEXT_PHASE`. The manager only surfaces
  it at natural breakpoints: right after `/speclite.constitution` if the repo already has real
  code (`MAP_SUGGESTION: build` - onboarding an existing project), or right after a
  `/speclite.implement` gap-check passes (`MAP_SUGGESTION: update`). It's always an offer, never
  automatic, and it isn't repeated in the same session if declined.
- Full accuracy rules (verify, don't guess; distinguish stated requirement / current
  implementation / inferred relationship; `needs verification` over invented certainty; a
  Validation Pass before finishing) live in `templates/map-guide.md`.

### Directory layout

```
your-project/
├── speclite/                       # this package - keep it, install.py re-runs safely
│   └── tools/build_skills.py       # regenerates skills/ from commands/ after an edit
├── .agents/
│   └── commands/                   # the 5 phase command files + map, flat
│       ├── speclite.constitution.md
│       ├── speclite.specify.md
│       ├── speclite.plan.md
│       ├── speclite.tasks.md
│       ├── speclite.implement.md
│       └── speclite.map.md
├── skills/                         # Skill-format wrappers - same content, self-contained
│   ├── speclite/SKILL.md           # the manager (mirrors speclite/SKILL.md, paths rewritten)
│   ├── speclite-constitution/SKILL.md
│   ├── speclite-specify/SKILL.md
│   ├── speclite-plan/SKILL.md
│   ├── speclite-tasks/SKILL.md
│   ├── speclite-implement/SKILL.md
│   └── speclite-map/SKILL.md
├── .speclite/
│   ├── feature.json                # which specs/NNN-* is "active"
│   ├── memory/
│   │   └── principles.md           # the ONE project-wide constitution (Spec Kit's own model)
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── principles-template.md
│   │   ├── clarify-taxonomy.md     # Phase 2 reference guide
│   │   ├── checklist-guide.md      # Phase 3 reference guide
│   │   ├── analyze-guide.md        # Phase 4 reference guide
│   │   ├── map-guide.md            # Project Map reference guide
│   │   ├── project-map-template.md
│   │   ├── prd-traceability-template.md
│   │   ├── architecture-map-template.md
│   │   ├── file-index-template.md
│   │   └── overrides/              # drop a same-named file here to override any template
│   └── scripts/
│       ├── python/                 # status.py, constitution_setup.py, new_feature.py,
│       │                           # setup_stage.py, setup_tasks_stage.py,
│       │                           # check_prerequisites.py, setup_map_stage.py, common.py
│       └── powershell/             # same set, PascalCase/.ps1
└── specs/
    ├── PROJECT_MAP.md               # optional - see "Project Map" above, siblings of
    ├── PRD_TRACEABILITY.md          # the feature directories below, never inside one
    ├── ARCHITECTURE_MAP.md
    ├── FILE_INDEX.md
    ├── PROJECT_MAP.json
    └── 001-your-feature/
        ├── spec.md
        ├── plan.md
        ├── tasks.md                 # includes the Analysis Pass / Final Gap-Check checkboxes
        ├── references/
        │   ├── PRD/     ├── images/   ├── fonts/
        │   ├── sounds/  ├── videos/   ├── data/
        │   └── docs/
        └── logs/                    # ONE flat folder - free-form evidence only, agent-organized
            ├── test-results/          # agent-created, as needed
            ├── screenshots/           # agent-created, as needed
            └── notes/                 # agent-created, as needed
```

#### Commands vs. Skills - why both?

Same split Spec Kit itself uses: `.agents/commands/*.md` is a flat file an agent reads when it
supports project-level custom slash-commands; `skills/<name>/SKILL.md` is the same instructions
wrapped in the Skill format (frontmatter with `name`, `description`, `compatibility`,
`metadata.source`) for agents that discover capabilities that way instead - Claude among them.
The content is intentionally identical, not just similar: `tools/build_skills.py` generates
every file under `skills/` directly from the matching file under `commands/`, so they can never
drift apart as long as you re-run it after editing a command. Both get installed automatically;
which one a given agent actually reads depends entirely on that agent, not on you.

### Phase completion signals (artifact-based, Spec Kit's own style)

No separate check-log decides whether a phase is done - `status.py`/`status.ps1` reads the
artifact that phase produces directly, the same way Spec Kit itself works:

| Phase | Done when |
|---|---|
| 1. Constitution | `.speclite/memory/principles.md` exists (checked, not gated) |
| 2. Specify | `spec.md` has no `[NEEDS CLARIFICATION]` marker left |
| 3. Plan | `plan.md`'s Pre-Implementation Checklist is fully checked |
| 4. Tasks | `tasks.md`'s `Analysis complete` checkbox is ticked |
| 5. Implement | every task in `tasks.md` is `[X]` AND its `Final Gap-Check` checkbox is ticked |

Both new Phase 4/5 checkboxes live directly in `tasks-template.md`, right next to the task
list - tick them only when genuinely true, never as a formality.

### `logs/` - one flat folder per feature, free-form evidence only

Not split by phase, and never read by `status` to decide completion - purely a place for
supporting evidence:

```
# no header, no table - just files, organized by the agent as it sees fit
logs/
├── test-results/   # automated test / terminal output
├── screenshots/    # UI captures proving a task works - including anything the user
│                   # already shared in chat; save a copy here instead of leaving it
│                   # only in the conversation history
└── notes/          # a brief write-up of a decision or exchange worth keeping that
                     # isn't already in spec.md / plan.md / tasks.md
```

**Recommended: exclude it from version control.** Add this to your project's `.gitignore`:

```
specs/*/logs/
```

speclite never edits `.gitignore` itself - only suggests it, in conversation, and leaves adding
it to you. It tends to hold large or disposable evidence rather than source of truth, and
excluding it also keeps the Project Map's incremental `git diff` scan free of screenshot/log
noise (see "Project Map" above).

`logs/` content is also useful input when building or updating the Project Map - a note
explaining *why* something was built a certain way often survives there even when it's not
obvious from the code alone; `map-guide.md` tells the map-building agent to check it.

### Large or complex work can span multiple turns or sessions

None of the 5 phases need to finish in a single turn. A big spec, a large plan, a long task
list, or implementing many tasks can legitimately take several turns, or the user closing the
chat and coming back later - `status` and the artifact-based checkboxes above exist precisely so
that pausing mid-phase costs nothing to resume. Compressing or rushing a large piece of work
just to make a phase appear "done" in one turn produces weaker output and often costs more
overall (in time and tokens) than doing it right across as many turns as it actually needs. This
is called out specifically in `commands/speclite.tasks.md` (the analyze pass) and
`commands/speclite.implement.md` (task execution and the final gap-check), and `map-guide.md`
has the equivalent guidance for a large `/speclite.map` build.

### Quick start

```bash
# 1. Install once per project (non-destructive, safe to re-run)
python speclite/install.py

# 2. Let the manager take it from here - it runs status, sees NEXT_PHASE: constitution,
#    helps draft the project's principles.md, then keeps chaining phases automatically:
#      constitution -> specify -> plan -> tasks -> implement
#
# 3. Drop any PRD/screenshots/fonts/etc. into the active feature's references/ subfolders
#    at any point - every phase checks there before assuming anything.
```

### Command files and their Skill wrappers

- `commands/speclite.constitution.md` → `skills/speclite-constitution/SKILL.md`
- `commands/speclite.specify.md` → `skills/speclite-specify/SKILL.md`
- `commands/speclite.plan.md` → `skills/speclite-plan/SKILL.md`
- `commands/speclite.tasks.md` → `skills/speclite-tasks/SKILL.md`
- `commands/speclite.implement.md` → `skills/speclite-implement/SKILL.md`
- `commands/speclite.map.md` → `skills/speclite-map/SKILL.md` *(optional, not one of the 5 phases)*

Each `commands/*.md` file is the source of truth - a self-contained instruction file an AI agent
reads before running that phase, same convention as Spec Kit's own `.md` command files. The
matching `skills/*/SKILL.md` is generated from it (see `tools/build_skills.py`); after editing a
command, re-run that script to keep both in sync. `SKILL.md` at the package root (and its
generated twin `skills/speclite/SKILL.md`) is the manager that decides which phase to read next,
using `status.py` / `status.ps1`.


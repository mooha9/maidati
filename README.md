# مائدتي

تطبيق ويب عربي لمتابعة نظام غذائي مبني على تحليل معادن الشعر (أيض بطيء): وجبة الآن، فاحص الأطعمة، الوجبات، الوصفات، والتذكير.

- المصدر: `src/app.html` (قصاصة Artifact تعمل كما هي على claude.ai).
- البناء: `python3 build.py --env production|staging --out public` يغلّفها بصفحة كاملة + manifest + service worker + أيقونات.
- النشر: الدفع إلى `main` ينشر الإنتاج على `/maidati/`، والدفع إلى `staging` ينشر التجربة على `/maidati/staging/`.
- البيانات في localStorage على الجهاز فقط (مفتاح التجربة بلاحقة `-staging`).

"""File browser configuration constants."""

import os

FILE_BROWSERS = {
    'transfers': {
        'title': 'ملفات التحويل', 
        'icon': '📤',
        'help_text': 'تعرض ملفات التحويلات الفردية المباشرة التي تتم بين فرع وآخر بناءً على الاحتياج.',
        'csv': os.path.join("data", "output", "transfers", "csv"),
        'excel': os.path.join("data", "output", "transfers", "excel"),
        'step': 7, 
        'session_key': 'selected_source_branch', 
        'key_prefix': 'transfers',
        'category': 'transfers'
    },
    'surplus': {
        'title': 'الفائض المتبقي', 
        'icon': '📦',
        'help_text': 'تقارير توضح أصناف الفائض التي لا تزال موجودة في الفروع بعد تلبية احتياجات الفروع الأخرى.',
        'csv': os.path.join("data", "output", "remaining_surplus", "csv"),
        'excel': os.path.join("data", "output", "remaining_surplus", "excel"),
        'step': 9, 
        'session_key': 'surplus_filter', 
        'key_prefix': 'surplus',
        'category': 'surplus'
    },
    'shortage': {
        'title': 'النقص', 
        'icon': '⚠️',
        'help_text': 'تقارير توضح احتياجات الفروع التي لم يتم تغطيتها بالكامل من خلال التحويلات المتاحة.',
        'csv': os.path.join("data", "output", "shortage", "csv"),
        'excel': os.path.join("data", "output", "shortage", "excel"),
        'step': 10, 
        'session_key': 'shortage_filter', 
        'key_prefix': 'shortage',
        'category': 'shortage'
    },
    'merged': {
        'title': 'التحويلات المجمعة مع نقل الفائض المتبقي', 
        'icon': '📋',
        'help_text': 'ملفات التحويل النهائية التي تدمج التحويلات المباشرة مع عمليات إعادة توزيع الفائض لتعظيم الفائدة.',
        'csv': os.path.join(
            "data", "output", "combined_transfers", "merged", "csv"
        ),
        'excel': os.path.join(
            "data", "output", "combined_transfers", "merged", "excel"
        ),
        'step': 11, 
        'session_key': 'merged_selected_branch', 
        'key_prefix': 'merged',
        'category': 'merged'
    },
    'separate': {
        'title': 'التحويلات المنفصلة مع نقل الفائض المتبقي', 
        'icon': '📂',
        'help_text': 'تفاصيل التحويلات لكل صنف على حدة ناتجة عن عملية الدمج وإعادة التوزيع.',
        'csv': os.path.join(
            "data", "output", "combined_transfers", "separate", "csv"
        ),
        'excel': os.path.join(
            "data", "output", "combined_transfers", "separate", "excel"
        ),
        'step': 11, 
        'session_key': 'sep_selected_source', 
        'key_prefix': 'sep',
        'category': 'separate'
    },
    'sales_analysis': {
        'title': 'تحليل المبيعات', 
        'icon': '📈',
        'help_text': 'نتائج فحص وتدقيق بيانات المبيعات الخام قبل البدء في عملية التوزيع.',
        'csv': os.path.join("data", "output", "sales_analysis", "csv"),
        'excel': os.path.join("data", "output", "sales_analysis", "excel"),
        'step': 4, 
        'session_key': 'sales_analysis_filter', 
        'key_prefix': 'sales',
        'category': 'sales_analysis'
    },
    'collections': {
        'title': 'التحويلات المجمعة بدون نقل الفائض المتبقي', 
        'icon': '📦',
        'help_text': 'تحتوي هذه الملفات على تجميعة لكافة التحويلات الخارجة من الفرع إلى جميع الفروع الأخرى، مصنفة حسب نوع المنتج (أقراص، كريمات، إلخ)، وذلك دون إجراء أي عمليات نقل للفائض المتبقي.',
        'csv': os.path.join("data", "output", "transfers", "csv"),
        'excel': os.path.join("data", "output", "transfers", "excel"),
        'step': 7, 
        'session_key': 'collections_selected_branch', 
        'key_prefix': 'collections',
        'category': 'collections'
    },
}

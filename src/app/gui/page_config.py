"""Page configurations for config-driven pages."""

# Department placeholder pages config
DEPARTMENTS = {
    'sales': {'title': 'قسم المبيعات', 'icon': '💰', 'features': ['إدارة المبيعات اليومية', 'تقارير المبيعات', 'تحليل المبيعات', 'إدارة العملاء']},
    'accounting': {'title': 'قسم الحسابات', 'icon': '📊', 'features': ['إدارة الحسابات', 'التقارير المالية', 'الميزانيات', 'المراجعة']},
    'marketing': {'title': 'قسم التسويق', 'icon': '📈', 'features': ['إدارة الحملات', 'تحليل السوق', 'إدارة العملاء', 'تقارير التسويق']},
    'hr': {'title': 'قسم اتش ار', 'icon': '👥', 'features': ['إدارة الموظفين', 'الحضور والانصراف', 'المرتبات', 'التقييمات']},
}

# File browser pages config
import os
FILE_BROWSERS = {
    'transfers': {
        'title': 'ملفات التحويل', 'icon': '📤',
        'csv': os.path.join("data", "output", "transfers", "csv"),
        'excel': os.path.join("data", "output", "transfers", "excel"),
        'step': 7, 'session_key': 'selected_source_branch', 'key_prefix': 'transfers'
    },
    'surplus': {
        'title': 'الفائض المتبقي', 'icon': '📦',
        'csv': os.path.join("data", "output", "remaining_surplus", "csv"),
        'excel': os.path.join("data", "output", "remaining_surplus", "excel"),
        'step': 9, 'session_key': 'surplus_filter', 'key_prefix': 'surplus'
    },
    'shortage': {
        'title': 'النقص', 'icon': '⚠️',
        'csv': os.path.join("data", "output", "shortage", "csv"),
        'excel': os.path.join("data", "output", "shortage", "excel"),
        'step': 10, 'session_key': 'shortage_filter', 'key_prefix': 'shortage'
    },
    'merged': {
        'title': 'التحويلات المجمعة', 'icon': '📋',
        'csv': os.path.join("data", "output", "combined_transfers", "merged", "csv"),
        'excel': os.path.join("data", "output", "combined_transfers", "merged", "excel"),
        'step': 11, 'session_key': 'merged_selected_branch', 'key_prefix': 'merged'
    },
    'separate': {
        'title': 'التحويلات المنفصلة', 'icon': '📂',
        'csv': os.path.join("data", "output", "combined_transfers", "separate", "csv"),
        'excel': os.path.join("data", "output", "combined_transfers", "separate", "excel"),
        'step': 11, 'session_key': 'sep_selected_source', 'key_prefix': 'sep'
    },
}

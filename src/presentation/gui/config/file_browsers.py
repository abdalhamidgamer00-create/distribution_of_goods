"""File browser configuration constants."""

import os

FILE_BROWSERS = {
    'transfers': {
        'title': 'ملفات التحويل', 
        'icon': '📤',
        'csv': os.path.join("data", "output", "transfers", "csv"),
        'excel': os.path.join("data", "output", "transfers", "excel"),
        'step': 7, 
        'session_key': 'selected_source_branch', 
        'key_prefix': 'transfers'
    },
    'surplus': {
        'title': 'الفائض المتبقي', 
        'icon': '📦',
        'csv': os.path.join("data", "output", "remaining_surplus", "csv"),
        'excel': os.path.join("data", "output", "remaining_surplus", "excel"),
        'step': 9, 
        'session_key': 'surplus_filter', 
        'key_prefix': 'surplus'
    },
    'shortage': {
        'title': 'النقص', 
        'icon': '⚠️',
        'csv': os.path.join("data", "output", "shortage", "csv"),
        'excel': os.path.join("data", "output", "shortage", "excel"),
        'step': 10, 
        'session_key': 'shortage_filter', 
        'key_prefix': 'shortage'
    },
    'merged': {
        'title': 'التحويلات المجمعة', 
        'icon': '📋',
        'csv': os.path.join(
            "data", "output", "combined_transfers", "merged", "csv"
        ),
        'excel': os.path.join(
            "data", "output", "combined_transfers", "merged", "excel"
        ),
        'step': 11, 
        'session_key': 'merged_selected_branch', 
        'key_prefix': 'merged'
    },
    'separate': {
        'title': 'التحويلات المنفصلة', 
        'icon': '📂',
        'csv': os.path.join(
            "data", "output", "combined_transfers", "separate", "csv"
        ),
        'excel': os.path.join(
            "data", "output", "combined_transfers", "separate", "excel"
        ),
        'step': 11, 
        'session_key': 'sep_selected_source', 
        'key_prefix': 'sep'
    },
    'sales_analysis': {
        'title': 'تحليل المبيعات', 
        'icon': '📈',
        'csv': os.path.join("data", "output", "sales_analysis", "csv"),
        'excel': os.path.join("data", "output", "sales_analysis", "excel"),
        'step': 4, 
        'session_key': 'sales_analysis_filter', 
        'key_prefix': 'sales'
    },
}

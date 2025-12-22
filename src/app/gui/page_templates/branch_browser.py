"""Generic branch-based file browser template."""
import streamlit as st, os
from src.app.gui.utils.file_manager import list_output_files
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (BRANCH_LABELS, render_branch_selection_buttons, render_selected_branch_info,
                                     render_file_expander, render_download_all_button, get_key_from_label, get_branch_key_from_label)
from src.app.gui.page_templates import list_files_in_folder, get_matching_folders
from src.core.domain.branches.config import get_branches

def render_transfers_browser(title: str, icon: str, csv: str, excel: str, step: int, sk: str, kp: str) -> None:
    """Render transfer files browser with branch selection."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    from src.app.gui.utils.auth import check_password
    if not check_password(): st.stop()
    st.title(f"{icon} {title}"); st.markdown("---")
    st.subheader("📍 اختر الفرع المصدر")
    render_branch_selection_buttons(sk, kp)
    sel = render_selected_branch_info(sk, f"📂 عرض من: **{{branch_name}}**"); st.markdown("---")
    if not sel: return
    branches = get_branches()
    for tab, d, ext in zip(st.tabs(["📊 Excel", "📄 CSV"]), [excel, csv], [".xlsx", ".csv"]):
        with tab:
            if not os.path.exists(d): st.warning(f"يرجى تشغيل الخطوة {step} أولاً."); continue
            prefix = "transfers_excel_from_" if ext == ".xlsx" else "transfers_from_"
            files = []
            for b in (branches if sel == 'all' else [sel]):
                p = os.path.join(d, f"{prefix}{b}_to_other_branches")
                if os.path.exists(p): files.extend(list_output_files(p, [ext]))
            if not files: st.warning("لا توجد ملفات"); continue
            opts = ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches if sel == 'all' or b != sel]
            tgt = st.selectbox("إلى:", opts, key=f"{kp}_t_{ext}")
            tk = get_branch_key_from_label(tgt)
            filtered = [f for f in files if not tk or f"to_{tk}" in f['relative_path'] + f['name']]
            st.success(f"تم العثور على {len(filtered)} ملف")
            if filtered:
                import re
                for f in filtered:
                    m = re.search(r'(from_\w+_to_\w+)', f.get('relative_path', '') + f['name'])
                    f['zip_path'] = os.path.join(m.group(1) if m else 'other', f['name'])
                render_download_all_button(filtered, f"{kp}_{sel}_to_{tk or 'all'}_{ext[1:]}.zip")
            for f in filtered: render_file_expander(f, ext, key_prefix=kp)

def render_merged_browser(title: str, icon: str, csv: str, excel: str, step: int, sk: str, kp: str) -> None:
    """Render merged transfers browser."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    from src.app.gui.utils.auth import check_password
    if not check_password(): st.stop()
    st.title(f"{icon} {title}"); st.markdown("---")
    st.subheader("📍 اختر الفرع المرسل")
    render_branch_selection_buttons(sk, kp)
    sel = render_selected_branch_info(sk, f"📂 من: **{{branch_name}}**"); st.markdown("---")
    if not sel: return
    from src.app.gui.components import group_files_by_branch
    for tab, d, ext in zip(st.tabs(["📊 Excel", "📄 CSV"]), [excel, csv], [".xlsx", ".csv"]):
        with tab:
            if not os.path.exists(d): st.warning(f"يرجى تشغيل الخطوة {step} أولاً."); continue
            folders = get_matching_folders(d, 'combined_transfers_from_', sel)
            if not folders: st.info("لا توجد ملفات"); continue
            cat = st.selectbox("الفئة:", ["الكل"] + list(CATEGORY_NAMES.values()), key=f"{kp}_c_{ext}")
            ck = get_key_from_label(cat, CATEGORY_NAMES)
            files = []
            for fo in folders:
                for f in list_files_in_folder(fo['path'], [ext]):
                    f['branch'], f['folder_name'] = fo['branch'], fo['name']
                    files.append(f)
            if ck: files = [f for f in files if ck in f['name'].lower()]
            st.success(f"تم العثور على {len(files)} ملف")
            if files:
                for f in files: f['zip_path'] = os.path.join(f.get('folder_name', ''), f['name'])
                render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
            for b, fs in group_files_by_branch(files).items():
                st.subheader(BRANCH_LABELS.get(b, b))
                for f in fs: render_file_expander(f, ext, key_prefix=kp)
                st.markdown("---")

def render_separate_browser(title: str, icon: str, csv: str, excel: str, step: int, sk: str, kp: str) -> None:
    """Render separate transfers browser."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    from src.app.gui.utils.auth import check_password
    if not check_password(): st.stop()
    st.title(f"{icon} {title}"); st.markdown("---")
    st.subheader("📍 اختر الفرع المرسل")
    render_branch_selection_buttons(sk, kp)
    sel = render_selected_branch_info(sk, f"📂 من: **{{branch_name}}**"); st.markdown("---")
    if not sel: return
    branches = get_branches()
    from src.app.gui.components import group_files_by_source_target
    for tab, d, ext in zip(st.tabs(["📊 Excel", "📄 CSV"]), [excel, csv], [".xlsx", ".csv"]):
        with tab:
            if not os.path.exists(d): st.warning(f"يرجى تشغيل الخطوة {step} أولاً."); continue
            sources = get_matching_folders(d, 'transfers_from_', sel)
            if not sources: st.info("لا توجد ملفات"); continue
            tl = st.selectbox("إلى:", ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches], key=f"{kp}_t_{ext}")
            cl = st.selectbox("الفئة:", ["الكل"] + list(CATEGORY_NAMES.values()), key=f"{kp}_c_{ext}")
            tk, ck = get_key_from_label(tl, BRANCH_LABELS), get_key_from_label(cl, CATEGORY_NAMES)
            files = []
            for src in sources:
                for tgt_name in os.listdir(src['path']):
                    tp = os.path.join(src['path'], tgt_name)
                    if not os.path.isdir(tp) or not tgt_name.startswith('to_'): continue
                    tgt = tgt_name.replace('to_', '')
                    if tk and tgt != tk: continue
                    for f in list_files_in_folder(tp, [ext]):
                        f.update({'source_branch': src['branch'], 'target_branch': tgt, 'source_folder': src['name'], 'target_folder': tgt_name})
                        files.append(f)
            if ck: files = [f for f in files if ck in f['name'].lower()]
            st.success(f"تم العثور على {len(files)} ملف")
            if files:
                for f in files: f['zip_path'] = os.path.join(f['source_folder'], f['target_folder'], f['name'])
                render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
            for (s, t), fs in group_files_by_source_target(files).items():
                st.subheader(f"{BRANCH_LABELS.get(s, s)} ← {BRANCH_LABELS.get(t, t)}")
                for f in fs: render_file_expander(f, ext, key_prefix=f"{kp}_{s}_{t}")
                st.markdown("---")

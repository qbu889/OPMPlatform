# routes/excel2word_routes.py
from flask import Blueprint, render_template, request, send_file, current_app, session, flash
from pathlib import Path
import time
import threading
import os
from utils.excel_to_word_core import excel_to_word, verify_consistency
from utils.cleanup_thread import run_cleanup_loop

# 新建蓝图，前缀统一为 /excel2word
excel2word_bp = Blueprint('excel2word', __name__, url_prefix='/excel2word')

# 启动后台清理线程（仅启动一次）
cleanup_started = False


def init_cleanup():
    global cleanup_started
    if not cleanup_started:
        thread = threading.Thread(target=run_cleanup_loop, daemon=True)
        thread.start()
        cleanup_started = True


# 保存上传的Excel文件（复用现有UPLOAD_FOLDER配置，统一文件管理）
def save_excel_file(uploaded_file):
    """保存上传的Excel文件，生成唯一文件名"""
    upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
    excel_input_dir = upload_dir / "excel_input"
    word_output_dir = upload_dir / "word_output"
    os.makedirs(excel_input_dir, exist_ok=True)
    os.makedirs(word_output_dir, exist_ok=True)

    # 生成带时间戳的唯一文件名（避免覆盖）
    timestamp = int(time.time() * 1000)
    file_stem = Path(uploaded_file.filename).stem
    file_suffix = Path(uploaded_file.filename).suffix
    unique_filename = f"{file_stem}_{timestamp}{file_suffix}"
    target_path = excel_input_dir / unique_filename
    uploaded_file.save(target_path)
    return str(target_path), str(word_output_dir / f"{file_stem}_{timestamp}.docx")


# ---------------------- 路由定义 ----------------------
@excel2word_bp.route('/')
def excel2word_page():
    """Excel转Word主页面"""
    init_cleanup()  # 启动清理线程
    return render_template('excel2word.html',
                           excel_uploaded='excel_path' in session,
                           converted=session.get('converted', False),
                           verify_result=session.get('verify_result'),
                           module_stats=session.get('module_stats'))


@excel2word_bp.route('/upload', methods=['POST'])
def upload_excel():
    """处理Excel文件上传"""
    if 'excel_file' not in request.files:
        flash("未选择上传文件！", "error")
        return render_template('excel2word.html', excel_uploaded=False)

    file = request.files['excel_file']
    if file.filename == '' or not file.filename.endswith(('.xlsx', '.xls')):
        flash("请上传有效的Excel文件（.xlsx/.xls）！", "error")
        return render_template('excel2word.html', excel_uploaded=False)

    # 保存文件并记录路径到session
    excel_path, word_path = save_excel_file(file)
    session['excel_path'] = excel_path
    session['word_path'] = word_path
    session['converted'] = False
    session['verify_result'] = None
    flash("Excel文件上传成功！", "success")
    return render_template('excel2word.html', excel_uploaded=True)


@excel2word_bp.route('/convert')
def convert_excel_to_word():
    """执行Excel转Word转换"""
    if 'excel_path' not in session:
        flash("请先上传Excel文件！", "error")
        return render_template('excel2word.html', excel_uploaded=False)

    try:
        excel_path = session['excel_path']
        word_path = session['word_path']
        # 调用核心转换方法
        excel_to_word(excel_path, word_path)
        session['converted'] = True
        flash("Word文档生成成功！", "success")
    except Exception as e:
        flash(f"转换失败：{str(e)}", "error")
    return render_template('excel2word.html', excel_uploaded=True, converted=session.get('converted'))


@excel2word_bp.route('/verify')
def verify_word_content():
    """校验Excel与Word内容一致性"""
    if 'word_path' not in session or not session['converted']:
        flash("请先完成Excel转Word转换！", "error")
        return render_template('excel2word.html', excel_uploaded=True, converted=session.get('converted'))

    try:
        excel_path = session['excel_path']
        word_path = session['word_path']
        verify_result, module_stats = verify_consistency(excel_path, word_path)
        session['verify_result'] = verify_result
        session['module_stats'] = module_stats
        if verify_result:
            flash("内容校验通过！Excel与Word内容一致", "success")
        else:
            flash("内容校验失败！Excel与Word内容不一致", "warning")
    except Exception as e:
        flash(f"校验失败：{str(e)}", "error")
    return render_template('excel2word.html',
                           excel_uploaded=True,
                           converted=True,
                           verify_result=session.get('verify_result'),
                           module_stats=session.get('module_stats'))


@excel2word_bp.route('/download/word')
def download_word():
    """下载生成的Word文档"""
    if 'word_path' not in session and os.path.exists(session['word_path']):
        flash("无可用的Word文件！", "error")
        return render_template('excel2word.html', excel_uploaded=True, converted=session.get('converted'))

    return send_file(
        session['word_path'],
        as_attachment=True,
        download_name=f"转换结果_{time.strftime('%Y%m%d%H%M%S')}.docx"
    )


@excel2word_bp.route('/download/stats')
def download_stats():
    """下载模块统计Excel"""
    if 'module_stats' not in session or not session['module_stats']:
        flash("无可用的统计数据！", "error")
        return render_template('excel2word.html', excel_uploaded=True, converted=True)

    import pandas as pd
    stats_path = Path(current_app.config['UPLOAD_FOLDER']) / f"统计数据_{time.strftime('%Y%m%d%H%M%S')}.xlsx"
    pd.DataFrame(session['module_stats']).to_excel(stats_path, index=False)
    return send_file(
        stats_path,
        as_attachment=True,
        download_name=f"模块统计_{time.strftime('%Y%m%d%H%M%S')}.xlsx"
    )
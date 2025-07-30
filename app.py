#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇报评分投票系统后端API
基于Flask框架，使用MySQL数据库
"""

from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')  # 生产环境请设置环境变量
CORS(app)

# 数据库配置 - 支持环境变量
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'voting_system'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': True
}

@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

def init_database():
    """初始化数据库"""
    try:
        # 首先创建数据库（如果不存在）
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)  # 移除database参数
        
        with mysql.connector.connect(**temp_config) as connection:
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS voting_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库创建成功")
        
        # 然后连接到数据库并创建表
        with get_db_connection() as connection:
            cursor = connection.cursor()
            
            # 创建reports表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL COMMENT '汇报标题',
                    description TEXT COMMENT '汇报描述/内容',
                    creator VARCHAR(100) NOT NULL COMMENT '创建者姓名',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    status ENUM('active', 'closed') DEFAULT 'active' COMMENT '投票状态',
                    deadline DATETIME COMMENT '投票截止时间'
                )
            """)
            
            # 创建judges表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS judges (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE COMMENT '评委姓名',
                    email VARCHAR(255) COMMENT '邮箱',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建votes表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    report_id INT NOT NULL COMMENT '汇报项目ID',
                    judge_name VARCHAR(100) NOT NULL COMMENT '评委姓名',
                    score INT NOT NULL COMMENT '评分(-3到3)',
                    comment TEXT COMMENT '评价意见',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '投票时间',
                    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_vote (report_id, judge_name) COMMENT '同一评委对同一汇报只能投票一次'
                )
            """)
            
            # 插入示例评委数据（如果不存在）
            cursor.execute("""
                INSERT IGNORE INTO judges (name, email) VALUES 
                ('张三', 'zhangsan@company.com'),
                ('李四', 'lisi@company.com'),
                ('王五', 'wangwu@company.com'),
                ('赵六', 'zhaoliu@company.com')
            """)
            
            print("数据库表创建成功")
            
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        print("请检查MySQL服务是否启动，以及数据库配置是否正确")
        # 在生产环境中，我们不希望因为数据库连接失败而阻止应用启动
        return False
    return True

@app.route('/health')
def health_check():
    """健康检查端点"""
    return {'status': 'ok', 'message': '应用正常运行'}, 200

@app.route('/')
def index():
    """首页 - 显示所有汇报项目"""
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, title, description, creator, created_at, status,
                       (SELECT COUNT(*) FROM votes WHERE report_id = reports.id) as vote_count
                FROM reports 
                ORDER BY created_at DESC
            """)
            reports = cursor.fetchall()
            return render_template('index.html', reports=reports)
    except Exception as e:
        flash(f'获取汇报列表失败: {e}', 'error')
        return render_template('index.html', reports=[])

@app.route('/create', methods=['GET', 'POST'])
def create_report():
    """创建新的汇报投票"""
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            creator = request.form['creator']
            deadline_str = request.form.get('deadline')
            
            deadline = None
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            
            with get_db_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO reports (title, description, creator, deadline)
                    VALUES (%s, %s, %s, %s)
                """, (title, description, creator, deadline))
                
                report_id = cursor.lastrowid
                flash('汇报投票创建成功！', 'success')
                return redirect(url_for('report_detail', report_id=report_id))
                
        except Exception as e:
            flash(f'创建失败: {e}', 'error')
    
    return render_template('create_report.html')

@app.route('/report/<int:report_id>')
def report_detail(report_id):
    """查看汇报详情和投票结果"""
    judge_name = request.args.get('judge_name', '')  # 从URL参数获取评委姓名
    creator_name = request.args.get('creator', '')   # 从URL参数获取创建者姓名
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # 获取汇报基本信息
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            report = cursor.fetchone()
            
            if not report:
                flash('汇报不存在', 'error')
                return redirect(url_for('index'))
            
            # 权限控制逻辑
            is_creator = creator_name and creator_name == report['creator']
            is_personal_view = bool(judge_name and not is_creator)
            is_admin_view = is_creator
            
            if judge_name and not is_creator:
                # 个人视图：评委只能看到自己的投票
                cursor.execute("""
                    SELECT judge_name, score, comment, created_at 
                    FROM votes 
                    WHERE report_id = %s AND judge_name = %s
                    ORDER BY created_at DESC
                """, (report_id, judge_name))
                votes = cursor.fetchall()
            elif is_creator:
                # 创建者视图：可以看到所有投票详情
                cursor.execute("""
                    SELECT judge_name, score, comment, created_at 
                    FROM votes 
                    WHERE report_id = %s 
                    ORDER BY created_at DESC
                """, (report_id,))
                votes = cursor.fetchall()
            else:
                # 默认视图：只显示统计信息，不显示具体投票详情
                votes = []
                is_personal_view = False
                is_admin_view = False
            
            # 获取总体统计信息（始终显示）
            cursor.execute("""
                SELECT COUNT(*) as vote_count, AVG(score) as avg_score
                FROM votes 
                WHERE report_id = %s
            """, (report_id,))
            stats_data = cursor.fetchone()
            
            if stats_data and stats_data['vote_count'] > 0:
                avg_score = float(stats_data['avg_score'])
                total_score = avg_score + 5  # 基础分5分
                vote_count = stats_data['vote_count']
            else:
                avg_score = 0
                total_score = 5
                vote_count = 0
            
            stats = {
                'vote_count': vote_count,
                'avg_score': round(avg_score, 2),
                'total_score': round(total_score, 2)
            }
            
            return render_template('report_detail.html', 
                                 report=report, votes=votes, stats=stats, 
                                 is_personal_view=is_personal_view, 
                                 is_admin_view=is_admin_view,
                                 current_judge=judge_name,
                                 is_creator=is_creator)
    except Exception as e:
        flash(f'获取汇报详情失败: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/vote/<int:report_id>', methods=['GET', 'POST'])
def vote(report_id):
    """评委投票页面"""
    if request.method == 'POST':
        try:
            judge_name = request.form['judge_name'].strip()
            score = int(request.form['score'])
            comment = request.form.get('comment', '').strip()
            
            # 验证评分范围
            if score < -3 or score > 3:
                flash('评分必须在-3到3之间', 'error')
                return redirect(url_for('vote', report_id=report_id))
            
            # 验证评委姓名
            if not judge_name:
                flash('请输入评委姓名', 'error')
                return redirect(url_for('vote', report_id=report_id))
            
            with get_db_connection() as connection:
                cursor = connection.cursor()
                
                # 检查是否已经投票
                cursor.execute("""
                    SELECT id FROM votes 
                    WHERE report_id = %s AND judge_name = %s
                """, (report_id, judge_name))
                
                if cursor.fetchone():
                    flash('您已经对此汇报投过票了', 'error')
                    return redirect(url_for('vote', report_id=report_id))
                
                # 插入投票记录
                cursor.execute("""
                    INSERT INTO votes (report_id, judge_name, score, comment)
                    VALUES (%s, %s, %s, %s)
                """, (report_id, judge_name, score, comment))
                
                flash('投票成功！', 'success')
                # 投票成功后，重定向到个人视图，只显示自己的投票
                return redirect(url_for('report_detail', report_id=report_id, judge_name=judge_name))
                
        except ValueError:
            flash('评分必须是数字', 'error')
        except Exception as e:
            flash(f'投票失败: {e}', 'error')
    
    # GET请求，显示投票表单
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            report = cursor.fetchone()
            
            if not report:
                flash('汇报不存在', 'error')
                return redirect(url_for('index'))
            
            if report['status'] == 'closed':
                flash('此汇报投票已关闭', 'error')
                return redirect(url_for('report_detail', report_id=report_id))
            
            return render_template('vote.html', report=report)
    except Exception as e:
        flash(f'获取汇报信息失败: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/api/reports/<int:report_id>/close', methods=['POST'])
def close_report(report_id):
    """关闭汇报投票"""
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE reports SET status = 'closed' WHERE id = %s
            """, (report_id,))
            
            return jsonify({'success': True, 'message': '投票已关闭'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'关闭失败: {e}'}), 500

@app.route('/creator_login/<int:report_id>', methods=['GET', 'POST'])
def creator_login(report_id):
    """创建者身份验证"""
    if request.method == 'POST':
        creator_name = request.form.get('creator_name', '').strip()
        
        try:
            with get_db_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
                report = cursor.fetchone()
                
                if not report:
                    flash('汇报不存在', 'error')
                    return redirect(url_for('index'))
                
                if creator_name == report['creator']:
                    # 验证成功，重定向到管理员视图
                    return redirect(url_for('report_detail', report_id=report_id, creator=creator_name))
                else:
                    flash('创建者姓名验证失败，请确认您是该汇报的创建者', 'error')
                    
        except Exception as e:
            flash(f'验证失败: {e}', 'error')
    
    # 获取汇报信息用于显示
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            report = cursor.fetchone()
            
            if not report:
                flash('汇报不存在', 'error')
                return redirect(url_for('index'))
                
            return render_template('creator_login.html', report=report)
    except Exception as e:
        flash(f'获取汇报信息失败: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/check_vote', methods=['GET', 'POST'])
def check_vote():
    """查询个人投票记录"""
    if request.method == 'POST':
        judge_name = request.form.get('judge_name', '').strip()
        if not judge_name:
            flash('请输入评委姓名', 'error')
            return render_template('check_vote.html')
        
        try:
            with get_db_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                # 获取该评委的所有投票记录
                cursor.execute("""
                    SELECT v.*, r.title, r.creator, r.created_at as report_created_at
                    FROM votes v
                    JOIN reports r ON v.report_id = r.id
                    WHERE v.judge_name = %s
                    ORDER BY v.created_at DESC
                """, (judge_name,))
                
                votes = cursor.fetchall()
                
                if votes:
                    return render_template('check_vote.html', votes=votes, judge_name=judge_name)
                else:
                    flash(f'没有找到评委"{judge_name}"的投票记录', 'info')
                    return render_template('check_vote.html')
                    
        except Exception as e:
            flash(f'查询失败: {e}', 'error')
            return render_template('check_vote.html')
    
    return render_template('check_vote.html')

@app.route('/api/reports/<int:report_id>/results')
def get_results(report_id):
    """获取汇报投票结果API"""
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # 获取汇报信息和统计结果
            cursor.execute("""
                SELECT r.*, 
                       COUNT(v.id) as vote_count,
                       COALESCE(AVG(v.score), 0) as avg_score,
                       COALESCE(AVG(v.score), 0) + 5 as total_score
                FROM reports r
                LEFT JOIN votes v ON r.id = v.report_id
                WHERE r.id = %s
                GROUP BY r.id
            """, (report_id,))
            
            result = cursor.fetchone()
            if result:
                result['avg_score'] = round(result['avg_score'], 2)
                result['total_score'] = round(result['total_score'], 2)
            
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'获取结果失败: {e}'}), 500

if __name__ == '__main__':
    # 尝试初始化数据库，但不让失败阻止应用启动
    try:
        db_initialized = init_database()
        if not db_initialized:
            print("警告：数据库初始化失败，应用将在有限功能模式下运行")
    except Exception as e:
        print(f"数据库初始化遇到异常: {e}")
        print("应用将在有限功能模式下运行")
    
    # 启动应用 - 支持环境变量配置
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', '5000'))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"启动应用在 {host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)